
from collections import defaultdict
import random
import os
import yaml
import json
from invoice2data import extract_data
from invoice2data.extract.loader import read_templates
# import pdftotext
#from tabula.io import read_pdf
# from invoice2data.input import tesseract4

try:
    os.chdir('/home/ubuntu/invoice-reader')
except Exception as e:
    print("home directory not changed to /home/ubuntu/invoice-reader")


# @app.route("/extract_data", methods = ['POST', 'GET'])
def extract_data_(filename_pdf):
#     os.chdir('/home/drishte/invoice-reader')
    print(os.getcwd())
    templates_folder = 'master_template'
    print('**********************************')
#     print(os.getcwd())
#     os.system('pwd')
    templates = read_templates(templates_folder)
    result = extract_data(os.getcwd()
                          + filename_pdf, templates=templates)
    print(result)
    return result

# @app.route("/extract_table", methods = ['POST', 'GET'])

# def extract_table(pdf_file: "pdf file path") -> "list of dataframe of tables in pdf":
#     '''
#     Installation :
#         pip install tabula-py tabula camelot-py[cv]

#     Parameters
#     ----------
#     pdf_file : "pdf file path"
#         DESCRIPTION.

#     Returns
#     -------
#     tables : list
#         DESCRIPTION.

#     '''
#     os.chdir('/home/drishte/invoice-reader')
#     print(os.getcwd())
#     from tabula.io import read_pdf
#     tables = read_pdf(pdf_file, pages="all")
#     for i in range(len(tables)):
#         tables[i] = tables[i].fillna("")
#     return tables
