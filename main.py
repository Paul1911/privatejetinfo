from config import config, admin
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
import yaml

with open("maillist.yaml", "r") as file:
        maillist = yaml.safe_load(file)

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
    df_AHO, df_PVD, df_ECA, df_05, error_messages = get_data() #, df_silver
    logging.info("Data retrieval finished")
    logging.info(f"------------------------------- Following data retrievals ran into an error: -------------------------------\n{error_messages}")

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
    df["Route"] = df['Departure IATA/ICAO'] + "-" + df['Arrival IATA/ICAO']
    df["Airline|AC"] = df['Airline'] + " | " + df['Aircraft']
    final_columns = [
        'Departure Date',
        'Departure IATA/ICAO',
        'Arrival IATA/ICAO',
        'Route',
        'Departure Airport',
        'Arrival Airport',
        #'Airline',
        #'Aircraft',
        "Airline|AC",
        'Departure Time',
        'Arrival Time',
        'Duration',
        'Available Seats',
        'Price',
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
    subject = 'Private Jet Offers on ' + str(datetime.today().strftime('%d-%m-%Y'))

    context = ssl.create_default_context()

    # Number formatting for final table
    formatters ={'Available Seats': lambda x: f'{int(x)}'}
    
    for mailaddress, cfg in email_receiver.items():

        # Get Configs from maillist
        all_flights = cfg['all_flights']

        special_flights = cfg['special_flights']
        spec_flts_dep_ap = special_flights['dep_airports'] if special_flights['dep_airports'] is not None else []
        spec_flts_arr_ap = special_flights['arr_airports'] if special_flights['arr_airports'] is not None else []
        spec_flts_routes = special_flights['routes'] if special_flights['routes'] is not None else []

        alarm_flights = cfg['alarm_flights']
        alarm_flts_dep_ap = alarm_flights['dep_airports'] if alarm_flights['dep_airports'] is not None else []
        alarm_flts_arr_ap = alarm_flights['arr_airports'] if alarm_flights['arr_airports'] is not None else []
        alarm_flts_routes = alarm_flights['routes'] if alarm_flights['routes'] is not None else []

        # Filter data frame for configs and convert to HTML tables
        
        html_table_all_flights = ""
        html_table_special_flights = "No flights for you this time. Life's hard, right?"
        html_table_alarm_flights = ""

        # Special Flights
        table_special_flights = df[
            df['Route'].isin(spec_flts_routes)|
            df['Departure IATA/ICAO'].isin(spec_flts_dep_ap)|
            df['Arrival IATA/ICAO'].isin(spec_flts_arr_ap)|
            df['Route'].isin(alarm_flts_routes)|
            df['Departure IATA/ICAO'].isin(alarm_flts_dep_ap)|
            df['Arrival IATA/ICAO'].isin(alarm_flts_arr_ap)
            ].drop("Route", axis=1)
        html_table_special_flights = table_special_flights.to_html(
            index=False, 
            classes='table table-striped', 
            border=0, na_rep="",  # Replace NaN with an empty string
            )
        
        # Alarm flights
        alarm_conditions = (
            df['Route'].isin(alarm_flts_routes) |
            df['Departure IATA/ICAO'].isin(alarm_flts_dep_ap) |
            df['Arrival IATA/ICAO'].isin(alarm_flts_arr_ap)
        )
        alarm = True if df[alarm_conditions].shape[0] > 0 else False

        # All flights
        if all_flights:
            df_all_flights = df.drop("Route", axis=1)
            html_table_all_flights = df_all_flights.to_html(
                index=False, 
                classes='table table-striped', 
                formatters = formatters,
                border=0, na_rep="",  # Replace NaN with an empty string
            )

        html_content = f"""
            <html>
            <head>
                <style>
                    .table {{ border-collapse: collapse; width: 100%; }}
                    .table td, .table th {{ border: 1px solid #ddd; padding: 8px; }}
                    .table th {{ padding-top: 12px; padding-bottom: 12px; text-align: left; background-color: #f4f4f4; }}
                </style>
            </head>
            <body>
                <h1>Currently Published Private Jet Positioning Flights:</h1>
                <div style="margin-bottom: 10px;">No guarantee is given for the accuracy of the data.
                Full information on the respective private jet airline web page, 
                which are accessible via MyIDTravel. 

                <p> If this newsletter helped you find a privat jet to try, maybe consider donating 3 EUR to <a href="https://www.dkms.de/aktiv-werden/geld-spenden" target="_blank">Deutsche Knochenmarkspende</a> 
                or 3 CHF to <a href="https://www.blutstammzellspende.ch/de/Geld-spenden/geld-spenden" target="_blank">Blutstammzellspende</a>. Also, tell me about it, makes the developer happy ;)!


                <h2>Published Private Jet Flights on your preferred Routes:</h2>
                </div>

                {html_table_special_flights}

                <div style="margin-bottom: 10px;">
                <h2>All Currently Published Private Jet Flights:</h2>
                </div>

                {html_table_all_flights}

                <h3>ExcellentAir Fares (incl. TAX and Fees)</h3>
                <h4>See MyIDTravel for latest price information.</h4>
                <ul>
                    <li><strong>Germany:</strong> € 39,00</li>
                    <li><strong>Europa:</strong> € 49,00</li>
                    <li><strong>North Africa / Canaries:</strong> € 59,00</li>
                </ul>
                <h3>Silver Cloud Air Fares</h3>
                <h4>See MyIDTravel for latest price information.</h4>
                <ul>
                    <li><strong>Flights within Germany:</strong> € 100</li>
                    <li><strong>Flights within the EU (incl. Switzerland and UK):</strong> € 250</li>
                </ul>
                Attention: Prices vary dependent on language selection. Please inquire directly via their website to receive the correct price.
            </body>
            </html>
            """
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            try:
                em = MIMEMultipart()
                if alarm:
                    # Set priority to high
                    em['X-Priority'] = '1' 
                    em['X-MSMail-Priority'] = 'High'
                    subject = "PRIVATE JET ALARM - Availability for your Alarm Airports"
                em['From'] = email_sender
                em['Subject'] = subject
                em['To'] = mailaddress
                em.attach(MIMEText(html_content, 'html'))
                smtp.sendmail(email_sender, mailaddress, em.as_string())
                logging.info(f"Mail sent to {mailaddress}.")
            except Exception as e:
                print(e)
                logging.info(f"Mailing {mailaddress} did not work.")
            finally:
                pass


    # Error message
    if error_messages:
        html = f"""{error_messages}"""
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            for mailaddress in admin:
                try:
                    part1 = MIMEText(html, 'html')
                    em = MIMEMultipart()
                    em['From'] = email_sender
                    em['Subject'] = "PrivateJet Exceptions"
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