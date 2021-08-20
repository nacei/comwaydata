#!/usr/bin/python
# -*- coding:UTF-8 -*-
# use comway map to com port and read the data from com,
# 发送数据至南京房屋安全鉴定平台 server http://218.94.87.201:8093/sms/api/monitoringDeviceInterface/save
# python 3.x
# programer: hanxiaojian
# 2021.6
# 钜力安如村设备串口采集并传输到鉴定处服务器
import serial
import json
import time
import requests


def http_post(postdata):
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
    }
    url = "http://218.94.87.201:8093/sms/api/monitoringDeviceInterface/save"  # sent to南京鉴定处平台
    syskey='GoiXPz61kepEHx7d75usZmypE27hq1dVOM6GrlBmpADK9943r4IpmQHjxX9V=='
    res = requests.post(url, data=json.dumps(postdata), headers=headers).text
    return res


def readserial(c):
    com = 'com' + str(c)
    ser = serial.Serial(com, 115200, timeout=0.5)
    if not ser.isOpen():
        ser.open()
    print('waiting data...武汉bitian设备')
    while True:
        time.sleep(1)
        if ser.inWaiting() > 0:  # 缓存中有数据
            s = ser.readline()
            hexstr = s.hex()
            # startposition = hexstr.find('aa')
            # endposition = hexstr.rfind('bb')
            # data = hexstr[startposition:endposition + 2]  # 原始数据
            # return data
            return hexstr
        else:
            continue
    ser.close()


# 定义传感器类别字典
Sensor_Types = {'01': '裂缝', '02': '单轴倾斜', '19': 'kp静力水准仪', '04': '双轴倾斜带温度', '05': '应变', '06': '温湿度', '26': '激光静力水准仪',
                '31': 'bt静力水准仪'}

def getdata(data):
    # 计算机本地时间
    saveTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))  # 入库savetime
    print(saveTime)
    # 解析数据
    data = data[6:]
    # acqtime = "20" + data[0:2] + "-" + data[2:4] + "-" + data[4:6] + " " + data[6:8] + ":" + data[8:10] + ":" + data[10:12]  # 采集仪日期
    data = data[12:]
    acqId = data[0:4]  # 采集仪编号 入库
    print(acqId)
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
        Sensor_T = Sensor_Types[st]
        # print(Sensor_T)
        dai = []
        tp = ['x', 'y', 't', 'err']
        unit = ['deg', 'deg', 'C', '']
        if st == "04":  # 双向倾斜带T
            for i in range(0, 3):  # 有x,y,t 3组数据
                if int(data[4:6]) == 0:
                    dataX = float(data[6:8] + data[8:10] + data[10:12]) / 10000
                elif int(data[4:6]) == 1:
                    dataX = -float(data[6:8] + data[8:10] + data[10:12]) / 10000
                else:
                    dataX = -1
                dic = {"type": tp[i], "data": dataX, "unit": unit[i]}
                dai.append(dic)
                data = data[8:]
            data = data[4:]
            # print(dai)
        elif st == '31':
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
        da = {"sensorID": sn, "type": st, "factory": "czbt", "data": dai}
        # print(da)
        jds.append(da)
    dataout = {"acqId": acqId, "acqFactory": "czbt", "acqType": "BT-16", "acqCode": 0, "recTime": saveTime,
               "memo": "", "jData": jds}
    print(dataout)
    return dataout


t = 0
while t < 2:
    time.sleep(2)
    try:
        # 采集数据
        comport = 2  # com
        data = readserial(comport).upper()
        # print(data)
        datalist=data.split('BB')
        # print(datalist)
        for each in datalist:
            if each=="": continue
            print(each,'\n')
            dataout=getdata(each)
            # data = json.dumps(dataout, ensure_ascii=False)  # 转json格式
            print (dataout)
            bk = http_post(dataout)
            # print(bk)
    except Exception as err:
        print("there is err.", err)
        continue

