from config import config
import scraper 
import logging
import pandas as pd
from email.message import EmailMessage
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO)

user_empno = config['user_empno']

# Air Hamburg AHO
user_AHO = config['user_AHO']
user_pw_AHO = config['user_password_AHO']
user_airline_AHO = config['user_airline_AHO']

# PadAviation PVD
user_PVD = config['user_PVD']
user_pw_PVD = config['user_password_PVD']
user_airline_PVD = config['user_airline_PVD']

# ExcellentAir ECA
user_pw_ECA = config['user_password_ECA']

# Platoon Aviation 05
user_05 = config['user_05']
user_pw_05 = config['user_password_05']
user_airline_05 = config['user_airline_05']

# Silver Cloud Air SCR
user_pw_SCR = config['user_password_SCR']

if __name__ == "__main__":

    with scraper.AirHamburgScraper(user_AHO, user_pw_AHO, user_airline_AHO, user_empno) as AirHamburg:
        AirHamburg.login()
        html = AirHamburg.get_table_html()
        df_AHO = AirHamburg.html_to_df(html)

    with scraper.PadaviationScraper(user_PVD, user_pw_PVD, user_airline_PVD, user_empno) as PadAviation:
        PadAviation.login()
        df_PVD = PadAviation.html_to_df()

    with scraper.ExcellentAirScraper("", user_pw_ECA, "", "") as ExcellentAir:
        ExcellentAir.login()
        df_ECA = ExcellentAir.html_to_df()

    with scraper.PlatoonAviationScraper(user_05, user_pw_05, user_airline_05, user_empno) as PlatoonAviation:
        PlatoonAviation.login()
        df_05 = PlatoonAviation.html_to_df()

    with scraper.SilverCloudAir("",user_pw_SCR,"","") as SilverCloud:
        SilverCloud.login()
        df_silver = SilverCloud.html_to_df()

    print(df_AHO.columns, df_PVD.columns, df_ECA.columns, df_05.columns, df_silver.columns)

    # Create merge df
    columns = [
    'Departure Date',
    'Departure IATA',
    'Arrival IATA',
    'Departure ICAO',
    'Arrival ICAO',
    'Departure Airport',
    'Arrival Airport',
    'Airline',
    'Aircraft Type',
    'Departure Time',
    'Arrival Time',
    'Duration',
    'Distance',
    'Available Seats',
    'Price',
    'Comment'
    ]
    df=pd.DataFrame(columns=columns)
    print(df)
    raise

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
        """.format(df_05.to_html())
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
        logging.info("Mail sent")
