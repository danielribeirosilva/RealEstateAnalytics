# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 02:41:58 2014

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
    return connectToDatabase('localhost','crawler','crawler','real_estate_analytics','/Applications/MAMP/tmp/mysql/mysql.sock')

def fieldIsGiven(field):
    field = field.strip()
    if "Não Informado" in field:
        return False
    if len(field) <= 0:
        return False
    if field == ",":
        return False
    return True
    
def processField(s):
    if s[-1] == ',':
        s = s[:-1]
    return s

def buildFullAddress(address_detail, address, neighborhood, city, state):
    full_address = ""
    if fieldIsGiven(address_detail):
        full_address += processField(address_detail) + ", "
    if fieldIsGiven(address):
        full_address += processField(address) + ", "
    #return empty if none of the above are provided
    if full_address == "":
        return ""
    #otherwise, continue
    if fieldIsGiven(neighborhood):
        full_address += processField(neighborhood) + ", "
    if fieldIsGiven(city):
        full_address += processField(city) + " - "
    if fieldIsGiven(state):
        full_address += processField(state)
    return full_address


def outputAddressList():
    con = connectToDefaultDatabase()
    cur = con.cursor()
        
    try:
        query = "SELECT id, address_detail, address, neighborhood, city, state FROM properties"
        cur = con.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(query)
    
        row = cur.fetchone()
        while row is not None:
            r_id = row["id"]
            row = {idx:s.encode('utf-8') for idx,s in row.iteritems() if isinstance(s, basestring)}
            full_address = buildFullAddress(row["address_detail"] ,row["address"],row["neighborhood"],row["city"],row["state"])
            
            #print str(r_id) + " : " + row["address_detail"] + " " + row["address"] + " " + row["neighborhood"]
            print str(r_id) + " : " + full_address
            #print "---------------------------------------------------------------------------"            
            
            row = cur.fetchone()
        
    except MySQLdb.Error, e:
       print "Error %d: %s" % (e.args[0],e.args[1])
    con.close()



def runQuery(q):
    con = connectToDefaultDatabase()
    cur = con.cursor()
    try:
        cur.execute(q)
        row = cur.fetchone()
        while row is not None:
            print row
            row = cur.fetchone()
    except MySQLdb.Error, e:
       print "Error %d: %s" % (e.args[0],e.args[1])
    finally:
        con.close()
        
        
def getAllPropertiesRefNum():
    con = connectToDefaultDatabase()
    cur = con.cursor()
    try:
        query = "SELECT ref_num FROM properties GROUP BY ref_num"
        cur.execute(query)
        all_ref_num = [row[0] for row in cur.fetchall()]
        return all_ref_num
    except MySQLdb.Error, e:
       print "Error %d: %s" % (e.args[0],e.args[1])
    finally:
        con.close()    

def entryExists(ref_num, last_update):
    con = connectToDefaultDatabase()
    cur = con.cursor()
    try:
        query = "SELECT * FROM properties WHERE ref_num="+str(ref_num)+" AND last_update='"+str(last_update)+ "'"
        cur.execute(query)
        row = cur.fetchone()
        if row == None:
            return False
        return True
    except MySQLdb.Error, e:
       print "Error %d: %s" % (e.args[0],e.args[1])
    finally:
        con.close()

def updateDbWithSoldProperties(sold_properties, date):
    con = connectToDefaultDatabase()
    cur = con.cursor()
    for p in sold_properties:
        query = "INSERT INTO sold(ref_num, selling_date) VALUES("+str(p)+", '"+str(date)+"')"
        try:
           cur.execute(query)
           con.commit()
        except:
           con.rollback()
    con.close()
    
    
#getAllPropertiesRefNum()