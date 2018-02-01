#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
"""
The code below has the following steps:

1- Opens the xml defined in OSM_FILE.
2- Extract the nodes to NODES_FILE.
3- Extract the nodes' key-values to NODE_TAGS_FILE
4- Extract ways to WAYS_FILE
5- Extract ways' key-values to WAY_TAGS_FILE

The output files are .csv comma separated.
"""

import xml.etree.cElementTree as ET
import unicodecsv as csv
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# FILES
OSM_FILE = "san-sebastian_spain.osm.xml"
NODES_FILE = "nodes.csv"
NODE_TAGS_FILE = "node_tags.csv"
WAYS_FILE = "ways.csv"
WAY_TAGS_FILE = "way_tags.csv"

# CSV HEADERS

NODES_HEADER = ["id", "lat", "lon", "user"]
NODE_TAGS_HEADER = ["id", "key", "value"]
WAYS_HEADER = ["id", "user"]
WAY_TAGS_HEADER = ["id", "key", "value"]

def clean_streets(name):
    """ The function receives a street name and fix it. It does the process on different steps:
    1- Fix Capital letters
    2- Remove Spanish Language and leaves the Basque one
    3- Changes Avda. to Etorbida
    4- Changes CR CRTA to Kalea
    5- Changes pz to Plaza
    6- If the name is in different order (we separate them by commas), then we remove the comma and inverse the order
    """
    name = name.title()
    name = str(name.split("/")[0])
    # Fix Etorbidea abreviation
    name = re.sub(r"Avda\.", "Etorbidea", name)
    # Fix Kalea Abreviation
    name = re.sub(r"CL", "Kalea", name)
    # Fix Karretera
    name = re.sub(r"Cr", "Kalea", name)
    name = re.sub(r"Crta", "Kalea", name)
    # Fix Plaza
    name = re.sub(r"Pz", "Plaza", name)
    # Switch order
    name = name.split(",")[::-1]
    return ' '.join(name).strip()

def write_csv(output,fieldnames,data):
    """ This function writes the dictionary it receives to a csv file. These are the parameters:
    output: this is the filename of the file to write to.
    fieldnames: the "keys" of our dictionary, used as fieldnames on csv
    data: the dictionary itself with the data that needs to be written to "output" file
    """
    with open(output, 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, encoding='utf-8')
        for dict in data:
            if dict != {}:
                writer.writerow(dict)

def extract_data(type,input):
    """ Principal function. It extract the kind of data we want from the xml file.
    These are the parameters:
    type: it can be "node", "node_tags", "way", "way_tags".
    input: the xml file to examine

    Returns nothing.
    """

    temp_list=[]
    """ If the type is "node" then we find those elements with name "node" and extract
    id, lat, lon, user from them and store in a temporary dictionary.
    When the loop is finished and all file scanned, we call write_csv to export
    the result dictionary to a file.
    """
    if type == "node":
        for event, elem in ET.iterparse(input):
            temp_dict={}
            if elem.tag == "node":
                temp_dict["id"]=elem.get("id")
                temp_dict["lat"]=elem.get("lat")
                temp_dict["lon"]=elem.get("lon")
                temp_dict["user"]=elem.get("user")
                temp_list.append(temp_dict)
                temp_dict={}
        write_csv(NODES_FILE,NODES_HEADER,temp_list)

        """ If the type is "node_tags" then we find those elements with name "node" at least
        one tag (key-pair value). Then we extract the id, key and value.
        When the loop is finished and all file scanned, we call write_csv to export
        the result dictionary to a file.
        """
    elif type == "node_tags":

        for event, elem in ET.iterparse(input):
            temp_dict={}
            if elem.tag == "node":
                # We analyze those "nodes" that has at least one tag (one key-value pair)
                if list(elem) != []:
                    for tag in list(elem):
                        if tag.get("k") != "created_by":
                            temp_dict["id"]=elem.get("id")
                            temp_dict["key"]=tag.get("k")
                            if tag.get("k") == "addr:street":
                                temp_dict["value"]=clean_streets(tag.get("v"))
                            else:
                                temp_dict["value"]=tag.get("v")
                            temp_list.append(temp_dict)
                            temp_dict={}
        write_csv(NODE_TAGS_FILE,NODE_TAGS_HEADER,temp_list)

    elif type == "way":
    # Follows same logic as "nodes", but extracting id and user instead.
        for event, elem in ET.iterparse(input):
            temp_dict={}
            if elem.tag == "way":
                temp_dict["id"]=elem.get("id")
                temp_dict["user"]=elem.get("user")
                temp_list.append(temp_dict)
                temp_dict={}
        write_csv(WAYS_FILE,WAYS_HEADER,temp_list)

    elif type == "way_tags":
    # Follows same logic as "node_tags", but extracting id, key and value instead.
        for event, elem in ET.iterparse(input):
            temp_dict={}
            if elem.tag == "way":
                if list(elem) != []:
                    for tag in list(elem):
                        if tag.keys() == ['k', 'v']:
                            temp_dict["id"]=elem.get("id")
                            temp_dict["key"]=tag.get("k")
                            if tag.get("k") == "addr:street":
                                temp_dict["value"]=clean_streets(tag.get("v"))
                            else:
                                temp_dict["value"]=tag.get("v")
                            temp_dict["value"]=tag.get("v")
                            temp_list.append(temp_dict)
                            temp_dict={}
        write_csv(WAY_TAGS_FILE,WAY_TAGS_HEADER,temp_list)

extract_data("node",OSM_FILE)
extract_data("node_tags",OSM_FILE)
extract_data("way",OSM_FILE)
extract_data("way_tags",OSM_FILE)
