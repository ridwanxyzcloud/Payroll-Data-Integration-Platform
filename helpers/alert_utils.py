import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv(override=True)

def send_urgent_email(subject, body, to_email):
    """Send an urgent email to the data engineer."""
    from_email = os.getenv("from_email")
    password = os.getenv("email_password")

    # Set up the server for Outlook
    smtp_server = 'smtp.office365.com'
    smtp_port = 587

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        print(f"Urgent email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")


# Test
if __name__ == "__main__":
    send_urgent_email("clouds", "Test Body", "ridwanclouds@gmail.com")