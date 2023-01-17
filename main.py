import datetime
import json

from flask import Flask, make_response, request, jsonify
from Repository import DataBaseRepository as repository
from Classes import RequestFormatter
from Service import ItsPredictionService
from MlModel import TestML

app = Flask(__name__)

@app.route('/')
def hello_world():
    equipmentId="1_16"
    repository.findDefinitItsWithEquipmentMrid(equipmentId)
    return 'Hello World'

@app.route('/predict', methods=['POST'])
def postPredict():
    predictedMap=ItsPredictionService.predict(request)
    response=json.dumps(predictedMap)
    return response

@app.route('/train', methods=['POST'])
def postTrain():
    trained = TestML.training()
    return "модель обучена"


if __name__ == '__main__':
    app.run(port='8086')



