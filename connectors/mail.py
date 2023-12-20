import imaplib
import email
import csv
import json
from datetime import datetime



def fetch_emails_from_today_csv(username, password, server, port=993, file_path='emails_today.csv'):
    try:
        # Connect to the IMAP server
        mail = imaplib.IMAP4_SSL(server, port)
        mail.login(username, password)

        # Select the inbox
        mail.select("inbox")

        # Get today's date in the format required for IMAP
        today = datetime.now().strftime("%d-%b-%Y")

        # Search for emails from today
        result, data = mail.search(None, '(SENTSINCE {date})'.format(date=today))
        if result != 'OK':
            return "No messages found for today!"

        # Open the file to write emails
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Writing the headers
            writer.writerow(["Sender", "Subject", "Date Sent", "Email Content"])

            for num in data[0].split():
                result, data = mail.fetch(num, "(RFC822)")
                if result != 'OK':
                    continue

                # Parse the email content
                msg = email.message_from_bytes(data[0][1])

                # Extracting details from the header
                from_ = msg.get("From")
                subject = msg.get("Subject")
                date_sent = msg.get("Date")
                content = ""

                for part in msg.walk():
                    # If part is multipart, continue
                    if part.is_multipart():
                        continue

                    # Get the content type
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    # If part is text/plain or text/html
                    if content_type in ("text/plain", "text/html") and "attachment" not in content_disposition:
                        charset = part.get_content_charset()
                        payload = part.get_payload(decode=True)
                        
                        # Decode payload with detected charset or fall back to ISO-8859-1
                        try:
                            if charset is not None:
                                content += payload.decode(charset)
                            else:
                                content += payload.decode('ISO-8859-1')
                        except UnicodeDecodeError:
                            content += payload.decode('ISO-8859-1', errors='replace')

                # Write the email details as a row in the CSV file
                writer.writerow([from_, subject, date_sent, content])

        mail.close()
        mail.logout()
        return "Emails from today have been written to " + file_path

    except Exception as e:
        return str(e)

# Load the JSON data from the file
with open('../config.json', 'r') as file:
    config = json.load(file)

# Usage example (replace with your details and desired file path)
result = fetch_emails_from_today_csv(config["MAIL_ADDRESS"], config["MAIL_PASSWORD"], config["MAIL_SERVER"], file_path='emails_today.txt')
print(result)

