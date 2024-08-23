import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv(override=True)


def send_urgent_email(subject, body, to_email):
    """
    Sends an urgent email to the specified recipient.

    This function sends an email using the Outlook SMTP server. It retrieves the sender's
    email address and password from environment variables and constructs an email with
    the provided subject and body. The email is then sent to the specified recipient.

    Parameters:
    -----------
    subject : str
        The subject line of the email.

    body : str
        The body content of the email.

    to_email : str
        The recipient's email address.

    Environment Variables:
    ----------------------
    from_email : str
        The sender's email address, retrieved from an environment variable.

    email_password : str
        The password for the sender's email account, retrieved from an environment variable.

    Logs:
    -----
    - Logs a success message to the console if the email is sent successfully.
    - Logs an error message to the console if sending the email fails.

    Raises:
    -------
    Exception:
        If an error occurs during the email sending process, it is caught and logged.

    Example Usage:
    --------------
    send_urgent_email("Data Quality Alert", "High percentage of missing values detected.", "data.engineer@example.com")
    """

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
