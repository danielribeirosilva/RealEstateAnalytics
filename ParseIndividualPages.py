# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 13:31:58 2014

@author: daniel
"""

from bs4 import BeautifulSoup
import os
import sys
import MySQLdb
import re

file_folder = 'detailed_pages/'
sleep_time = 10

#get list of files in target directory
files_list = os.listdir(file_folder)


# ----------------------------------------------------
# FUNCTION THAT PARSES ONE PAGE 
# ----------------------------------------------------

def parsePage(file_path):
    
    f = open(file_path, 'r')
    html = f.read();
    soup = BeautifulSoup(html, "html.parser")
    
    #get main info block - all main info is here
    main_info_block = soup.find(attrs={'class':'ficha_dadosprincipais'})
    
    #get header block - data here: ref_num, property_type, deal_type, price
    main_info_block_header = main_info_block.find(attrs={'class':'ficha_dadosprincipais_titulo'})
    type_block = main_info_block_header.find(attrs={'class':'ficha_texto18', 'class':'ficha_titulo'})
    
    print type_block.prettify()
    
    
    
    #return fields
    
    
    
    
    
# ----------------------------------------------------
# RUN PARSING ON ALL NEW FILES 
# ----------------------------------------------------


try:
    con = MySQLdb.connect(host = 'localhost',
                          user = 'crawler',
                          passwd = 'crawler', 
                          db = 'real_estate_analytics', 
                          unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock')
    cur = con.cursor()

    for file_name in files_list:
        print file_name
        #ignore system files, etc
        if file_name[-4:] <> ".txt":
            continue
        #get ref num and last update form file name
        split_name = re.split("[_\.]",file_name)
        ref_num = split_name[0]
        last_update = split_name[1]
        #adjust date format from BR (dd-mm-yyyy) to MySQL DATE(yyyy-mm-dd)
        split_date = re.split("[-]",last_update)
        last_update = "-".join(reversed(split_date))
        
        
        # TEST ---------------------------------------------
        parsePage(file_folder+file_name)
        break
        

        # --------------------------------------------------        
        
        
        
        #check if file has already been uploaded to db
        cur.execute("SELECT * FROM properties WHERE ref_num = '" + ref_num + "' AND last_update = '" + last_update + "'")
        if cur.fetchone() <> None:
            continue
        
        #parsePage(file_folder+file_name)        
        
        
        cur.execute("SELECT * FROM properties WHERE ref_num = 'asd123' AND last_update = '2014-03-09'")
        ver = cur.fetchone()    
        print ver
        
        break
    
except MySQLdb.Error, e:
  
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)
    
finally:    
    if con:    
        con.close()


