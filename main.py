
import codecs

from fastapi import FastAPI
from fastapi.datastructures import UploadFile
from fastapi.params import Body, File

from hadoop_runner import fit_and_predict

app = FastAPI()


@app.post("/fit_and_predict")
def run_fit_and_predict(
    data: UploadFile = File(...),
    training_proportion: float = Body(...)
):
    return fit_and_predict(
        codecs.iterdecode(data.file,'utf-8'), 
        training_proportion
    )