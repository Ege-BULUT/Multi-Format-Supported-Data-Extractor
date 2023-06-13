import fitz
import os
import pytesseract
import csv
import io
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'P:\Simply-Deliver\Teserract\tesseract.exe'

# Open the PDF file
document_name = "test3.pdf"
pdf_document = fitz.open(document_name)

# Initialize dictionaries for storing text and images
texts = {}
images = {}
img_counter = 0

for page_num, page in enumerate(pdf_document):
    # Extract text from the page
    texts[page_num] = page.get_text()

    for img in page.get_images():
        xref = img[0]
        pix = fitz.Pixmap(pdf_document, xref)
        img_name = f"image_{img_counter}.jpg"
        images[img_counter] = img_name

        if pix.n < 5:  # this is GRAY or RGB
            if not pix.colorspace.name in (fitz.csGRAY.name, fitz.csRGB.name):
                pix = fitz.Pixmap(fitz.csRGB, pix)
            pix.save(img_name, "png")
        else:  # CMYK: convert to RGB first
            pix1 = fitz.Pixmap(fitz.csRGB, pix)
            if not pix1.colorspace.name in (fitz.csGRAY.name, fitz.csRGB.name):
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
            pix1.save(img_name, "png")
            pix1 = None
        pix = None
        img_counter += 1  # increment the image counter after each image is processed


# Create a directory to store the extracted data
path = document_name+"_extracted_data"
if not os.path.exists(path):
    os.makedirs(path)

# Save the extracted text to files
for page_num in texts:
    with open(path + '/text_page_' + str(page_num) + '.txt', 'w') as f:
        f.write(texts[page_num])


# Use pytesseract to extract text from the images
image_texts = {}
for img_num in images:
    image_text = pytesseract.image_to_string(images[img_num])
    image_texts[img_num] = image_text
    with open(path + '/image_text_' + str(img_num) + '.txt', 'w') as f:
        f.write(image_text)



#CSVye yazmak icin formatladigimiz kisim :
data = []
for page_num in texts:
    for line in texts[page_num].split():
        data.extend([[page_num, "text", word] for word in line.split()])
    for img_num in images:
        if img_num in image_texts:
            for line in image_texts[img_num].split():
                data.extend([[img_num, "image", word] for word in line.split()])

testdata = []
for page_num in texts:
    for line in texts[page_num].split("\n"):
        testdata.append([page_num, "text", line])
        #testdata.extend([[page_num, "text", word] for word in line.split()])

for img_num in images:
    if img_num in image_texts:
        for line in image_texts[img_num].split("\n"):
            testdata.append([img_num, "image", line])
            print(str(img_num) + ". ben testdataya appendledim : " + line)
            #testdata.extend([[img_num, "image", word] for word in line.split("")])

# Write the data to a CSV file
with open(document_name+'_parsed_data.csv', 'w') as csv_file:
    fieldnames = ['source_number', 'source_type', 'data']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for index, row in enumerate(testdata):# data:(split()) / testdata:(split("\n")
        writer.writerow({'source_number': row[0], 'source_type': row[1], 'data': row[2]})