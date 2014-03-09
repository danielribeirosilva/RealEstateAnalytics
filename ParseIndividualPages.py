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
import unicodedata


file_folder = 'detailed_pages/'
sleep_time = 10

#get list of files in target directory
files_list = os.listdir(file_folder)



# -----------------------------------------------------------------------------
# AUX FUNCTIONS 
# -----------------------------------------------------------------------------

def strip_accents(s):
   no_accents_unicode = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
   return unicodedata.normalize('NFKD', no_accents_unicode).encode('ascii','ignore')



# -----------------------------------------------------------------------------
# FUNCTION THAT PARSES ONE PAGE 
# -----------------------------------------------------------------------------

def parsePage(file_path):
    
    f = open(file_path, 'r')
    html = f.read();
    soup = BeautifulSoup(html, "html.parser")
    
    #get main info block - all main info is here
    main_info_block = soup.find(attrs={'class':'ficha_dadosprincipais'})
    
    #get header block - data here: ref_num, property_type, deal_type, price
    main_info_block_header = main_info_block.find(attrs={'class':'ficha_dadosprincipais_titulo'})
    
    type_block = main_info_block_header.find(attrs={'class':'ficha_texto18', 'class':'ficha_titulo'})
    deal_type = type_block.contents[0]
    property_type = type_block.contents[-1].contents[-1].split()[-1]

    price_block = main_info_block_header.find(attrs={'class':'ficha_texto16'})
    price = price_block.contents[0].contents[0] # in format "R$ xxx.xxx,xx"
    price = price.split()[-1] # remove R$
    if price == "Consulte":
        price = int(0)
    else:
        price = price.replace(".","") #remove . separators
        price = price.split(',')[0] #remove decimal part, if any
        price = int(price)
    
    #get all sub-blocks of info form main info block
    list_of_info_blocks = []
    list_of_info_blocks = list_of_info_blocks + main_info_block.find_all(attrs={'class':'ficha_dadosprincipais_informacoes'})
    list_of_info_blocks = list_of_info_blocks + main_info_block.find_all(attrs={'class':'ficha_dadosprincipais_informacoes_metade'})
    list_of_info_blocks = list_of_info_blocks + main_info_block.find_all(attrs={'class':'ficha_dadosprincipais_informacoes_umquarto'})

    address_detail_type_list = ["Edificio","Condominio"]    
    address_detail_type = ""
    address_detail = ""
    address = ""
    neighborhood = ""
    city = ""
    state = ""
    extra_info = ""
    
    for info_block in list_of_info_blocks:
        info_title = info_block.contents[0].strip()
        info_data = info_block.span.contents[0].strip()
        
        if len(info_title) == 0: #no info is provided about content
            extra_info = extra_info + info_data + "  |  "
            continue
        
        info_title_no_accents = strip_accents(info_title)
        
        if info_title_no_accents in address_detail_type_list:
            address_detail_type = info_title
            address_detail = info_data
        elif info_title_no_accents == "Endereco":
            address = info_data
        elif info_title_no_accents == "Bairro":
            neighborhood = info_data
        elif info_title_no_accents == "Cidade":
            city = info_data.split(',')[0].strip()
            state = info_data.split(',')[1].strip()
        else:
            extra_info = extra_info + info_title + ": " + info_data + "  |  "
    
    
    #get blocks of complementary info: Areas, Observation, and Extra Infos
    list_of_complementary_info_blocks = main_info_block.find_all(attrs={'class':'ficha_detalhes'})
    
    area_total = float(0)
    area_usable = float(0)
    area_land = float(0)
    observations = ""    
    
    for compl_info_block in list_of_complementary_info_blocks:
        compl_block_title = compl_info_block.find(attrs={'class':'ficha_texto16'}).contents[0]
        compl_block_title_no_accents = strip_accents(compl_block_title)
        compl_info_block.span.decompose() #remove title
        #observations
        if compl_block_title_no_accents == "Observacoes":
            observations = re.sub(r'[\s\t\n]+',r' ',compl_info_block.get_text())
        #areas
        elif compl_block_title_no_accents == "Areas":
            area_total = 0
            areas_split = re.sub(r'[\s\t\n]+',r' ',compl_info_block.get_text()).split()
            for idx in range(len(areas_split)/4):
                area_type = strip_accents(areas_split[4*idx + 1])
                area_value = float(areas_split[4*idx + 2].replace(",","."))
                if area_type == "util:":
                    area_usable = area_value
                elif area_type == "total:":
                    area_total = area_value
                elif area_type == "terreno:":
                    area_land = area_value
        #extra info
        else:
            current_extra_info_text = re.sub(r'[\s\t\n]+',r' ',compl_info_block.get_text())
            extra_info = extra_info + current_extra_info_text + "  |  "
    
    

    #print price#_block.prettify()
    
    
    
    
    values = []
    
    values.append(deal_type)
    values.append(property_type)
    values.append(price)
    
    values.append(address_detail_type)
    values.append(address_detail)
    values.append(address)
    values.append(neighborhood)
    values.append(city)
    values.append(state)
    
    values.append(area_total)
    values.append(area_usable)
    values.append(area_land)
    values.append(observations)
    values.append(extra_info)
    
    return values
    
    
    
    
    
# -----------------------------------------------------------------------------
# RUN PARSING ON ALL NEW FILES 
# -----------------------------------------------------------------------------


try:
    con = MySQLdb.connect(host = 'localhost',
                          user = 'crawler',
                          passwd = 'crawler', 
                          db = 'real_estate_analytics', 
                          unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock')
    cur = con.cursor()

    for file_name in files_list:
        
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
        print "ref: " + ref_num        
        values = parsePage(file_folder+file_name)
        print values
        break
        

        # --------------------------------------------------        
        
        
        
        #check if file has already been uploaded to db
        cur.execute("SELECT * FROM properties WHERE ref_num = '" + ref_num + "' AND last_update = '" + last_update + "'")
        if cur.fetchone() <> None:
            continue
        
        #parsePage(file_folder+file_name)        
        
        
        #cur.execute("SELECT * FROM properties WHERE ref_num = 'asd123' AND last_update = '2014-03-09'")
        #ver = cur.fetchone()    
        #print ver
        
        #break
    
except MySQLdb.Error, e:
  
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)
    
finally:    
    if con:    
        con.close()


