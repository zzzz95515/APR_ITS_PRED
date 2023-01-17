import psycopg2


def connectToDb():
    con = psycopg2.connect(
        database="APR",
        user="postgres",
        password="123",
        host="127.0.0.1",
        port="5432")
    print("Database opened successfully")
    print(con)
    return con


def findDefinitItsWithEquipmentMrid(equipmentMrid):
    con = connectToDb()
    cur = con.cursor()
    cur.execute(
        "select its from  library.its_measurements_postgres_version where library.its_measurements_postgres_version.equipment_id = '" + equipmentMrid + "' Order by library.its_measurements_postgres_version.measurment_date asc")
    rows = cur.fetchall()
    con.close()
    return rows

def findDefinitItsWithEquipmentMridAndDateBefore(equipmentMrid, date):
    con = connectToDb()
    cur = con.cursor()
    cur.execute(
        "select its from  library.its_measurements_postgres_version where library.its_measurements_postgres_version.equipment_id = '" + equipmentMrid + "' And measurement_date <'"+ date+"' Order by library.its_measurements_postgres_version.measurment_date asc")
    rows = cur.fetchall()
    con.close()
    return rows


def findLastDefiniteDate(equipmentMrid):
    con = connectToDb()
    cur = con.cursor()
    cur.execute(
        "select its_measurements_postgres_version.measurment_date from  library.its_measurements_postgres_version where library.its_measurements_postgres_version.equipment_id = '" + equipmentMrid + "' Order by library.its_measurements_postgres_version.measurment_date desc Limit 1")
    rows = cur.fetchone()
    con.close()
    return rows


def findPredictedItsWithEquipmentAndPlan(equipmentMrid, planNumber):
    con = connectToDb()
    cur = con.cursor()
    cur.execute(
        "select predicted_its_meas.its from  library.predicted_its_meas where library.predicted_its_meas.equipment_mrid = '" + equipmentMrid + "' And plan_number = " + planNumber + "  Order by library.predicted_its_meas.pred_date asc")
    rows = cur.fetchall()
    con.close()
    return rows


def findFirstPredictedDateWithEquipmentAndPlan(equipmentMrid, planNumber):
    con = connectToDb()
    cur = con.cursor()
    cur.execute(
        "select predicted_its_meas.pred_date from  library.predicted_its_meas where library.predicted_its_meas.equipment_mrid = '" + equipmentMrid + "' And plan_number = " + planNumber + " Order by library.predicted_its_meas.pred_date asc Limit 1")
    rows = cur.fetchone()
    con.close()
    return rows


def findPredictedItsObraz():
    con = connectToDb()
    cur = con.cursor()
    cur.execute("select its from library.predicted_its")
    rows = cur.fetchall()
    con.close()
    return rows


def saveToPredictedItsMeas(dateList, equip_id_list, itsList, planNumber):
    con = connectToDb()
    cur = con.cursor()
    cur.execute("Select id from  library.predicted_its_meas Order by library.predicted_its_meas.id Desc limit 1")
    id = cur.fetchone()[0]
    for i in range(len(dateList)):
        id += 1
        cur.execute(
            "insert into  library.predicted_its_meas (id,pred_date,its,equipment_mrid,plan_number) values (" + str(
                id) + ",'" + str(dateList[i]) + "'," + str(itsList[i]) + ",'" + str(equip_id_list[i]) + "'," + str(
                planNumber) + ")")
    con.commit()
    con.close()


def saveToPredictedItsObraz(itsList):
    con = connectToDb()
    cur = con.cursor()
    cur.execute("Delete from library.predicted_its")
    con.commit()
    for i in range(len(itsList)):
        cur.execute(
            "insert into  library.predicted_its (its) values (" + str(itsList[i][0]) + ")")
    con.commit()
    con.close()
