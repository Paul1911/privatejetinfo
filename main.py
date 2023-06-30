from config import config
import scraper 
import logging
import pandas as pd
import random
from datetime import datetime
from email.message import EmailMessage
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO)

user_empno = random.randint(35000, 50000)

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

    '''with scraper.AirHamburgScraper(user_AHO, user_pw_AHO, user_airline_AHO, user_empno) as AirHamburg:
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

    # Big Merge
    for df in [df, df_AHO, df_PVD, df_ECA, df_05, df_silver]:
        print(df.dtypes)
    df = pd.concat([df, df_AHO, df_PVD, df_ECA, df_05, df_silver])#, ignore_index=True)

    # Formatting 
    df['Departure IATA'] = df['Departure IATA'].fillna(df['Departure ICAO'])
    df['Arrival IATA'] = df['Arrival IATA'].fillna(df['Arrival ICAO'])
    df = df.rename(columns={'Departure IATA': 'Departure IATA/ICAO', 'Arrival IATA': 'Arrival IATA/ICAO'})
    df = df.sort_values(by='Departure Date')
    df = df.reset_index(drop=True)
    df = df.drop(["Distance","Departure ICAO","Arrival ICAO"], axis=1)
    df = df.fillna("")
    df.to_csv("main.csv")
    print(df)'''
    df = pd.read_csv("main.csv")
    

    email_sender = config['user_mail']
    email_password = config['user_password_mail']
    email_receiver = ''
    subject = 'Privatejet Offers on ' + str(datetime.today().strftime('%d-%m-%Y'))
    
    from pretty_html_table import build_table
    html_table_blue_light = build_table(df, 'yellow_light', font_family='Open Sans, sans-serif')
    html = """\
        <html>
        <head></head>
        <body>
            <h1>Currently published Private Jet Positioning flights:</h1>
            <div style="margin-bottom: 10px;">No guarantee for data correctness. 
            Full information on the respective privatejet airline web page, 
            which are accessible via MyIDTravel. 
            If you see any errors or wrong figures, please message paul.friedrich@gmx.net.</div>

            {0}

            <h1>Excellentair Fares (incl. TAX and Fees)</h1>
            <h4>See MyIDTravel for latest price information.</h4>
            <ul>
                <li><strong>Germany:</strong> € 39,00</li>
                <li><strong>Europa:</strong> € 49,00</li>
                <li><strong>North Africa / Canaries:</strong> € 59,00</li>
            </ul>
            <h1>Silver Cloud Air Fares</h1>
            <h4>See MyIDTravel for latest price information.</h4>
            <ul>
                <li><strong>Flights within Germany:</strong> € 100</li>
                <li><strong>Flights within the EU (incl. Switzerland and UK):</strong> € 250</li>
                <li><strong>Attention: Prices vary dependent on language selection. Please inquire directly via their website to receive the correct price.</strong></li>
            </ul>

        </body>
        </html>
        """.format(html_table_blue_light)
    
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
