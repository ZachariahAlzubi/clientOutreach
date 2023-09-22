import csv
import pandas as pd

import logging
import random
import re
import time

from outreach.search import google_search_with_timeout
from outreach.scraping import scrape_website_with_timeout
from outreach.cleaning import clean_email, clean_business_name

# Proxy settings
username = 'user-splx70gleh-country-us'
password = 'h4ui90lsvyZOS2chAr'
proxy = f"socks5h://{username}:{password}@gate.smartproxy.com:7000"
proxies = {
    'http': proxy,
    'https': proxy
}

# Load the xls file
df = pd.read_excel('list_data.xlsx')

# Set up logging
logging.basicConfig(filename='scraping_errors.log', level=logging.ERROR)

# Define a function to generate email guesses
def guess_emails(business_name):
    # Remove non-alphanumeric characters
    clean_name = re.sub(r'\W+', '', business_name)
    return f'{clean_name}@gmail.com, info@{clean_name}.com'

# Prompt the user for the number of links to process
num_links = int(input("Enter the number of links to process: "))

# Iterate over the DataFrame
for index, row in df.head(num_links).iterrows():
    start_time = time.time()
    print(f"Processing link {index+1} of {num_links}...")
    link = google_search_with_timeout(row)
    if link is None:  # Skip this row if google_search took too long
        continue
    print(f"Found link: {link} (Time taken: {time.time() - start_time} seconds)")
    df.loc[index, 'Link'] = link
    start_time = time.time()
    contact_info = scrape_website_with_timeout(link)
    if contact_info is None:  # Skip this row if scrape_website took too long
        continue
    print(f"Found contact info: {contact_info} (Time taken: {time.time() - start_time} seconds)")
    email_matches = ', '.join(contact_info[0]) if contact_info[0] else guess_emails(row['Legal Business Name'])
    df.loc[index, 'Emails'] = email_matches
    df.loc[index, 'Phone Numbers'] = ', '.join(contact_info[1]) if contact_info[1] else ''
    df.loc[index, 'Contact Form Link'] = contact_info[2] if contact_info[2] else ''
    time.sleep(random.uniform(1, 3))

# Save the DataFrame back to an xls file
df.to_excel('schoolInfo.xlsx', index=False)
print("Done!")

# Read the excel file
df = pd.read_excel('first5000.xlsx')

# Apply clean_business_name function to the 'Legal Business Name' column
df['Legal Business Name'] = df['Legal Business Name'].apply(clean_business_name)

# Iterate over the rows of the dataframe
for i, row in df.iterrows():
    # If Emails is empty, fill with guessed emails
    if pd.isnull(row['Emails']):
        business_name = row['Legal Business Name']
        guessed_emails = f"{business_name}@gmail.com, info@{business_name}.com"
        df.loc[i, 'Emails'] = guessed_emails
    else:
        # Check for duplicate emails
        email_list = row['Emails'].split(", ")
        # Remove duplicates by converting the list to a set, then convert back to list
        email_list = list(set(email_list))
        # Join the emails back into a string, separated by commas
        email_str = ", ".join(email_list)
        # Replace the email cell with the cleaned emails
        df.loc[i, 'Emails'] = email_str

# Create a copy of the dataframe
df_cleaned = df.copy()

# Apply clean_email function to 'Emails' column
df_cleaned['Emails'] = df_cleaned['Emails'].apply(clean_email)

# Save the cleaned dataframe to a new excel file
df_cleaned.to_excel('cleanedEmails5000.xlsx', index=False)

# Load the Excel file
df = pd.read_excel('cleanedEmails5000.xlsx')

# Select the third column. Note that Python uses 0-indexing, so the third column would be index 2.
third_column = df.iloc[:, 2]

# Save the third column to a CSV file
third_column.to_csv('third_column.csv', index=False)

# Open the input and output files
with open('third_column.csv', 'r') as infile, open('output.csv', 'w', newline='') as outfile:
    # Create a CSV writer for the output file
    writer = csv.writer(outfile)

    # Read the input file line by line
    for line in infile:
        # Split the line into emails
        emails = line.strip().split(',')

        # Write each email to the output file
        for email in emails:
            writer.writerow([email.strip()])  # strip() is used to remove leading/trailing whitespace

# Regular expression pattern for matching email addresses
pattern = re.compile(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')

# Open the input and output files
with open('output.csv', 'r') as infile, open('cleaned_output.csv', 'w', newline='') as outfile:
    # Create a CSV writer for the output file
    writer = csv.writer(outfile)

    # Read the input file line by line
    for line in infile:
        # Remove quotes
        line = line.replace('"', '')

        # Find the email address in the line
        match = pattern.search(line)

        # If an email address was found, write it to the output file
        if match:
            writer.writerow([match.group(1)])

        
