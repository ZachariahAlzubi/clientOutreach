import re


# Function to clean the business name
def clean_business_name(business_name):
    if isinstance(business_name, str):
        # Convert to lower case, remove spaces and special characters
        business_name = re.sub(r'\W+', '', business_name).lower()
    else:
        business_name = ''
    return business_name

# Function to clean the email
def clean_email(email):
    # Split by comma in case of multiple emails
    emails = email.split(", ")
    cleaned_emails = []
    for email in emails:
        # Find the first occurrence of a letter and the last occurrence of a period
        match = re.search(r'[a-zA-Z].*?\.[a-zA-Z]+', email)
        if match:
            # If a match is found, extract it and add to cleaned_emails
            cleaned_emails.append(match.group())
    # Join cleaned_emails into a string, separated by commas
    cleaned_email_str = ", ".join(cleaned_emails)
    return cleaned_email_str