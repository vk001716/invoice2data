
global reader
from invoice2data import *
# from .migrate import *



def whoami():
    import inspect
    print("*"*30)
    return inspect.stack()[1][3]
def caller_function ():
    import inspect
    print("\t"+":"*10)
    return inspect.stack()[2][3]






def convert_pdf_to_image(pdf_file):
    import os
    from pdf2image import convert_from_path
    temp_directory = "temp_directory"
    os.system(f"rm -r {temp_directory}")
    os.system("mkdir -p {}".format(temp_directory))
    images = convert_from_path(pdf_file)
    image_files = []
    for i in range(len(images)):
        save_file_name = temp_directory + "/" + 'page'+ str(i) +'.jpg'
        images[i].save(save_file_name, 'JPEG')
        image_files.append(save_file_name)
    return image_files



def convert_image_to_string(image_files):
    import easyocr
    if "reader" not in globals():
        global reader 
        reader = easyocr.Reader(['en'], gpu = False)
    reader_results = []
    text_extractions = []
    for image_file in image_files:
        reader_result =  reader.readtext(\
               image = image_file,
               width_ths = 10,
               height_ths=1.5
               )
        reader_results.append(reader_result)
    for reader_result in reader_results:
        for (bbox, text, prob) in reader_result: 
            text_extractions.append(text)
            print(text)
    print(whoami())
    print(text_extractions)
    return text_extractions

def image_string_post_processing(string_list):
    replace_list = [
        ("`", ""),
        (";", ":"),
        ("~", ""),
    ]
    for string in string_list:
        for item in replace_list:
            string.replace(item[0], item[1])
    print(whoami())
    print(string_list)
    return string_list



def convert_string_to_pdf(string_list, pdf_file = "image-string-pdf.pdf"):
    from fpdf import FPDF
    # save FPDF() class into a 
    # variable pdf
    # Add a page
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(left=0, top=0, right=0)
    # set style and size of font 
    # that you want in the pdf
    pdf.set_font("Arial", size = 15)
    for text in string_list: 
        pdf.cell(0, 0, txt = text,ln =1 )
    pdf.output(pdf_file)
    return pdf_file





def image_pdf_string(pdf_file):
    '''
    This fuction is to be used during annotation
    -> Takes a image pdf and gives its equivalent string
    '''
    image_files = convert_pdf_to_image(pdf_file)
    image_2_string = convert_image_to_string(image_files)
    image_2_string = image_string_post_processing(image_2_string)
    print(whoami())
    print(image_2_string)
    return image_2_string




def image_pdf_final_result(pdf_file):
    '''
    Takes an image pdf returns text pdf form
    '''
    image_2_string = image_pdf_string(pdf_file)
    new_pdf_file = convert_string_to_pdf(image_2_string)
    return extract_data_(new_pdf_file)
