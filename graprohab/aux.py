# -*- coding: utf-8 -*-
"""
Created on Fri May 16 15:58:34 2014

@author: daniel
"""

import MySQLdb
import sys
import re

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

def organExists(entry_id, organ):
    con = connectToDefaultDatabase()
    cur = con.cursor()
    try:
        query = "SELECT * FROM organs WHERE entry_id='" + str(entry_id) + "' AND organ_name='" + organ + "'"
        cur.execute(query)
        row = cur.fetchone()
        if row == None:
            return False
        return True
    except MySQLdb.Error, e:
       print "Error %d: %s" % (e.args[0],e.args[1])
    finally:
        con.close()

def insertEntry(entry, meeting_date):
    con = connectToDefaultDatabase()
    cur = con.cursor()
    columns=[]
    values=[]
    for key in entry.keys():
        if u'Org\xe3os' in key: #this field will be inserted in another table
            continue
        columns.append(getColumnName(key))
        values.append("'"+adjustFormat(entry[key])+"'")
    columns.append('meeting_date')
    values.append("'"+meeting_date+"'")
    query = "INSERT INTO `entries` (" + ",".join(columns) + ") VALUES(" +  ",".join(values) + ")"
    print '---------\n'+query
    try:
       cur.execute(query)
       con.commit()
    except:
       con.rollback()  

def adjustFormat(word):
    return re.sub("'"," ",word) #remove simple quotes
       
def getEntryId(entry, meeting_date):
    con = connectToDefaultDatabase()
    cur = con.cursor()
        
    try:
        query = "SELECT id FROM entries WHERE order_number = '" + entry[u'N\xba de ordem'] + "' AND meeting_date = '" + meeting_date + "'"
        print "--------------\n" + query
        cur = con.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(query)
    
        row = cur.fetchone()
        return row["id"]
        
    except MySQLdb.Error, e:
       print "Error %d: %s" % (e.args[0],e.args[1])
    con.close()
    
       
def insertOrgans(entry_id,organ_list):
    con = connectToDefaultDatabase()
    cur = con.cursor()
    for organ in organ_list:
        if organExists(entry_id, organ):
            continue
        query = "INSERT INTO `organs` (entry_id, organ_name) VALUES('" + str(entry_id) + "','" + organ + "')"
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