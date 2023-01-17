from Repository import  DataBaseRepository
def predictIts(dataToPredict):
    predictedIts = DataBaseRepository.findPredictedItsObraz()
    return  predictedIts