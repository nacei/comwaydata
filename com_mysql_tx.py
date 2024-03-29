#!/usr/bin/python
# -*- coding:UTF-8 -*-
# use comway map to com port and read the data from com,
# save to local database
# project：泰兴人民医院项目
# programer: hxj
# 2021.4

import serial
import json
import time
import requests
import pymysql


def connetDB():
    try:
        # 连接数据库
        conn = pymysql.connect(host='njgdsp.oicp.net', user='root', password='song', port=3306, db='comway',
                               charset='utf8')
        conn.autocommit(True)
        cur = conn.cursor()
        return (conn, cur)
    except:
        print('failue connect to db')
        return None


def colseDB(conn, cur):
    conn.close()
    cur.close()


# def insertDB(time,number,x1,y1,t1,x2,y2,t2,level,level2,level3):
def insertDB(acqId, acqFactory, acqType, acqcode, saveTime, recTime, jdata, memo):
    (db, cursor) = connetDB()
    # print(db,cursor)
    sql = 'INSERT INTO txhospital(acqID, acqFactory, acqType, acqCode, saveTime, recTime, jData ,memo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
    try:
        if cursor.execute(sql, (acqId, acqFactory, acqType, acqcode, saveTime, recTime, jdata, memo)):
            print('successful saved.')
            db.commit()
    except Exception as err:
        print('failed',err)
        db.rollback()
    # cursor.execute(sql)
    # db.comit()
    # print("data saved.")
    return


def readSerial(c):
    com = 'com' + str(c)
    ser = serial.Serial(com, 115200, timeout=0.5)
    if not ser.isOpen(): ser.open()
    print('waiting data...泰兴市人民医院检测楼')
    while True:
        time.sleep(1)
        if ser.inWaiting() > 0:  # 缓存中有数据
            s = ser.readline()
            hexstr = s.hex()
            return hexstr
        else:
            continue
    ser.close()

#解析数据
def btdata(data):
    # 定义传感器类别字典
    Sensor_Types = {'01': '裂缝', '32': '振弦应变计', '31': '静力水准仪', '04': '双轴倾斜带温度', '05': '应变', '19': '鲲鹏水准', '26': '激光静力水准仪'}
    # 计算机本地时间
    saveTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))  # 入库savetime
    print(saveTime)
    # 解析数据
    data = data[6:]
    # acqtime = "20" + data[0:2] + "-" + data[2:4] + "-" + data[4:6] + " " + data[6:8] + ":" + data[8:10] + ":" + data[10:12]  # 采集仪日期
    data = data[12:]
    acqId = data[0:4]  # 采集仪编号 入库
    # print(acqId)
    acqFactory = 'czbt'  # 厂家
    acqType = 'BT-16'  # 型号
    data = data[4:]
    Sensor_All = int(data[0:2])  # 传感器数量
    # print(Sensor_All)
    data = data[2:]
    jds = []
    for each in range(0, Sensor_All):
        sn = str(data[0:2])  # numID
        # print('sn', sn)
        st = str(data[2:4])  # type
        # Sensor_T = Sensor_Types[st]
        # print(Sensor_T)
        if st == "04":  # 双向倾斜带T
            dai = []
            tp = ['x', 'y', 't', 'err']
            unit = ['deg', 'deg', 'C', '']
            for i in range(0, 3):  # 有x,y,t 3组数据
                if int(data[4:6]) == 0:
                    dataX = float(data[6:8] + data[8:10] + data[10:12]) / 10000
                elif int(data[4:6]) == 1:
                    dataX = -float(data[6:8] + data[8:10] + data[10:12]) / 10000
                else:
                    dataX = -1
                dic = {"type": tp[i], "value": dataX, "unit": unit[i]}
                dai.append(dic)
                data = data[8:]
            data = data[4:]
            # print(dai)
        elif st == '31' : #比天静力水准，不待温度
            dai=[]
            tp = ['level', 'err']
            if int(data[4:6]) == 0:  # x
                dataX = float(data[6:8] + data[8:10] + data[10:12]) / 1000
            elif int(data[4:6]) == 1:
                dataX = -float(data[6:8] + data[8:10] + data[10:12]) / 1000
            else:
                dataX = -1
            dai = [{"type": tp[0], "value": dataX, "unit": "mm"}]
            # print(dai)
            data = data[12:]
        elif st=='32': #振弦应变计16ch
            # print(data)
            dai = []
            di=[]
            tp = ['x1', 'x2','x3','x4','x5','x6', 'x7','x8','x9','x10','x11', 'x12','x13','x14','x15','x16']
            for i in range(0,16):
                dataX = float(data[6:8] + data[8:10] + data[10:12]) / 100
                print(dataX)
                di.append(dataX)
                data=data[8:]
            # print(di)
            dic = dict(zip(tp, di))
            dai.append(dic)
            # print(dai)
            data = data[68:]
        da = {"sensorID": sn, "type": st, "factory": "czbt", "data": dai}
        # print(da)
        jds.append(da)
        jdss=json.dumps(jds)
    dataout = {"acqId": acqId, "acqFactory": "czbt", "acqType": "BT-16", "acqCode": 0, "recTime": saveTime, "jData": jdss,
               "memo":""}
    print(dataout)
    return dataout

#主程序
while True:
    time.sleep(1)
    # 采集数据
    comport = 7  # com 泰兴人民医院
    data = readSerial(comport)
    print(data)
    dataout = btdata(data)
    # data = json.dumps(dataout, ensure_ascii=False)  # 转json格式
    acqId = dataout['acqId']
    # print(acqId)
    acqFactory = dataout['acqFactory']
    # print(acqFactory)
    acqType = dataout['acqType']
    # print(acqType)
    acqcode = dataout['acqCode']
    # print(type(acqcode),acqcode)
    saveTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))  # 入库savetime
    # print(type(saveTime),saveTime)
    recTime = dataout['recTime']
    # print(type(recTime),recTime)
    jdata =str(dataout['jData'])
    # print(type(jdata),jdata)
    memo = dataout['memo']
    print(memo)
    insertDB(acqId, acqFactory, acqType, acqcode, saveTime, recTime, jdata, memo)
