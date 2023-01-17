def requestFormatForPrediction(request):
    try:
        equip = request.json['equip']
    except:
        equip=None
    try:
        isFirst = request.json['isfirst']
    except:
        isFirst=None
    try:
        endOfPrediction = request.json['endOfPrediction']
    except:
        endOfPrediction=None
    try:
        planNumber = request.json['planNumber']
    except:
        planNumber=None
    try:
        lastPlan = request.json['lastPlan']
    except:
        lastPlan=None
    try:
        saveToDb = request.json['saveToDb']
    except:
        saveToDb=None
    return equip, isFirst,endOfPrediction,planNumber, lastPlan, saveToDb