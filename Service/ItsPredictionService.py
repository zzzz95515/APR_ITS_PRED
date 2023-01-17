from Repository import DataBaseRepository
from Classes import RequestFormatter
from MlModel import mlModel as ml
import datetime
import random as r


def predict(request):
    global list_date
    equip, isFirst, endOfPrediction, planNumber, lastPlan, saveToDb = RequestFormatter.requestFormatForPrediction(
        request)
    dict_eq = {}

    for each in equip:
        fixDatesList = []
        deltaList = []
        print(each.get('equip_id'))
        if each.get('fixDate') != None:
            fixDates = each.get('fixDate')
            deltaList = each.get('delta')
            for fixdate in fixDates:
                fixDatesList.append(datetime.datetime.strptime(fixdate, "%d/%m/%y"))

        if lastPlan == None:
            try:
                dataToPredict = DataBaseRepository.findDefinitItsWithEquipmentMrid(each.get('equip_id'))
                firstDate = DataBaseRepository.findLastDefiniteDate(each.get('equip_id'))[0]
                firstDate = firstDate + datetime.timedelta(1)
            except:
                print("оборудование " + each.get('equip_id') + "не найдено или отсутствуют данные для расчета")
                continue

        else:
            try:
                dataToPredict = DataBaseRepository.findPredictedItsWithEquipmentAndPlan(each.get('equip_id'), lastPlan)
                firstDate = DataBaseRepository.findFirstPredictedDateWithEquipmentAndPlan(each.get('equip_id'),
                                                                                          lastPlan)
            except:
                print("оборудование " + each.get('equip_id') + "не найдено или отсутствуют данные для расчета")
                continue
        lastIts = dataToPredict[len(dataToPredict) - 1][0]
        itsList = ml.predictIts(lastIts)
        itsList = tupleToList(itsList)
        itsList = prediction(itsList, lastIts)

        dict_each, list_its, list_date, list_equip_id = postprocessing(each, itsList, firstDate, fixDatesList,
                                                                       deltaList, endOfPrediction)
        dict_eq.update(dict_each)
    if saveToDb == 1:
        savePredictedItsToDb(list_equip_id, list_its, list_date, planNumber)
    return dict_eq


def postprocessing(each, itsList, firstDate, fixDatesList, delta, endOfPrediction):
    list_its = []
    list_date = []
    list_equip_id = []
    map = {}
    n = 0
    for i in range(len(itsList)):
        predictedDate = firstDate + datetime.timedelta(i)
        if n < len(fixDatesList):
            if fixDatesList[n].date() == predictedDate:
                for j in range(i, len(itsList)):
                    itsList[j] = itsList[j] + delta[n]
                    if itsList[j] > 100:
                        itsList[j] = 100
                        itsList[j - 1] = 100
                n += 1
        mapi = {str(predictedDate): itsList[i]}
        map.update(mapi)
        list_equip_id.append(each.get('equip_id'))
        list_its.append(itsList[i])
        list_date.append(predictedDate)
        if predictedDate == endOfPrediction:
            break
    dict_each = {each.get('equip_id'): map}
    return dict_each, list_its, list_date, list_equip_id


def prediction(its_predict, lastIts):
    first = its_predict[0]
    delta = first * 100 - lastIts
    for i in range(len(its_predict)):
        its_predict[i] = its_predict[i] * 100 - delta
    return its_predict


def tupleToList(tuple):
    resultList = []
    for i in tuple:
        resultList.append(i[0])
    return resultList


def savePredictedItsToDb(listDate, list_eqiup_id, lrsi_its, planNumber):
    DataBaseRepository.saveToPredictedItsMeas(listDate, list_eqiup_id, lrsi_its, planNumber);


def linearPrediction(request):
    equip, isFirst, endOfPrediction, planNumber, lastPlan, saveToDb = RequestFormatter.requestFormatForPrediction(
        request)
    dict_full = {}
    dateslist = []
    itsslist = []
    listEquip = []

    for each in equip:
        fixDatesList = []
        deltaList = []
        print(each.get('equip_id'))
        if each.get('fixDate') != None:
            fixDates = each.get('fixDate')
            deltaList = each.get('delta')
            for fixdate in fixDates:
                fixDatesList.append(datetime.datetime.strptime(fixdate, "%d/%m/%y"))

        if lastPlan == None:
            try:
                dataToPredict = DataBaseRepository.findDefinitItsWithEquipmentMrid(each.get('equip_id'))
                firstDate = DataBaseRepository.findLastDefiniteDate(each.get('equip_id'))[0]
                firstDate = firstDate + datetime.timedelta(1)
            except:
                print("оборудование " + each.get('equip_id') + "не найдено или отсутствуют данные для расчета")
                continue

        else:
            try:
                dataToPredict = DataBaseRepository.findPredictedItsWithEquipmentAndPlan(each.get('equip_id'),
                                                                                        lastPlan)
                firstDate = DataBaseRepository.findFirstPredictedDateWithEquipmentAndPlan(each.get('equip_id'),
                                                                                          lastPlan)
            except:
                print("оборудование " + each.get('equip_id') + "не найдено или отсутствуют данные для расчета")
                continue
        realIts = DataBaseRepository.findDefinitItsWithEquipmentMridAndDateBefore(each.get('equip_id'),
                                                                                  each.get(('fixDate')))
        lastPerioud = [realIts[len(realIts) - 1]]
        for i in range(len(realIts) - 2, 0, -1):
            if (realIts[i] > realIts[i + 1]):
                lastPerioud.append(realIts[i])
            else:
                break
        dif = (lastPerioud[0] - lastPerioud[len(lastPerioud) - 1]) / len(lastPerioud)
        its = dataToPredict[len(dataToPredict) - 1]
        k = 50
        ddiff = k * dif
        map_eq = {}
        predictionSize = (firstDate - endOfPrediction).days
        predictedDate = firstDate
        for i in range(predictionSize):
            k -= 1
            if k == 0:
                its = its - ddiff
                k = r.randint(80, 140)
                ddiff = k * dif
            predictedDate = predictedDate + datetime.timedelta(1)
            for j in range(len(fixDatesList)):
                if fixDatesList == predictedDate:
                    its += deltaList[j]
            mapi = {str(predictedDate): its}
            dateslist.append(predictedDate)
            itsslist.append(its)
            listEquip.append(each.get('equip_id'))
        map_eq.update(mapi)
        dict_map = {each.get('equip_id'): map_eq}
    dict_full.update(dict_map)
    if saveToDb == 1:
        savePredictedItsToDb(dateslist, listEquip, itsslist, planNumber)
    return dict_full
