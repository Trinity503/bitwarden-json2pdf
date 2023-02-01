#pip3 install fpdf
#pip3 install imagesize
'''
    convert bitwarden export to pdf
'''

from glob import glob
from os.path import exists, join
import json
from jinja2 import Environment

#for the pdf creation
from fpdf import FPDF

#for the creation-date
import datetime
x = datetime.datetime.now()
date = x.strftime("%Y") + '-' + x.strftime("%m") + '-' + x.strftime("%d")

#for the image
import imagesize




# initializing variables with values
fileName = 'Bitwarden - Passwortliste.pdf'
documentTitle = 'Bitwarden - Passwortliste'
title = 'Bitwarden - Passwortliste'
subTitle = 'Streng geheim!'
#image = 'MZ.png'
image = 'eching_image.jpg'

width, height = imagesize.get(image)


class PDF(FPDF):
    def header(self):
      if self.page_no() == 1:
        # Logo
        #self.image(image, 100, 15, 20)#markus
        self.image(image, 70, 15, 70)#eching

        # Arial bold 15
        self.set_font('Cardelina', '', 36)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 70, documentTitle, 0, 0, 'C')
        # Line break
        self.ln(50)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Cardelina', '', 8)
        # Page number
        self.cell(0, 10, date + ' || ' 'Seite ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


pdf = PDF(orientation='P', unit='mm', format='A4')

pdf.add_font('Cardelina','','Cardelina.ttf', uni=True)

#pdf_w=210
#pdf_h=297
pdf.set_font('Cardelina', '', 16)
pdf.alias_nb_pages()
pdf.add_page()
#pdf.ln(30)








def get_password_file_name():
    '''
    Returns the name of the password file
    '''
    possibilities = ['./resources/password.json', './password.json']
    for possibility in possibilities:
        if exists(possibility):
            return possibility

    other_findings = []

    other_findings.append(glob(join('./resources', 'bitwarden*.json')))
    other_findings.append((glob('./bitwarden*.json')))

    if len(other_findings[0]) != 0:
        return other_findings[0][0].replace('\\', '/')
    elif len(other_findings[1]) != 0:
        return other_findings[1][0].replace('\\', '/')
    else:
        raise FileNotFoundError("No password file found")


def check_field(bitwarden_item, field):
    '''
    Checks if a field is present in the bitwarden item and applies default value if not
    '''
    try:
        return bitwarden_item[field]
    except KeyError:
        return None


def parse_item(bitwarden_item):
    '''
    Converts bitwarden syntax to intern syntax
    '''
    i_item = {}
    i_item["name"] = check_field(bitwarden_item, "name")
    i_item["notes"] = check_field(bitwarden_item, "notes")
    i_item["type"] = check_field(bitwarden_item, "type")
    login = check_field(bitwarden_item, "login")
    if login:
        i_item["username"] = check_field(login, "username")
        i_item["password"] = check_field(login, "password")
    try:
        i_item["url"] = bitwarden_item["login"]["uris"][0]["uri"]
    except (KeyError, IndexError):
        i_item["url"] = None
    return i_item



print("Passwortliste: " + get_password_file_name())

#with open('./output.html', 'w', encoding="utf-8") as input_file:
    #html_file.write(parse_to_html())
    
categories = []
unrelated_category = {'name': 'Uncategorized', 'items': []}
categories.append(unrelated_category)

with open(get_password_file_name(), 'r', encoding="utf-8") as bitwarden_file:
        data = json.load(bitwarden_file)
        #print(data)
        for folder in data["folders"]:
            folder_id = folder["id"]
            folder_name = folder["name"]
            #pdf.drawText(folder["name"])
            #print(folder_name)
            category = {}
            category["items"] = []
            category["name"] = folder_name
            for item in data["items"]:
                if item["folderId"] == folder_id:
                    category["items"].append(parse_item(item))
            categories.append(category)
        for item in data["items"]:
            if item["folderId"] is None:
                unrelated_category["items"].append(parse_item(item))


for category in categories:
   for item in category["items"]:
      pdf.set_text_color(0)
      pdf.set_font_size(16)
      pdf.cell(0, 5, item["name"], 0, 1)
      pdf.set_text_color(155)
      pdf.set_font_size(12)
      if item["type"] == 1:
        pdf.cell(0, 5, "Username: " + item["username"], 0, 1)
        pdf.cell(0, 5, "Password: " + item["password"], 0, 1)
      if item["url"]:
        pdf.multi_cell(0, 5, "URL: " + item["url"], 0, 1)
      if item["notes"]:
        pdf.multi_cell(0, 5, "Notes: " + item["notes"], 0, 1)
      pdf.ln(8)
      
#     text.setFillColor(colors.black)
#     text.setFont('abc', 16)
#     text.textLine(text=item["name"])
#     text.setFont('abc', 12)
#     text.setFillColor(colors.gray)
#     text.textLine(text="Username: " + item["username"])
#     text.textLine(text="Password: " + item["password"])
#     text.textLine(text="URL: " + item["url"])
#     if item["notes"]:
#       text.textLine(text="Notes: " + item["notes"])
#     text.textLine(text="")
    
    

pdf.output(fileName,'F')
    
    
