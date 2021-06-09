from invoice2data import extract_data
from invoice2data.extract.loader import read_templates
import os
from collections import defaultdict
import json
import yaml
from datetime import datetime
import inspect
from config import *


def whoami():
    return inspect.stack()[1][3]
def caller_function ():
    return inspect.stack()[2][3]



print(master_json)

def init_master_json(master_json_file = master_json_file):
    global master_json
    if os.path.exists(master_json_file):
        with open(master_json_file, 'r') as f :
            master_json = defaultdict(dict,json.load(f))
    else:
        master_json = defaultdict(dict, master_json)
        
        
def init_removed_json(removed_json_file = removed_json_file):
    global removed_json
    if os.path.exists(removed_json_file):
        with open(removed_json_file, 'r') as f :
            removed_json = defaultdict(dict,json.load(f))
    else:
        removed_json = defaultdict(dict, removed_json)

        
        
def init_updated_json(updated_json_file = updated_json_file):
    global updated_json
    if os.path.exists(updated_json_file):
        with open(updated_json_file, 'r') as f :
            updated_json = defaultdict(dict, json.load(f))
    else:
        updated_json = defaultdict(dict, updated_json)
        
        
        
def update_removed_json(json_data) -> None:
    removed_json[str(datetime.now())] = json_data
    with open(removed_json_file, 'w+') as f:
        json.dump(dict(removed_json_file), f)

        
def update_updated_json(json_data) -> None:
    updated_json[str(datetime.now())] = json_data
    with open(updated_json_file, 'w+') as f:
        json.dump(dict(updated_json), f)

        
def update_master_json(json_data) -> None:
    """
    Inputs:
        Json_data(dict) : data to append to master json file
    Returns: 
        None
    """
    global master_json
    field = 'fields'
    tables = 'tables'
    # Updating Updated_json vairable and file
    update_updated_json(json_data)
    # Appending field to master json
    if field in json_data.keys():
        for data in json_data[field]:
            count = 0
            for i, key_value in enumerate(master_json[field]) :
                if list(key_value.keys())[0] == list(data.keys())[0]:
                    master_json[field][i][list(key_value.keys())[0]].append(str(data[list(data.keys())[0]]))
                    count += 1
                    break
            if count == 0 :
                master_json[field].append({
                    list(data.keys())[0]: [str(data[list(data.keys())[0]])]
                })
    # Updating Table
    if tables in json_data.keys():
        [master_json[tables].append(table) for table in json_data[tables]]
    print("New Master Json\n", master_json)
    with open(master_json_file, 'w+') as f:
        json.dump(dict(master_json), f)
    update_master_yml_file()

        
def update_master_yml_file()-> None:
    '''
    Take master_json and write it to master_yml_file
    '''
    global master_json
    print("updating yml file from {} function ".format(caller_function()))
    formated_json  = defaultdict()
    formated_json['issuer'] = master_json['issuer']
    formated_json['keywords'] = master_json['keywords']
    formated_json['fields'] = defaultdict()
    formated_json['tables'] = []
    if not os.path.exists(master_template_folder):
        os.makedirs(master_template_folder)
    for key_value in master_json['fields']:
        regex_value = '|'.join(set([i for i in key_value[list(key_value.keys())[0]]])) 
        if len(regex_value) > 0:
            formated_json['fields'][list(key_value.keys())[0]]  = regex_value
    del formated_json['fields']['Default']
    formated_json['fields'] = dict(formated_json['fields'])
    if len(formated_json['fields']) == 0:
        del formated_json['fields']
    for table in master_json['tables']:
        formated_json['tables'].append(table)
    del formated_json['tables'][0]
    if len(formated_json['tables']) == 0:
        del formated_json['tables']
    # Save the json data to yml file
    with open(os.path.join(master_template_folder, master_template_yml_file), 'w+') as f:
        yaml.dump(dict(formated_json), f, allow_unicode=True)
        print("Saved master yml data is : \n{}".format(yaml.dump(dict(formated_json))))



        
def removing_data_from_master_json(json_data):
    global master_json
    if not isinstance(json_data, dict):
        raise Exception("json data should be of dict type not {}".format(type(json_data)))
    
    if "fields" in json_data.keys():
        for field in json_data['fields']:
            count = 0
            for index, master_field in enumerate(master_json['fields']):
                if list(field.keys())[0] == list(master_field.keys())[0]:
                    try:
                        count +=1
                        master_json['fields'][index][list(field.keys())[0]].remove(field[list(field.keys())[0]])
                        print(str(field) +"\n\tRemoved")
                    except Exception as e:
                        print(str(field) , "Value not in" , str(master_json['fields'][index]))
            if count == 0:
                print(field, "not in", master_json['fields'])
    # Removing tables
    if "tables" in json_data.keys():
        for table in json_data['tables']:
            try:
                master_json['tables'].remove(table)
                print(str(table)+'\n\tRemoved')
            except Exception as e:
                print(table, "\nnot in master_json tables: \n", master_json['tables'])
    print(removing_data_from_master_json.__name__, "Updating yml file")
    update_master_yml_file()
    print(removing_data_from_master_json.__name__, "updated")
        
        
        
init_master_json()
init_removed_json()
init_updated_json()




'''
Usage:
	from pipeline import *
	
Funcitons:
	update_master_json :
		Pass the json data( from api )  to this function 
		This function will update the master json yml file
	removing_data_from_master_json :
		Pass the json data( from api )  to this function 
		This function will remove json data passed from master json and its yml file


Uninstall invoice2data library from your environment
Then install library from 
pip install git+https://github.com/vk001716/invoice2data

There is also a change in extact_data function of previous code
you have to replace 'template' folder by 'master_template' folder
'''
