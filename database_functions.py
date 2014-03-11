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
    con = connectToDatabase('localhost','crawler','crawler','real_estate_analytics','/Applications/MAMP/tmp/mysql/mysql.sock')
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
    con = connectToDatabase('localhost','crawler','crawler','real_estate_analytics','/Applications/MAMP/tmp/mysql/mysql.sock')
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
    #SHOW CREATE TABLE properties
    
    
outputAddressList()
#runQuery("SELECT id, address_detail, address, neighborhood, city, state FROM properties LIMIT 1")