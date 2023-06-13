import fitz
import os
import pytesseract
import csv


pytesseract.pytesseract.tesseract_cmd = r'Teserract\tesseract.exe'

# Open the PDF file
document_folder = "PDFs/"
document_name = "BULUT Logistics.pdf"
document_path = document_folder+document_name
csv_suffix = "_parsed_data"

output_folder = "extracted/"
output_suffix = "_extracted_data"
output_text_suffix = "/text_page_"
output_image_suffix = "/image_text_"
pdf_document = fitz.open(document_path)
# Initialize dictionaries for storing text and images
texts = {}
images = {}
img_counter = 0

for page_num, page in enumerate(pdf_document):
    # Extract text from the page

    texts[page_num] = page.get_text(sort=True)
    print("get_text ("+str(page_num)+") : " + texts[page_num])

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
path = output_folder + document_path + output_suffix
if not os.path.exists(path):
    os.makedirs(path)

# Save the extracted text to files
for page_num in texts:
    with open(path + output_text_suffix + str(page_num) + '.txt', 'w') as f:
        f.write(texts[page_num])

# Use pytesseract to extract text from the images
image_texts = {}
for img_num in images:
    image_text = pytesseract.image_to_string(images[img_num])
    image_texts[img_num] = image_text
    with open(path + output_image_suffix + str(img_num) + '.txt', 'w') as f:
        f.write(image_text)

# Create a list to store all the data
data = []

# Append text data to the list
for page_num in texts:
    for line in texts[page_num].split("\n"):
        data.append([page_num, "text", line])

# Append image data to the list, in between text data
for img_num in images:
    if img_num in image_texts:
        for line in image_texts[img_num].split("\n"):
            data.append([img_num, "image", line])

# Write the data to a CSV file
with open(output_folder + document_path + csv_suffix + '.csv', 'w') as csv_file:
    fieldnames = ['source_number', 'source_type', 'data']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for index, row in enumerate(data):
        writer.writerow({'source_number': row[0], 'source_type': row[1], 'data': row[2]})