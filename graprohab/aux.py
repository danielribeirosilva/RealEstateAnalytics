# -*- coding: utf-8 -*-
"""
Created on Fri May 16 15:58:34 2014

@author: daniel
"""

import MySQLdb
import sys

def connectToDatabase(h, u, p, d_b, u_s):
    try:
        con = MySQLdb.connect(host = h,
                          user = u,
                          passwd = p, 
                          db = d_b, 
                          unix_socket=u_s,
                          charset = "utf8")
        return con
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)

def connectToDefaultDatabase():
    return connectToDatabase('localhost','root','root','graprohab','/Applications/MAMP/tmp/mysql/mysql.sock')
    
def entryExists(date, order_number):
    con = connectToDefaultDatabase()
    cur = con.cursor()
    try:
        query = "SELECT * FROM entries WHERE meeting_date='" + date + "' AND order_number='" + str(order_number) + "'"
        cur.execute(query)
        row = cur.fetchone()
        if row == None:
            return False
        return True
    except MySQLdb.Error, e:
       print "Error %d: %s" % (e.args[0],e.args[1])
    finally:
        con.close()

def insertEntry(entry):
    con = connectToDefaultDatabase()
    cur = con.cursor()
    columns=[]
    values=[]
    for key in entry.keys():
        columns.append(key)
        values.append(entry[key])
    query = "INSERT INTO `entries` (" + ",".join(columns) + ") VALUES(" +  ",".join(values) + ")"
    try:
       cur.execute(query)
       con.commit()
    except:
       con.rollback()  
       
def getColumnName(key):
    return{
        u'N\xba de ordem' : 'order_number',
        u'N\xba Protocolo' : 'protocol',
        u'Interessado' : 'interested',
        u'Munic\xedpio' : 'city',
        u'Regi\xe3o' : 'region',
        u'Empreendimento' : 'enterprise',
        u'N\xba de unidades' : 'units'
    }[key]