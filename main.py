from config import config
import scraper 
import logging
logging.basicConfig(level=logging.INFO)

user = config['user_02']
user_pw = config['user_password_02']
user_airline = config['user_airline_02']
user_empno = config['user_empno_02']


if __name__ == "__main__":

    with scraper.AirHamburgScraper(user, user_pw, user_airline, user_empno) as AirHamburg:
        AirHamburg.login()
        html = AirHamburg.get_table_html()
        df = AirHamburg.html_to_df(html)
        print(df)