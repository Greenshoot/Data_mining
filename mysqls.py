# -*- coding: utf-8 -*-
"""

"""

import pymysql

#连接MYSQL数据库
db = pymysql.connect("localhost","root","root","TESTDB" )
cursor = db.cursor()

#在数据库建表
def creat_table():
    cursor.execute("DROP TABLE IF EXISTS DZDP2")
    sql = '''CREATE TABLE DZDP2(
            cus_id varchar(100),
            comment_time varchar(55),
            comment_star varchar(55),
            cus_comment text(5000),
            kouwei varchar(55),
            huanjing varchar(55),
            fuwu varchar(55),
            shopID varchar(55)
            );'''
    cursor.execute(sql)
    return

#存储爬取到的数据
def save_data(data_dict):
    sql = '''INSERT INTO DZDP2(cus_id,comment_time,comment_star,cus_comment,kouwei,huanjing,fuwu,shopID) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'''
    value_tup = (data_dict['cus_id']
                 ,data_dict['comment_time']
                 ,data_dict['comment_star']
                 ,data_dict['cus_comment']
                 ,data_dict['kouwei']
                 ,data_dict['huanjing']
                 ,data_dict['fuwu']
                 ,data_dict['shopID']
                 )
    try:
        cursor.execute(sql,value_tup)
        db.commit()
    except:
            print(value_tup)
    return

#关闭数据库
def close_sql():
    db.close()
