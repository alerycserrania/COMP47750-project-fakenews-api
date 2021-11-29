from typing import IO, List
import uuid
import csv
import random
import os
import json
from hdfs import InsecureClient
from sqlalchemy import text
import math

from db import SessionLocal

def fit_and_predict(data: IO, training_proportion: float):
    idx = uuid.uuid4().hex
    client = InsecureClient(os.environ['FASTAPI_HADOOP_WEB_URL'])

    # first step: split data into training/test
    trainings, tests = split_data(data, training_proportion)

    try:
        with client.write(f'{idx}/training_data.csv', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator='\n')
            for line in trainings:
                writer.writerow(line)

        with client.write(f'{idx}/test_data.csv', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator='\n')
            for line in tests:
                writer.writerow(line)
        
        # wordcount step: count number of occurence of words in fake and real news
        os.system(f'mapred streaming -input {idx}/training_data.csv -output {idx}/wordcount '
                f'-mapper jobs/wordcount_mapper.py -reducer jobs/wordcount_reducer.py')
        os.system(f'hadoop fs -text {idx}/wordcount/* | hadoop fs -put - {idx}/wordcount.csv')

        # vocab count step: count number of words (features) in the dataset
        os.system(f'mapred streaming -input {idx}/wordcount -output {idx}/nb_words '
                f'-mapper jobs/vocab_reducer.py')
        os.system(f'hadoop fs -text {idx}/nb_words/* | hadoop fs -put - {idx}/nb_words.txt')

        # class priors step: calculate log of class priors
        os.system(f'mapred streaming -input {idx}/wordcount -output {idx}/class_priors '
                f'-mapper jobs/class_priors_mapper.py -reducer jobs/class_priors_reducer.py')
        os.system(f'hadoop fs -text {idx}/class_priors/* | hadoop fs -put - {idx}/class_priors.csv')
        
        # feature probas step: calculate log of feature probas
        os.system(f'mapred streaming -input {idx}/wordcount -output {idx}/feature_probas '
                f'-mapper "jobs/feature_probas_reducer.py {idx}"')
        os.system(f'hadoop fs -text {idx}/feature_probas/* | hadoop fs -put - {idx}/feature_probas.csv')
        
        # run tests step: predict and create result file
        os.system(f'mapred streaming -input {idx}/test_data.csv -output {idx}/test_result '
                f'-mapper "jobs/predict_mapper.py {idx}" -reducer "jobs/predict_reducer.py {idx}"')
        os.system(f'hadoop fs -text {idx}/test_result/* | hadoop fs -put - {idx}/test_result.csv')


        stats = generate_stats(idx, client)
        store_model(idx, client, stats)
    finally:
        client.delete(f'{idx}/', recursive=True)

    return stats


def predict(idx: str, tests: List[str]):
    client = InsecureClient(os.environ['FASTAPI_HADOOP_WEB_URL'])

    try:
        stats = load_model(idx, client)

        with client.write(f'{idx}/test_data.csv', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator='\n')
            for line in tests:
                writer.writerow(['', '', '', '', '', '', line])

        os.system(f'mapred streaming -input {idx}/test_data.csv -output {idx}/test_result '
                f'-mapper "jobs/predict_mapper.py {idx}" -reducer "jobs/predict_reducer.py {idx}"')
        os.system(f'hadoop fs -text {idx}/test_result/* | hadoop fs -put - {idx}/test_result.csv')
        
        with client.read(f'{idx}/test_result.csv', encoding='utf-8') as f:
            test_result = list(csv.reader(f, quoting=csv.QUOTE_MINIMAL))
    finally:
        client.delete(f'{idx}/', recursive=True)

    print(test_result)
    return [
        {'no': int(line[0]), 'result': line[1], 'proba': log_likel_to_proba(float(line[2]), float(line[3]), line[1])}
        for line in test_result
    ]

def logsumexp(p_real: float, p_fake: float):
    c = max(p_real, p_fake)
    return c + math.log(math.exp(p_real - c) + math.exp(p_fake - c))

def log_likel_to_proba(p_real: float, p_fake: float, result: str):
    if result == 'r':
        return math.exp(p_real - logsumexp(p_real, p_fake))
    elif result == 'f':
        return math.exp(p_fake - logsumexp(p_real, p_fake))

        
def store_model(idx: str, client: InsecureClient, stats: dict):
    with client.read(f'{idx}/class_priors.csv', encoding='utf-8') as f:
        reader = csv.reader(f, quoting=csv.QUOTE_MINIMAL)
        class_priors = [{
            'idx': idx,
            'cl': cl,
            'p_real': float(p_real),
            'p_fake': float(p_fake),
        } for cl, p_real, p_fake in reader]

    with client.read(f'{idx}/feature_probas.csv', encoding='utf-8') as f:
        reader = csv.reader(f, quoting=csv.QUOTE_MINIMAL)
        feature_probas = [{
            'idx': idx,
            'word': word,
            'p_real': float(p_real),
            'p_fake': float(p_fake),
        } for word, p_real, p_fake in reader]

    with SessionLocal() as db:
        db.execute(
            text("INSERT INTO class_priors (idx, cl, p_real, p_fake) VALUES(:idx, :cl, :p_real, :p_fake)"),
            class_priors
        )

        db.execute(
            text("INSERT INTO feature_probas (idx, word, p_real, p_fake) VALUES(:idx, :word, :p_real, :p_fake)"),
            feature_probas
        )

        db.execute(
            text("INSERT INTO stats (idx, stats) VALUES(:idx, :stats)"),
            {"idx": idx, "stats": json.dumps(stats)}
        )

        db.commit()


def get_stats(idx: str):
    with SessionLocal() as db:
        stats = db.execute(
            text('SELECT * FROM stats where idx=:idx'),
            {"idx": idx}
        ).fetchone()

    return json.loads(stats[1])

def load_model(idx: str, client: InsecureClient):
    with SessionLocal() as db:
        class_priors = db.execute(
            text('SELECT * FROM class_priors where idx=:idx'),
            {"idx": idx}
        ).fetchall()

        feature_probas = db.execute(
            text('SELECT * FROM feature_probas where idx=:idx'),
            {"idx": idx}
        ).fetchall()

        stats = db.execute(
            text('SELECT * FROM stats where idx=:idx'),
            {"idx": idx}
        ).fetchone()
    
    class_priors = [l[1:] for l in class_priors]
    feature_probas = [l[1:] for l in feature_probas]
    stats = json.loads(stats[1])

    with client.write(f'{idx}/class_priors.csv', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        for line in class_priors:
            writer.writerow(line)

    with client.write(f'{idx}/feature_probas.csv', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        for line in feature_probas:
            writer.writerow(line)
        
    return stats




def split_data(data: IO, training_proportion: float):
    lines = list(csv.reader(data, quoting=csv.QUOTE_ALL))
    random.shuffle(lines)
    delim = int(len(lines) * training_proportion)
    return lines[:delim], lines[delim:]


def confusion_matrix(idx: str, client: InsecureClient):
    with client.read(f'{idx}/test_result.csv', encoding='utf-8') as f:
        test_result = list(csv.reader(f, quoting=csv.QUOTE_MINIMAL))

    with client.read(f'{idx}/test_data.csv', encoding='utf-8') as f:
        test_data = list(csv.reader(f, quoting=csv.QUOTE_MINIMAL))

    tp, tn = 0, 0
    fp, fn = 0, 0
    for i in range(len(test_result)):
        idx = int(test_result[i][0])
        if test_result[i][1] == 'f' and test_data[idx][3] == 'f':
            tp += 1
        elif test_result[i][1] == 'r' and test_data[idx][3] == 'r':
            tn += 1
        elif test_result[i][1] == 'f' and test_data[idx][3] == 'r':
            fp += 1
        else:
            fn += 1

    return [[tn, fp], [fn, tp]]


def generate_stats(idx: str, client: InsecureClient):
    with client.read(f'{idx}/training_data.csv', encoding='utf-8') as f:
        articles = list(csv.reader(f, quoting=csv.QUOTE_ALL))
        nb_real_articles = sum(1 for l in articles if l[3] == 'r')
        nb_fake_articles = sum(1 for l in articles if l[3] == 'f')

    with client.read(f'{idx}/class_priors.csv', encoding='utf-8') as f:
        reader = csv.reader(f, quoting=csv.QUOTE_MINIMAL)
        for l in reader:
            if l[0] == 'r':
                nb_words_real_articles = int(l[1])
            if l[0] == 'f':
                nb_words_fake_articles = int(l[1])

    with client.read(f'{idx}/wordcount.csv', encoding='utf-8') as f:
        reader = list(csv.reader(f, quoting=csv.QUOTE_MINIMAL))
        real_words_sorted = [
            (word, int(count))
            for word, count, _ in sorted(reader, key=lambda l: int(l[1]), reverse=True)[:100]
        ]
        fake_words_sorted = [
            (word, int(count))
            for word, _, count in sorted(reader, key=lambda l: int(l[2]), reverse=True)[:100]
        ]
    
    with client.read(f'{idx}/test_result.csv', encoding='utf-8') as f:
        test_result = list(csv.reader(f, quoting=csv.QUOTE_MINIMAL))

    with client.read(f'{idx}/test_data.csv', encoding='utf-8') as f:
        test_data = list(csv.reader(f, quoting=csv.QUOTE_MINIMAL))

    tp, tn = 0, 0
    fp, fn = 0, 0
    for i in range(len(test_result)):
        id_line = int(test_result[i][0])
        if test_result[i][1] == 'f' and test_data[id_line][3] == 'f':
            tp += 1
        elif test_result[i][1] == 'r' and test_data[id_line][3] == 'r':
            tn += 1
        elif test_result[i][1] == 'f' and test_data[id_line][3] == 'r':
            fp += 1
        else:
            fn += 1

    return {
        "idx": idx,
        "nb_articles": {
            "real": nb_real_articles,
            "fake": nb_fake_articles,
        }, 
        "nb_words": {
            "real": nb_words_real_articles,
            "fake": nb_words_fake_articles,
        },
        "words_popularity_in_order": {
            "real": real_words_sorted,
            "fake": fake_words_sorted,
        },
        "confusion_matrix": [
            [tn, fp], 
            [fn, tp],
        ]
    }


if __name__ == '__main__':
    result = fit_and_predict(open('data.csv', 'r', encoding='utf-8'), 0.67)
    print(result)