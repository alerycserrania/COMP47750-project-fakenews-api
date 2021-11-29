
import codecs
import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.datastructures import UploadFile
from fastapi.params import Body, File

from hadoop_runner import fit_and_predict, predict, get_stats

app = FastAPI()

origins = [
    os.environ["FASTAPI_FRONT_URL"],
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/fit_and_predict")
def run_fit_and_predict(
    data: UploadFile = File(...),
    training_proportion: float = Body(...)
):
    return fit_and_predict(
        codecs.iterdecode(data.file,'utf-8'), 
        training_proportion
    )

@app.post("/predict")
def run_predict(
    idx: str = Body(...),
    tests: List[str] = Body(...)
):
    return predict(idx, tests)

@app.get("/stats/{idx}")
def stats_from_idx(idx: str):
    return get_stats(idx)