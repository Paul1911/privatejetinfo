import selenium 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions 
import time
import pandas as pd
from config import config
from bs4 import BeautifulSoup
import logging
logging.basicConfig(level=logging.INFO)

user = config['user_02']
user_pw = config['user_password_02']
user_airline = config['user_airline_02']
user_empno = config['user_empno_02']

def get_table_html():
    with webdriver.Firefox() as driver:
        driver.get("https://www.air-hamburg.de/de/login")
        #cookie_decline_button = WebDriverWait(driver, 10).until(
        #    expected_conditions.element_to_be_clickable((By.CLASS_NAME, "cc-deny"))
        #)
        time.sleep(1)
        cookie_decline_button = driver.find_element(By.CLASS_NAME, "cc-deny")
        cookie_decline_button.click()

        # Send user information
        #id_box = driver.find_element(By.ID,"username")
        id_box = WebDriverWait(driver, 10).until(
            expected_conditions.visibility_of_element_located((By.ID, "username"))
        )
        id_box.send_keys(user)
        # Send password information
        pass_box = driver.find_element(By.NAME, "password")
        pass_box.send_keys(user_pw)# Find login button
        # Click login
        login_button = driver.find_element(By.CLASS_NAME,"btn-primary")
        login_button.click()
        driver.get("https://www.air-hamburg.de/de/idtravel")
        accept_continue_button = driver.find_element(By.CLASS_NAME,"uk-button-primary")
        accept_continue_button.click()

        time.sleep(2)
        airline_box = driver.find_element(By.ID,"employee.fieldset[0].fields.em_airline")
        select = Select(airline_box)
        select.select_by_value(user_airline)
        emp_id_box = driver.find_element(By.CLASS_NAME,"field-text")
        emp_id_box.send_keys(user_empno)
        emp_ret_button = driver.find_element(By.CSS_SELECTOR, 'button[data-bind*="_onClick"]')
        emp_ret_button.click()
        next_button = driver.find_element(By.CLASS_NAME,"uk-button-primary")
        driver.execute_script("window.scrollBy(0, 1000);")
        next_button.click()

        # Parse the HTML code with BeautifulSoup
        logging.info("get html source code starts")
        html = driver.page_source
        logging.info("get html source code finished")
        driver.close()
        logging.info("driver closed")
    return html

def html_to_df(html):
    logging.info("html_to_df started")
    # Parse the HTML code with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    flight_list = soup.find_all("ul", class_="flights-list")

    # Find all the flight items directly from the flight_list
    flight_items = []
    for flight in flight_list:
        flight_items.extend(flight.find_all('li'))
    logging.info("html preparsing finished")

    # Create an empty dictionary to store the data
    data = {
        'Airline': [],
        'Aircraft Type': [],
        'Seats': [],
        'Departure Code': [],
        'Departure Airport': [],
        'Departure Time': [],
        'Duration': [],
        'Distance': [],
        'Arrival Code': [],
        'Arrival Airport': [],
        'Arrival Time': [],
        'Base Price': []
    }
    # Extract data from each flight item
    for flight_item in flight_items:

        # Add airline
        data['Airline'] = "Air Hamburg (02)"

        # Extract departure information
        departure_div = flight_item.find('div', {'class': 'departure'})
        departure_code = departure_div.find('h4').text.strip()
        data['Departure Code'].append(departure_code if departure_code else '')
        departure_airport = departure_div.find_all('span')[0].text.strip()
        data['Departure Airport'].append(departure_airport if departure_airport else '')
        departure_time = departure_div.find_all('span')[1].text.strip()
        data['Departure Time'].append(departure_time if departure_time else '')

        # Extract flight info
        aircraft_type = flight_item.find_all('span')[0].text.strip().split(":")[1]
        data['Aircraft Type'].append(aircraft_type if aircraft_type else '')
        seats = flight_item.find_all('span')[1].text.strip().split(" ")[1]
        data['Seats'].append(seats if seats else '')
        duration = flight_item.find('span', {'class': 'durationinfo'}).text.strip().split("/")[0]
        data['Duration'].append(duration if duration else '')
        distance = flight_item.find('span', {'class': 'durationinfo'}).text.strip().split("/")[1]
        data['Distance'].append(distance if distance else '')

        # Extract arrival information
        arrival_div = flight_item.find('div', {'class': 'arrival'})
        arrival_code = arrival_div.find('h4').text.strip()
        data['Arrival Code'].append(arrival_code if arrival_code else '')
        arrival_airport = arrival_div.find_all('span')[0].text.strip()
        data['Arrival Airport'].append(arrival_airport if arrival_airport else '')
        arrival_time = arrival_div.find_all('span')[1].text.strip()
        data['Arrival Time'].append(arrival_time if arrival_time else '')

        # Extract base price
        base_price = flight_item.find_all('span')[11].text.strip().split(":")[1].strip()
        data['Base Price'].append(base_price if base_price else '')
    logging.info("html parsing finished")

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(data)
    logging.info(df)
    return df

if __name__ == "__main__":
    df = html_to_df(get_table_html())
    print(df)