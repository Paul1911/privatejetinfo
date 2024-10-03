from config import config,maillist
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
from pretty_html_table import build_table

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.info("Main.py started")

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

def create_merge_df():
    columns = [
        'Departure Date',
        'Departure IATA',
        'Arrival IATA',
        'Departure ICAO',
        'Arrival ICAO',
        'Departure Airport',
        'Arrival Airport',
        'Airline',
        'Aircraft',
        'Departure Time',
        'Arrival Time',
        'Duration',
        'Distance',
        'Available Seats',
        'Price',
        'Comment'
    ]
    df=pd.DataFrame(columns=columns)
    return df

def get_data():
    errors = []
    df_AHO = pd.DataFrame()
    df_PVD = pd.DataFrame()
    df_ECA = pd.DataFrame()
    df_05 = pd.DataFrame()

    try:
        with scraper.AirHamburgScraper(user_AHO, user_pw_AHO, user_airline_AHO, user_empno) as AirHamburg:
            AirHamburg.login()
            html = AirHamburg.get_table_html()
            df_AHO = AirHamburg.html_to_df(html)
    except:
        errors.append("Air Hamburg failed")
    finally:
        pass
    
    try:
        with scraper.PadaviationScraper(user_PVD, user_pw_PVD, user_airline_PVD, user_empno) as PadAviation:
            PadAviation.login()
            df_PVD = PadAviation.html_to_df()
    except:
        errors.append("PadAviation failed")
    finally:
        pass

    try:
        with scraper.ExcellentAirScraper("", user_pw_ECA, "", "") as ExcellentAir:
            ExcellentAir.login()
            df_ECA = ExcellentAir.html_to_df()
    except:
        errors.append("ExcellentAir failed")
    finally:
        pass    

    try:
        with scraper.PlatoonAviationScraper(user_05, user_pw_05, user_airline_05, user_empno) as PlatoonAviation:
            PlatoonAviation.login()
            df_05 = PlatoonAviation.html_to_df()
    except:
        errors.append("Platoon Aviation failed")
    finally:
        pass    
    
    #try:
    #    with scraper.SilverCloudAir("",user_pw_SCR,"","") as SilverCloud:
    #        SilverCloud.login()
    #        df_silver = SilverCloud.html_to_df()
    #except:
    #3    errors.append("Silver Cloud Air failed")
    #finally:
    #    pass    

    return df_AHO, df_PVD, df_ECA, df_05, errors #, df_silver


if __name__ == "__main__":

    # data retrieval
    df_AHO, df_PVD, df_ECA, df_05, errors = get_data() #, df_silver
    logging.info("Data retrieval finished")
    logging.info(errors)

    #Create merge df    
    df=create_merge_df()

    # Big Merge
    df = pd.concat([df, df_AHO, df_PVD, df_ECA, df_05]) #, df_silver

    # Formatting 
    df['Departure IATA'] = df['Departure IATA'].fillna(df['Departure ICAO'])
    df['Arrival IATA'] = df['Arrival IATA'].fillna(df['Arrival ICAO'])
    df = df.rename(columns={'Departure IATA': 'Departure IATA/ICAO', 'Arrival IATA': 'Arrival IATA/ICAO'})
    df = df.sort_values(by=['Departure Date', 'Departure Time'])
    df = df.reset_index(drop=True)
    df = df.drop(["Distance","Departure ICAO","Arrival ICAO"], axis=1)
    df = df.fillna("")
    df = df.drop_duplicates()
    final_columns = [
        'Departure Date',
        'Departure IATA/ICAO',
        'Arrival IATA/ICAO',
        'Departure Airport',
        'Arrival Airport',
        'Airline',
        'Aircraft',
        'Departure Time',
        'Arrival Time',
        'Duration',
        'Available Seats',
        'Price',
        'Comment'
    ]
    df = df.reindex(columns=final_columns)
    df.to_csv("main.csv")
    df = pd.read_csv("main.csv").iloc[:,1:]
    print("main df:\n", df.head())
    logging.info("Main df formatting finished")

    
    # Mailing
    logging.info("Mailing started")
    email_sender = config['user_mail']
    email_password = config['user_password_mail']
    email_receiver = maillist
    subject = 'Privatejet Offers on ' + str(datetime.today().strftime('%d-%m-%Y'))
    
    
    html_table_blue_light = build_table(df, 'yellow_light', font_family='Open Sans, sans-serif', font_size='15px',
        width_dict=['60','55','55','130','130','110','80','55','55','55','55','70','100',],
        padding= '0px 0px 0px 2px'
        )
    html = """\
        <html>
        <head></head>
        <body>
            <h1>Currently Published Private Jet Positioning Flights:</h1>
            <div style="margin-bottom: 10px;">No guarantee is given for the accuracy of the data.
            Full information on the respective private jet airline web page, 
            which are accessible via MyIDTravel. 
            </div>

            {0}

            <h1>ExcellentAir Fares (incl. TAX and Fees)</h1>
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
            </ul>
            Attention: Prices vary dependent on language selection. Please inquire directly via their website to receive the correct price.

        </body>
        </html>
        """.format(html_table_blue_light)
    
    # HTML format testing
    html_testing = False
    if html_testing:
        f = open('testhtml.html', 'w')
        f.write(html)
        f.close()
        raise

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        for mailaddress in email_receiver:
            try:
                part1 = MIMEText(html, 'html')
                em = MIMEMultipart()
                em['From'] = email_sender
                em['Subject'] = subject
                em.attach(part1)
                em['To'] = mailaddress
                smtp.sendmail(email_sender, mailaddress, em.as_string())
                logging.info(f"Mail sent to {mailaddress}.")
            except Exception as e:
                print(e)
                logging.info(f"Mailing {mailaddress} did not work.")
            finally:
                pass

    logging.info("Mailing finished")
    logging.info("Program finished")
