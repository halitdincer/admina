import imaplib
import email
import csv
import json
from datetime import datetime


def fetch_emails_from_today(username, password, server, port=993):
    email_data = "Sender,Subject,Date Sent,Email Content\n"  # CSV header

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

        for num in data[0].split():
            result, data = mail.fetch(num, "(RFC822)")
            if result != 'OK':
                continue

            # Parse the email content
            msg = email.message_from_bytes(data[0][1])

            # Extracting details from the header
            from_ = msg.get("From").replace(',', ';')  # Replace commas to preserve CSV format
            subject = msg.get("Subject").replace(',', ';')
            date_sent = msg.get("Date").replace(',', ';')
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

            # Concatenate the email details into the string
            email_data += f'"{from_}","{subject}","{date_sent}","{content}"\n'

        mail.close()
        mail.logout()
        return email_data

    except Exception as e:
        return str(e)

# Load the JSON data from the file
with open('../config.json', 'r') as file:
    config = json.load(file)

    result = fetch_emails_from_today(config["MAIL_ADDRESS"], config["MAIL_PASSWORD"], config["MAIL_SERVER"], file_path='emails_today.txt')
    print(result)

