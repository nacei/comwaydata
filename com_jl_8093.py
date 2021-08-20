#!/usr/bin/python
# -*- coding:UTF-8 -*-
# use comway map to com port，then read data from com
# com read and save to mysql for 钜力项目 安如村 to 南京鉴定处平台
# python 3.x
# programer: hanxiaojian
# 2021.6
_author_ = 'hanxiaojian njtech'
import serial
import json
import time, configparser, os,sys,datetime
import pymysql
import requests


def http_post(postdata):
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
    }
    url = "http://218.94.87.201:8093/sms/api/monitoringDeviceInterface/save"  # sent to南京鉴定处平台
    # syskey = 'GoiXPz61kepEHx7d75usZmypE27hq1dVOM6GrlBmpADK9943r4IpmQHjxX9V=='
    postdata = {'syskey':'GoiXPz61kepEHx7d75usZmypE27hq1dVOM6GrlBmpADK9943r4IpmQHjxX9V==','data':postdata}
    res = requests.post(url, data=json.dumps(postdata), headers=headers).text
    print('return：',res)
    # if res['code']=='200':
    #     print('传输成功！')
    return res


def connetDB():
    try:
        # 连接数据库
        print('connect to:',host)
        conn = pymysql.connect(host=host, user=user, password=password, port=port, db=db, charset=charset)
        conn.autocommit(True)
        cur = conn.cursor()
        return (conn, cur)
    except Exception as err:
        print('failue connect to db', err)
        return None


def colseDB(conn, cur):
    conn.close()
    cur.close()


def insertDB(devId, projectId, devFactory, devType, saveTime, jdata):
    (db, cursor) = connetDB()
    # print(type(devId),type(projectId),type(devFactory),type(devType),type(saveTime),type(jdata))
    sql = "INSERT INTO rawdata (ProjectId,devId,devFactory,devType,saveTime,jData) VALUES (%s,%s,%s,%s,%s,%s);"
    try:
        # sen = cursor.mogrify(sql)  # 相比上面的错误代码，这里给姓名对应的占位符加上了引号
        # print(sen)
        if cursor.execute(sql, (projectId, devId, devFactory, devType, saveTime, jdata)):
            print('successful saved.')
            db.commit()
    except:
        print('failed')
        db.rollback()
    # cursor.execute(sql)
    # db.comit()
    return


def readSerial(c):
    com = 'com' + str(c)
    ser = serial.Serial(com, 115200, timeout=0.5)
    if not ser.isOpen(): ser.open()
    print('waiting data...com:', c)
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


def main():
    global proId
    while True:
        time.sleep(1)
        try:
            # 采集数据
            data = readSerial(com)
            # print(data)
            # 计算机本地时间
            insertTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))  # 入库savetime
            print('接收时间：', insertTime, type(insertTime))
            # 解析数据
            data = data[6:]
            # acqtime = "20" + data[0:2] + "-" + data[2:4] + "-" + data[4:6] + " " + data[6:8] + ":" + data[8:10] + ":" + data[10:12]  # 采集仪日期
            data = data[12:]
            devId = data[0:4]  # 采集仪编号 入库
            print('采集仪编号：', int(devId, 16))
            if devId == '0101':
                proId = '安如村25号'
            elif devId == '003d':
                proId = '舸舫园'
            devFactory = '常州比天智能科技有限公司'  # 入库
            devType = 'BT-16'  # 入库
            data = data[4:]
            Sensor_All = int(data[0:2])  # 传感器数量
            data = data[2:]
            dataout = []
            klist04 = ['ch', 'type', 'datax', 'datay', 'temp']
            klist26 = ['ch', 'type', 'data']
            # print(data)
            for each in range(0, Sensor_All):
                da = []
                sn = str(data[0:2])  # numID
                st = str(data[2:4])  # type
                # print(sn, st, type(st))
                Sensor_T = Sensor_Types[st]
                da.append(sn)
                da.append(Sensor_T)
                if st == "04":
                    # print('接受了一个倾角传感器数据')
                    for i in range(0, 3):  # 有x,y,t 3组数据
                        if int(data[4:6]) == 0:
                            dataX = float(data[6:8] + data[8:10] + data[10:12]) / 10000
                        elif int(data[4:6]) == 1:
                            dataX = -float(data[6:8] + data[8:10] + data[10:12]) / 10000
                        else:
                            dataX = -1
                        da.append(dataX)
                        data = data[8:]
                    data = data[4:]
                    eachdata = dict(zip(klist04, da))
                    dataout.append(eachdata)
                elif st == '31':
                    # print('接受了一个位移传感器数据')
                    if int(data[4:6]) == 0:
                        dataX = float(data[6:8] + data[8:10] + data[10:12]) / 10000
                    elif int(data[4:6]) == 1:
                        dataX = -float(data[6:8] + data[8:10] + data[10:12]) / 10000
                    else:
                        dataX = -1
                    da.append(dataX)
                    data = data[12:]
                    eachdata = dict(zip(klist26, da))
                    dataout.append(eachdata)
                elif st == '26':
                    # print('接受了一个Laser传感器数据')
                    if int(data[4:6]) == 0:
                        dataX = float(data[6:8] + data[8:10] + data[10:12]) / 1000
                    elif int(data[4:6]) == 1:
                        dataX = -float(data[6:8] + data[8:10] + data[10:12]) / 1000
                    else:
                        dataX = -1
                    da.append(dataX)
                    data = data[20:]
                    eachdata = dict(zip(klist26, da))
                    dataout.append(eachdata)
            # print(dataout)
            jdata = json.dumps(dataout, ensure_ascii=False)  # 入库 jdata
            print('入库数据:', jdata)
            insertDB(devId, proId, devFactory, devType, insertTime, jdata)
            # post to api server
            dataout={'ProjectId':proId,'saveTime':insertTime,'devId':devId,'jData':jdata,'devFactory':devFactory,'devType':devType,'acqTime':None}
            print('dataout=', dataout, 'type=',type(dataout))
            bk = http_post(dataout)
            # print(bk)
        except Exception as err:
            print('错误代码', err)
        continue


# 定义传感器类别字典
Sensor_Types = {'01': '裂缝', '02': '单轴倾斜', '31': '静力水准仪', '04': '双轴倾斜带温度', '05': '应变', '06': '温湿度', '26': '激光静力水准'}
# read config.ini file.
cf = configparser.ConfigParser()
curpath = os.getcwd()
print('current:',curpath)
cf.read(curpath + '\config.ini', encoding='utf-8')
com = cf.get("ComPort", "com")
host = cf.get("MySQL-DB", "host")
user = cf.get("MySQL-DB", "user")
password = cf.get("MySQL-DB", "password")
port = int(cf.get("MySQL-DB", "port"))
db = cf.get("MySQL-DB", "db")
charset = cf.get("MySQL-DB", "charset")


if __name__ == '__main__':
    main()
