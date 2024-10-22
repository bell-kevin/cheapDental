import pdfplumber
import pandas as pd
import requests

def download_pdf(url, local_filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(local_filename, 'wb') as f:
        f.write(response.content)

def extract_data_from_pdf(pdf_path):
    data = {}
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        code = parts[0]  # The dental code
                        price_str = parts[1]  # The price
                        # Check if the price_str is a valid price
                        try:
                            price = float(price_str.replace('$', '').replace(',', ''))
                            data[code] = price
                        except ValueError:
                            # If conversion fails, skip this line
                            continue
    return data

def compare_prices(pdf1_data, pdf2_data):
    comparison = []
    all_codes = set(pdf1_data.keys()).union(set(pdf2_data.keys()))
    
    for code in all_codes:
        price1 = pdf1_data.get(code, None)
        price2 = pdf2_data.get(code, None)
        
        if price1 is not None and price2 is not None:
            cheaper = 'PDF1' if price1 < price2 else 'PDF2' if price2 < price1 else 'Same Price'
            comparison.append((code, price1, price2, cheaper))
        elif price1 is not None:
            comparison.append((code, price1, 'N/A', 'PDF1 Only'))
        elif price2 is not None:
            comparison.append((code, 'N/A', price2, 'PDF2 Only'))
    
    return comparison

# URLs of the PDF files
pdf1_url = 'https://www.coastdental.com/wp-content/uploads/smileplusfeeschedule.pdf'
pdf2_url = 'https://ebusiness.ada.org/Assets/docs/85994.pdf'

# Local file paths to save the downloaded PDFs
pdf1_path = 'smileplusfeeschedule.pdf'
pdf2_path = 'ada_feeschedule.pdf'

# Download the PDFs
download_pdf(pdf1_url, pdf1_path)
download_pdf(pdf2_url, pdf2_path)

# Extract data from both PDFs
pdf1_data = extract_data_from_pdf(pdf1_path)
pdf2_data = extract_data_from_pdf(pdf2_path)

# Compare prices
price_comparison = compare_prices(pdf1_data, pdf2_data)

# Convert to DataFrame for better visualization
comparison_df = pd.DataFrame(price_comparison, columns=['Code', 'PDF1 Price', 'PDF2 Price', 'Cheaper'])
print(comparison_df)

# Optionally, save the comparison to a CSV file
comparison_df.to_csv('price_comparison.csv', index=False)
