from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import smtplib
load_dotenv()


def admin_assign(ticket_id,user_name,email,question):
    sub= f"[Ticket Assigned] New Support Ticket #{ticket_id}"
    body = f"""
    Hello Support Team,

    A new support ticket has been assigned to you.

    Ticket ID   : {ticket_id}
    Customer    : {email}
    Assignment  : You have been assigned to handle this ticket.
    Question    : {question}

    Please take the necessary actions.

    Regards,
    Chatbot Support System
    """
    mail_(user_name,sub,body)
    return "OK"

def customer_support(ticket_id,user_name):
    sub= f"Your Ticket #{ticket_id} Has Been Assigned"
    body = f"""
        Hello {user_name},

        Your support ticket has been assigned to one of our human support specialists.

        Ticket ID   : {ticket_id}
        Status      : Assigned to Human Agent

        You will receive further updates once your issue is reviewed.

        Thank you for your patience.

        Best,
        Support Team
        """
    mail_(user_name,sub,body)
    return "OK"


def mail_(email_id,sub,body):
    msg1 = MIMEMultipart()
    GMAIL_USERMAIL = os.getenv("USERMAIL_")
    GMAIL_PASSWORD = os.getenv("PASSWORD_")
    msg1['Subject'] = sub
    sending_body = body
    # Add the email sending_body
    msg1.attach(MIMEText(sending_body, 'plain'))

    # Connect to the SMTP server (Gmail uses port 587)
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        # Login to your Gmail account
        server.login(GMAIL_USERMAIL, GMAIL_PASSWORD)

        # Send the email
        server.sendmail(GMAIL_USERMAIL, email_id, msg1.as_string())

