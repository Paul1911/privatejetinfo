from email.message import EmailMessage
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from config import config
import yaml
import logging 

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

with open("maillist.yaml", "r") as file:
        maillist = yaml.safe_load(file)

email_sender = config['user_mail']
email_password = config['user_password_mail']
email_receiver = maillist
subject = "Update Info for your Private Jet Newsletter"

context = ssl.create_default_context()

with open("send_mail.html", "r", encoding="utf-8") as file:
    html = file.read()

with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(email_sender, email_password)

    for mailaddress, cfg in email_receiver.items():
        #try:
        em = MIMEMultipart()
        em['From'] = email_sender
        em['Subject'] = subject
        em['To'] = mailaddress
        em.attach(MIMEText(html, 'html'))
        smtp.sendmail(email_sender, mailaddress, em.as_string())
        logging.info(f"Mail sent to {mailaddress}.")
        #except Exception as e:
        #    print(e)
        #    logging.info(f"Mailing {mailaddress} did not work.")
        #finally:
        #    pass