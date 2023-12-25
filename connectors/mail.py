import imaplib
import email
import json
from datetime import datetime
from bs4 import BeautifulSoup  # Import Beautiful Soup

def fetch_emails_from_today(username, password, server, port=993):
    """
    Fetches the last emails from each mail chain for the current day from the "[Gmail]/All Mail" folder.
    
    This function connects to an IMAP server and searches the "[Gmail]/All Mail" folder for emails received today.
    It identifies the last email in each mail chain by checking if the message ID of an email appears in the 
    'References' or 'In-Reply-To' fields of other emails. If it doesn't, the email is considered the last in its thread.
    The function extracts and processes both HTML and plain text parts of the email. For HTML emails, the text is 
    extracted using Beautiful Soup, while plain text emails are used as-is. Line breaks in the text are replaced with 
    spaces to maintain a single-line format for each email's content.

    Parameters:
    username (str): The username for the email account.
    password (str): The password for the email account.
    server (str): The IMAP server address.
    port (int, optional): The port number for the IMAP server. Defaults to 993.

    Returns:
    str: A string representation of the latest email from each conversation for the current day. 
         The string is formatted with fields for the message ID, sender, recipients (To, Cc), subject, 
         date sent, and email content.
    """
    email_data = ""

    try:
        # Connect to the IMAP server
        mail = imaplib.IMAP4_SSL(server, port)
        mail.login(username, password)

        # Select the "[Gmail]/All Mail" folder
        result, _ = mail.select('"[Gmail]/All Mail"', readonly=True)
        if result != 'OK':
            return "Failed to select the [Gmail]/All Mail folder."

        # Get today's date in the format required for IMAP
        today = datetime.now().strftime("%d-%b-%Y")

        # Search for emails from today in the "[Gmail]/All Mail" folder
        result, data = mail.search(None, '(SENTSINCE {date})'.format(date=today))
        if result != 'OK':
            return "No messages found for today in [Gmail]/All Mail."

        emails = {}
        referenced_ids = set()

        for num in data[0].split():
            result, data = mail.fetch(num, "(RFC822)")
            if result != 'OK':
                continue

            # Parse the email content
            msg = email.message_from_bytes(data[0][1])
            message_id = msg.get("Message-ID")
            emails[message_id] = msg

            # Collect all referenced message IDs
            references = msg.get("References", "") or msg.get("In-Reply-To", "")
            referenced_ids.update(references.split())

        # Filter to get only last emails in each chain
        for message_id, msg in emails.items():
            if message_id in referenced_ids:
                continue  # This email is referenced by another, so it's not the last in the chain

            # Extracting details
            from_ = msg.get("From").replace(',', ';')
            to = msg.get("To", "").replace(',', ';')
            cc = msg.get("Cc", "").replace(',', ';')
            subject = msg.get("Subject").replace(',', ';')
            date_sent = msg.get("Date").replace(',', ';')
            content = ""

            for part in msg.walk():
                if part.is_multipart():
                    continue

                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    charset = part.get_content_charset()
                    payload = part.get_payload(decode=True)
                    try:
                        text = payload.decode(charset) if charset is not None else payload.decode('ISO-8859-1')
                    except UnicodeDecodeError:
                        text = payload.decode('ISO-8859-1', errors='replace')
                    content += text.replace('\n', ' ').replace('\r', '')  # Replacing line breaks
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    html = part.get_payload(decode=True)
                    soup = BeautifulSoup(html, "html.parser")
                    text = soup.get_text(separator=' ', strip=True)
                    content += text

            email_data += f'ID="{message_id}"\nFROM="{from_}"\nTO="{to}"\nCC="{cc}"\nSUBJECT="{subject}"\nDATE="{date_sent}"\nCONTENT="{content}"\n\n\n'

        mail.close()
        mail.logout()
        return email_data

    except Exception as e:
        return str(e)
