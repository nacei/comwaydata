import os,configparser

cf = configparser.ConfigParser()
curpath =os.getcwd()
cf.read(curpath+'\config.ini',encoding='utf8')
secs = cf.sections()
print(1,secs)
options = cf.options("MySQL-DB")
print(options)
items = cf.items("MySQL-DB")
print(items)
com = cf.get("ComPort","com")
print(com)
host = cf.get("MySQL-DB","host")
user = cf.get("MySQL-DB","user")
password = cf.get("MySQL-DB","password")
port = cf.get("MySQL-DB","port")
db = cf.get("MySQL-DB","db")
charset = cf.get("MySQL-DB","charset")
print(host,user,password,port,db,charset)