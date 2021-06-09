import cv2
from collections import defaultdict
import random
import os
import yaml
import boto3
import pandas as pd
import json
from invoice2data import extract_data
from invoice2data.extract.loader import read_templates
import pdftotext
from tabula.io import read_pdf
from django.conf import settings
# from invoice2data.input import tesseract4


ACCESS_KEY = 'AKIAQQ4KTYGPMSNVWL44'
SECRET_ACCESS_KEY = '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'
BUCKET = "campaigns-user-details-production"


s3 = boto3.resource('s3', aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_ACCESS_KEY)

bucket = s3.Bucket(BUCKET)
# def json_yml_conversion(json_data, yml_file):
#     with open(yml_file, 'w') as f:
#         indent  = 4
#         f.write('issuer: {}\n'.format(json_data['issuer']))
#         f.write('keywords:\n')
#         for keyword in json_data['keywords']:
#             f.write(' '*indent + keyword + '\n')
#         if 'fields' in json_data.keys():
#             f.write('fields:\n')
#             for field in json_data['fields']:
#                 f.write(' '* indent + list(field.keys())[0] +': ' +field[list(field.keys())[0]] + '\n')
#         if 'options' in json_data.keys():
#             f.write('options:\n')
#             for options in json_data['options']:
#                 f.write(' '* indent + list(options.keys())[0] +': ' + options[list(options.keys())[0]] + '\n')
#         if 'tables' in json_data.keys():
#             f.write('tables:\n')
#             for tables in json_data['tables']:
#                 f.write(' '* indent + list(tables.keys())[0] +': ' + tables[list(tables.keys())[0]] + '\n')
#                 f.write(' '* indent + list(tables.keys())[1] +': ' + tables[list(tables.keys())[1]] + '\n')
#                 f.write(' '* indent + list(tables.keys())[2] +': ' + tables[list(tables.keys())[2]] + '\n')


def download_folder(bucket_obj, remote_folder, local_folder):
    os.chdir('/home/drishte/invoice-reader')
    for obj in bucket_obj.objects.filter(Prefix=remote_folder):
        if obj.key[-1] == '/':
            continue
        bucket_obj.download_file(obj.key, os.path.join(
            local_folder, os.path.basename(str(obj.key))))


def dump(data, file_name):
    os.chdir('/home/drishte/invoice-reader')
    print(os.getcwd())
    f = open('temp.yml', 'w')
    yaml.dump(data, f)
    f.close()
    f = open('temp.yml', 'r')
    f2 = open(file_name, 'w')
    for line in f:
        f2.write(line.replace("'False'", 'False'))
    f.close()
    f2.close()
    os.remove('temp.yml')

# @app.route("/annotation_test", methods = ['POST', 'GET'])


def annotation_test(filename_pdf, json_data):
    os.chdir('/home/drishte/invoice-reader')
    print(os.getcwd())
    os.system('mkdir -p output_test')
    filename = 'output_test/output_test.yml'
    filename_pdf = 'output_test.pdf'
    print("JSON Data : {}".format(json_data))
    dump(json_data, filename)
    templates = read_templates('output_test')
    result = extract_data(filename_pdf, templates=templates)
    print('json result ', result)
    return result


# @app.route('/create_yml',methods=['GET','POST'])
def create_yml(json_data):
    os.chdir('/home/drishte/invoice-reader')
    print(os.getcwd())
    filename = 'create_yml.yml'
    # data = request.json
    data = json_data
    print('create_yml json data{}'.format(data))
    bucket_file_name = data['filename']
    options = {
        'options': {
            'remove_whitespace': 'False'
        }
    }
    data.update(options)
    del data['filename']
    print('create_yml json data after filename delete{}'.format(data))
#     with open(filename, 'w') as ff:
#         print(yaml.dump(data, ff, allow_unicode=True))
    dump(data, filename)
    bucket.upload_file(filename, 'invoce2data/{}'.format(bucket_file_name))
    print(data)
    return 'success'


# @app.route("/extract_data", methods = ['POST', 'GET'])
def extract_data_(filename_pdf):
    os.chdir('/home/drishte/invoice-reader')
    print(os.getcwd())
    templates_folder = 'master_template'
    print('**********************************')
    print(os.getcwd())
    os.system('pwd')
    # if not os.path.exists(templates_folder):
    #     os.mkdir(templates_folder)
    # for f in os.listdir(templates_folder):
    #     os.remove(os.path.join(templates_folder, f))

    # uploaded_file = request.files['document']
    # uploaded_file.save(filename_pdf)
    # download_folder(
    #     bucket_obj=bucket,
    #     remote_folder='invoice2data/',
    #     local_folder=templates_folder
    # )

    templates = read_templates(templates_folder)
    result = extract_data(os.getcwd()
                          + filename_pdf, templates=templates)
    print(result)
    return result

# @app.route("/extract_table", methods = ['POST', 'GET'])


def extract_table(pdf_file: "pdf file path") -> "list of dataframe of tables in pdf":
    '''
    Installation :
        pip install tabula-py tabula camelot-py[cv]

    Parameters
    ----------
    pdf_file : "pdf file path"
        DESCRIPTION.

    Returns
    -------
    tables : list
        DESCRIPTION.

    '''
    os.chdir('/home/drishte/invoice-reader')
    print(os.getcwd())
    from tabula.io import read_pdf
    tables = read_pdf(pdf_file, pages="all")
    for i in range(len(tables)):
        tables[i] = tables[i].fillna("")
    return tables
