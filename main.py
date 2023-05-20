from config import config
import scraper 
import logging
logging.basicConfig(level=logging.INFO)
from email.message import EmailMessage
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

user = config['user_02']
user_pw = config['user_password_02']
user_airline = config['user_airline_02']
user_empno = config['user_empno']


if __name__ == "__main__":

    with scraper.AirHamburgScraper(user, user_pw, user_airline, user_empno) as AirHamburg:
        AirHamburg.login()
        html = AirHamburg.get_table_html()
        df = AirHamburg.html_to_df(html)
    print(df)

    email_sender = config['user_mail']
    email_password = config['user_password_mail']
    email_receiver = ''
    subject = 'testsubject'
    

    html = """\
        <html>
        <head></head>
        <body>
            {0}
        </body>
        </html>
        """.format(df.to_html())
    part1 = MIMEText(html, 'html')

    em = MIMEMultipart()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    #em.set_content(body)
    em.attach(part1)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
