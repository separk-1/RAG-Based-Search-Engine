import os
import requests
from bs4 import BeautifulSoup

# Base URL for NUREG-0800, Chapter 5
base_url = "https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr0800/ch5/index.html"
base_download_url = "https://www.nrc.gov"

# Create a folder for the section files if it doesn't exist
root_dir = "NUREG0800_Chapter5"
if not os.path.exists(root_dir):
    os.makedirs(root_dir)

# Function to download the PDF
def download_pdf(section_folder, link, pdf_name):
    response = requests.get(link)
    pdf_path = os.path.join(section_folder, pdf_name)
    with open(pdf_path, 'wb') as pdf_file:
        pdf_file.write(response.content)
    print(f"Downloaded {pdf_name} in {section_folder}")

# Parse the webpage
response = requests.get(base_url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the section table
table_rows = soup.find_all('tr')

# Iterate through the rows to process each section
for row in table_rows:
    cells = row.find_all('td')
    if len(cells) > 0:
        section = cells[0].text.strip()  # Section name
        title = cells[1].text.strip()  # Title

        # Create a folder for each section
        section_folder = os.path.join(root_dir, section)
        if not os.path.exists(section_folder):
            os.makedirs(section_folder)

        # Get only the first PDF link in the 'Rev.' column (the latest one)
        rev_link = cells[2].find('a')
        if rev_link:
            pdf_url = base_download_url + rev_link['href']
            pdf_name = rev_link.text.strip() + ".pdf"
            # Download the latest PDF into the corresponding section folder
            download_pdf(section_folder, pdf_url, pdf_name)
