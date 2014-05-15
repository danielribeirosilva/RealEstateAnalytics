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
import aux

date_extracted = '2014-03-13'
file_folder = 'detailed_pages/'+date_extracted+"/"
table_name = 'properties'

#get list of files in target directory
files_list = os.listdir(file_folder)



# -----------------------------------------------------------------------------
# AUX FUNCTIONS 
# -----------------------------------------------------------------------------

def strip_accents(s):
   no_accents_unicode = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
   return unicodedata.normalize('NFKD', no_accents_unicode).encode('ascii','ignore')

def normalize_float(s):
    s = s.replace(".","")
    s = s.replace(",",".")
    return s

def getPageTitle(file_path):
    f = open(file_path, 'r')
    html = f.read();
    soup = BeautifulSoup(html, "html.parser")
    return soup.title.get_text()

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
    type_block_text_parts = type_block.get_text().split('|')
    deal_type = type_block_text_parts[0].strip()
    if len(type_block_text_parts) > 1:
        property_type = type_block_text_parts[1].strip()
    else:
        property_type = ""

    price_block = main_info_block_header.find(attrs={'class':'ficha_texto16'})
    price = price_block.get_text() # in format "R$ xxx.xxx,xx"
    price = price.split()[-1] # remove R$
    if price == "Consulte":
        price = '0'
    else:
        price = price.replace(".","") #remove . separators
        price = price.split(',')[0] #remove decimal part, if any
    
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
    
    area_total = '0'
    area_usable = '0'
    area_land = '0'
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
            base_text = compl_info_block.get_text()
            base_text = base_text.replace(" de ", " ")
            base_text = base_text.replace(" da ", " ")
            base_text = base_text.replace(" do ", " ")
            base_text = base_text.replace(":", ": ")
            areas_split = re.sub(r'[\s\t\n]+',r' ',base_text).split()
            for idx in range(len(areas_split)/4):
                area_type = strip_accents(areas_split[4*idx + 1])
                area_value = normalize_float(areas_split[4*idx + 2])
                if area_type == "util:":
                    area_usable = area_value
                elif area_type == "total:":
                    area_total = area_value
                elif area_type == "terreno:":
                    area_land = area_value
        #dimensions
        elif compl_block_title_no_accents == "Dimensoes":
            width = 0
            length = 0
            base_text = compl_info_block.get_text()
            base_text = base_text.replace(":", ": ")
            base_text = base_text.replace("Comprimento", " Comprimento")
            base_text = base_text.replace("Largura", " Largura")
            dimensions_split = re.sub(r'[\s\t\n]+',r' ',base_text).split()
            for idx in range(len(dimensions_split)/3):
                dimension_type = strip_accents(dimensions_split[3*idx + 0])
                dimension_value = dimensions_split[3*idx + 1].replace(",",".")
                if "Largura" in dimension_type:
                    width = float(dimension_value)
                elif "Comprimento" in dimension_type:
                    length = float(dimension_value)
            computed_area = width*length
            #print str(width) + "*" + str(length) + "=" + str(computed_area)
            if float(area_total) <= 0:
                area_total = str(computed_area)
            if float(area_land) <= 0:
                area_land = str(computed_area)
        #extra info
        else:
            current_extra_info_text = re.sub(r'[\s\t\n]+',r' ',compl_info_block.get_text())
            extra_info = extra_info + current_extra_info_text + "  |  "
    
    
    #try to find area in text if not specfied
    if float(area_total)==0 and float(area_usable)==0 and float(area_land)==0:
        search_regex = r'([\.0-9,]+[ ]*[mM][²2])'
        search_result = re.search(search_regex,observations)
        if search_result:
            detected_area_text = search_result.group(1)
            detected_area_text = re.split(r'[mM]',detected_area_text)[0]
            area_total = normalize_float(detected_area_text)
            print "detected area: " + area_total
        else:
            search_result = re.search(search_regex,extra_info)
            if search_result:
                detected_area_text = search_result.group(1)
                detected_area_text = re.split(r'[mM]',detected_area_text)[0]
                area_total = normalize_float(detected_area_text)
                print "detected area: " + area_total
    
    columns = []
    values = []
    
    columns.append("deal_type")
    values.append(deal_type)
    columns.append("property_type")
    values.append(property_type)
    columns.append("price")
    values.append(price)
    
    columns.append("address_detail_type")
    values.append(address_detail_type)
    columns.append("address_detail")
    values.append(address_detail)
    columns.append("address")
    values.append(address)
    columns.append("neighborhood")
    values.append(neighborhood)
    columns.append("city")
    values.append(city)
    columns.append("state")
    values.append(state)
    
    columns.append("area_total")
    values.append(area_total)
    columns.append("area_usable")
    values.append(area_usable)
    columns.append("area_land")
    values.append(area_land)
    columns.append("observations")
    values.append(observations)
    columns.append("extra_info")
    values.append(extra_info)
    
    return [columns,values]
    
    
    
    
    
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
        
        #check if file has already been uploaded to db
        cur.execute("SELECT * FROM properties WHERE ref_num = '" + ref_num + "' AND last_update = '" + last_update + "'")
        if cur.fetchone() <> None:
            continue
        
        #check if page is empty (was sold in between)
        page_title = getPageTitle(file_folder+file_name)
        if "foi encontrado nenhum" in page_title:
            print "REMOVING...\n"
            #update db with sold properties
            aux.updateDbWithSoldProperties([ref_num],date_extracted)
            #update db with active lists of properties (remove it from actives)
            aux.updateDbWithActiveProperties([],[ref_num])
            continue
        
        #parse page and get info
        print "ref: " + ref_num
        columns_and_values = parsePage(file_folder+file_name)
        columns = columns_and_values[0]        
        values = columns_and_values[1]
        
        #add ref_num and last_update to info
        columns.insert(0,"last_update")
        values.insert(0,last_update)
        columns.insert(0,"ref_num")
        values.insert(0,ref_num)
        #add extraction date
        columns.append('date_extracted')
        values.append(date_extracted)
        
        #insert info in database
        columns = ['`'+s+'`' for s in columns ]
        values = ['"'+s.replace("\"","")+'"' for s in values ]
        query = "INSERT INTO `" + table_name + "` (" + ",".join(columns) + ") VALUES(" +  ",".join(values) + ")"
        try:
           cur.execute(query)
           con.commit()
        except:
           con.rollback()        
        
        #print query
        #break

    
except MySQLdb.Error, e:
  
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)
    
finally:    
    if con:    
        con.close()


