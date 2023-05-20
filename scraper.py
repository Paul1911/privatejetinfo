import logging
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class AirHamburgScraper:
    def __init__(self, user, user_pw, user_airline, user_empno):
        self.user = user
        self.user_pw = user_pw
        self.user_airline = user_airline
        self.user_empno = user_empno
        self.driver = webdriver.Firefox()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def login(self):
        self.driver.get("https://www.air-hamburg.de/de/login")
        time.sleep(2)
        cookie_decline_button = self.driver.find_element(By.CLASS_NAME, "cc-deny")
        cookie_decline_button.click()
        # Blank area click to close hover over menus
        random_area = self.driver.find_element(By.CLASS_NAME, "control-label")
        random_area.click()

        time.sleep(2)
        id_box = self.driver.find_element(By.ID, "username")
        #id_box = WebDriverWait(self.driver, 10).until(
        #    EC.visibility_of_element_located((By.ID, "username"))
        #)
        id_box.send_keys(self.user)

        pass_box = self.driver.find_element(By.NAME, "password")
        pass_box.send_keys(self.user_pw)

        login_button = self.driver.find_element(By.CLASS_NAME, "btn-primary")
        login_button.click()

    def get_table_html(self):
        self.driver.get("https://www.air-hamburg.de/de/idtravel")
        accept_continue_button = self.driver.find_element(By.CLASS_NAME, "uk-button-primary")
        accept_continue_button.click()

        airline_box_locator = (By.ID, "employee.fieldset[0].fields.em_airline")
        airline_box = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(airline_box_locator))
        #airline_box = self.driver.find_element(By.ID, "employee.fieldset[0].fields.em_airline")
        select = Select(airline_box)
        select.select_by_value(self.user_airline)

        emp_id_box = self.driver.find_element(By.CLASS_NAME, "field-text")
        emp_id_box.send_keys(self.user_empno)
        self.driver.execute_script("window.scrollBy(0, 1000);")
        emp_ret_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-bind*="_onClick"]')
        emp_ret_button.click()

        next_button = self.driver.find_element(By.CLASS_NAME, "uk-button-primary")
        self.driver.execute_script("window.scrollBy(0, 1000);")
        next_button.click()

        # Parse the HTML code with BeautifulSoup
        html = self.driver.page_source
        return html

    def html_to_df(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        flight_list = soup.find_all("ul", class_="flights-list")
        flight_items = []
        for flight in flight_list:
            flight_items.extend(flight.find_all('li'))

        data = {
            'Airline': [],
            "Departure Date": [],
            'Departure Code': [],
            'Departure Airport': [],
            'Departure Time': [],
            'Arrival Code': [],
            'Arrival Airport': [],
            'Arrival Time': [],
            'Duration': [],
            'Distance': [],
            'Aircraft Type': [],
            'Seats': [],
            'Base Price': []
        }

        for flight_item in flight_items:

            # Add airline
            data['Airline'] = "Air Hamburg (02)"

            # Extract departure information
            departure_div = flight_item.find('div', {'class': 'departure'})
            departure_code = departure_div.find('h4').text.strip()
            data['Departure Code'].append(departure_code if departure_code else '')
            departure_airport = departure_div.find_all('span')[0].text.strip()
            data['Departure Airport'].append(departure_airport if departure_airport else '')
            departure_date = flight_item.find('span', {'class': 'distanceinfo'}).text.strip()
            data['Departure Date'].append(departure_date if departure_date else '')
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
        logging.info("Air Hamburg finished")
        return df

class PadaviationScraper:
    def __init__(self, user, user_pw, user_airline, user_empno):
        self.user = user
        self.user_pw = user_pw
        self.user_airline = user_airline
        self.user_empno = user_empno
        self.driver = webdriver.Firefox()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def login(self):
        self.driver.get("https://traveller.padaviation.com/")
        # Login
        username_box = self.driver.find_element(By.CLASS_NAME, "css-1kp110w")
        username_box.send_keys(self.user)
        password_box = self.driver.find_element(By.ID, "field-:r1:")
        password_box.send_keys(self.user_pw)
        login_button = self.driver.find_element(By.CLASS_NAME, "css-12susmb")
        login_button.click()

        # Accept Conditions
        time.sleep(1)
        accept_conditions_checkbox = self.driver.find_element(By.CLASS_NAME, "css-1q9fgjv")
        accept_conditions_checkbox.click()
        accept_button = self.driver.find_element(By.CLASS_NAME, "css-1749gbk")
        accept_button.click()

        # Select Airline and enter Emp No 
        airline_box = self.driver.find_element(By.ID, "airline")
        select = Select(airline_box)
        select.select_by_visible_text("Swiss")
        emp_id_box = self.driver.find_element(By.ID, "field-:r4:")
        emp_id_box.send_keys("77889")
        continue_button = self.driver.find_element(By.CLASS_NAME, "css-14wvpnd")
        continue_button.click()

        ####################


    def get_table_html(self):
        self.driver.get("https://www.air-hamburg.de/de/idtravel")
        accept_continue_button = self.driver.find_element(By.CLASS_NAME, "uk-button-primary")
        accept_continue_button.click()

        airline_box_locator = (By.ID, "employee.fieldset[0].fields.em_airline")
        airline_box = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(airline_box_locator))
        #airline_box = self.driver.find_element(By.ID, "employee.fieldset[0].fields.em_airline")
        select = Select(airline_box)
        select.select_by_value(self.user_airline)

        emp_id_box = self.driver.find_element(By.CLASS_NAME, "field-text")
        emp_id_box.send_keys(self.user_empno)

        emp_ret_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-bind*="_onClick"]')
        emp_ret_button.click()

        next_button = self.driver.find_element(By.CLASS_NAME, "uk-button-primary")
        self.driver.execute_script("window.scrollBy(0, 1000);")
        next_button.click()

        # Parse the HTML code with BeautifulSoup
        html = self.driver.page_source
        return html

    def html_to_df(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        flight_list = soup.find_all("ul", class_="flights-list")
        flight_items = []
        for flight in flight_list:
            flight_items.extend(flight.find_all('li'))

        data = {
            'Airline': [],
            "Departure Date": [],
            'Departure Code': [],
            'Departure Airport': [],
            'Departure Time': [],
            'Arrival Code': [],
            'Arrival Airport': [],
            'Arrival Time': [],
            'Duration': [],
            'Distance': [],
            'Aircraft Type': [],
            'Seats': [],
            'Base Price': []
        }

        for flight_item in flight_items:

            # Add airline
            data['Airline'] = "Air Hamburg (02)"

            # Extract departure information
            departure_div = flight_item.find('div', {'class': 'departure'})
            departure_code = departure_div.find('h4').text.strip()
            data['Departure Code'].append(departure_code if departure_code else '')
            departure_airport = departure_div.find_all('span')[0].text.strip()
            data['Departure Airport'].append(departure_airport if departure_airport else '')
            departure_date = flight_item.find('span', {'class': 'distanceinfo'}).text.strip()
            data['Departure Date'].append(departure_date if departure_date else '')
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
        logging.info("Air Hamburg finished")
        return df