import logging
import time
import pandas as pd
from bs4 import BeautifulSoup
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import airportsdata

class AirlineScraper:
    def __init__(self, user, user_pw, user_airline, user_empno):
        self.user = user
        self.user_pw = user_pw
        self.user_airline = user_airline
        self.user_empno = user_empno

    def __enter__(self):
        #self.driver = webdriver.Edge()
        options = webdriver.ChromeOptions()
        #options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()
class AirHamburgScraper(AirlineScraper):

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
            'Departure IATA': [],
            'Departure Airport': [],
            'Departure Time': [],
            'Arrival IATA': [],
            'Arrival Airport': [],
            'Arrival Time': [],
            'Duration': [],
            'Distance': [],
            'Aircraft': [],
            'Available Seats': [],
            'Price': []
        }

        for flight_item in flight_items:

            # Add airline
            data['Airline'] = "Air Hamburg"

            # Extract departure information
            departure_div = flight_item.find('div', {'class': 'departure'})
            departure_code = departure_div.find('h4').text.strip()
            data['Departure IATA'].append(departure_code if departure_code else '')
            departure_airport = departure_div.find_all('span')[0].text.strip()
            data['Departure Airport'].append(departure_airport if departure_airport else '')
            departure_date = flight_item.find('span', {'class': 'distanceinfo'}).text.strip()
            data['Departure Date'].append(departure_date if departure_date else '')
            departure_time = departure_div.find_all('span')[1].text.strip()
            data['Departure Time'].append(departure_time if departure_time else '')

            # Extract flight info
            aircraft_type = flight_item.find_all('span')[0].text.strip().split(":")[1]
            data['Aircraft'].append(aircraft_type if aircraft_type else '')
            seats = flight_item.find_all('span')[1].text.strip().split(" ")[1]
            data['Available Seats'].append(seats if seats else '')
            duration = flight_item.find('span', {'class': 'durationinfo'}).text.strip().split("/")[0]
            data['Duration'].append(duration if duration else '')
            distance = flight_item.find('span', {'class': 'durationinfo'}).text.strip().split("/")[1]
            data['Distance'].append(distance if distance else '')

            # Extract arrival information
            arrival_div = flight_item.find('div', {'class': 'arrival'})
            arrival_code = arrival_div.find('h4').text.strip()
            data['Arrival IATA'].append(arrival_code if arrival_code else '')
            arrival_airport = arrival_div.find_all('span')[0].text.strip()
            data['Arrival Airport'].append(arrival_airport if arrival_airport else '')
            arrival_time = arrival_div.find_all('span')[1].text.strip()
            data['Arrival Time'].append(arrival_time if arrival_time else '')

            # Extract Price
            base_price = flight_item.find_all('span')[11].text.strip().split(":")[1].strip()
            data['Price'].append(base_price if base_price else '')

        # Create a DataFrame from the extracted data
        df = pd.DataFrame(data)
        # Adjust dtypes
        df['Departure Date'] = pd.to_datetime(df['Departure Date'], format='%d.%m.%Y')
        df["Duration"] = df['Duration'].apply(lambda x: datetime.datetime.strptime(x.strip(), "%H:%M h").strftime("%H:%M") + " h")
        print("Air Hamburg:\n", df.head())
        logging.info("Air Hamburg finished")
        return df
    
class PadaviationScraper(AirlineScraper):
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
        time.sleep(2)
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
        time.sleep(2)


    def html_to_df(self):

        html = self.driver.page_source 

        # get Dates 
        soup = BeautifulSoup(html, 'html.parser')
        dates = [header.get_text() for header in soup.find_all('h1')]

        # Add Dates to Tables 
        tables = pd.read_html(html)
        for index, table in enumerate(tables):
            table["Departure Date"] = dates[index]

        # Format Table
        concatenated_tables = pd.concat(tables, axis=0)
        concatenated_tables["Departure Date"] = pd.to_datetime(concatenated_tables["Departure Date"], format='%A, %d %b %Y')
        concatenated_tables["Departure Airport"] = concatenated_tables["From"].str[:-4]
        concatenated_tables["Departure ICAO"] = concatenated_tables["From"].str[-4:]
        concatenated_tables["Arrival Airport"] = concatenated_tables["To"].str[:-4]
        concatenated_tables["Arrival ICAO"] = concatenated_tables["To"].str[-4:]
        concatenated_tables["Departure Time"] = pd.to_datetime(concatenated_tables["Time"].str[0:5],  format='%H:%M').dt.strftime('%H:%M')
        concatenated_tables["Arrival Time"] = pd.to_datetime(concatenated_tables["Time"].str[5:],  format='%H:%M').dt.strftime('%H:%M')
        # This duration calculation does not account for possible time zone changes
        #concatenated_tables["Duration"] = pd.to_datetime(concatenated_tables["Arrival Time"]) - pd.to_datetime(concatenated_tables["Departure Time"])
        #concatenated_tables["Duration"] = (concatenated_tables["Duration"].dt.total_seconds() // 60).astype(int)
        #concatenated_tables["Duration"] = concatenated_tables["Duration"].apply(lambda x: f"{x // 60:02d}:{x % 60:02d} h")
        concatenated_tables["Aircraft"] = concatenated_tables["Aircraft"].str[:-11]
        concatenated_tables["Price"] = concatenated_tables["Price"].str[:-15].astype('str') + " €"
        concatenated_tables["Airline"] = "PAD Aviation"
        concatenated_tables = concatenated_tables.drop(["Time", "Unnamed: 5", "From", "To"], axis=1).reset_index(drop=True)


        print("PADAviation:\n", concatenated_tables.head())
        logging.info("PADaviation finished")

        return concatenated_tables
    
class ExcellentAirScraper(AirlineScraper):
    def login(self):
        self.driver.get("https://excellentair.de/en/ferry-flights-for-crews/")
        # Login
        password_box = self.driver.find_element(By.ID, "pwbox-625")
        password_box.send_keys(self.user_pw)
        login_button = self.driver.find_element(By.NAME, "Submit")
        login_button.click()
        time.sleep(8)

    def html_to_df(self):

        html = self.driver.page_source 

        soup = BeautifulSoup(html, 'html.parser')

        # Find all elements with the "flight" class
        flight_elements = soup.find_all('div', class_='flight')

        # Create a list to store the extracted data
        data = []

        # Iterate over the flight elements and extract the desired information
        for flight in flight_elements:
            flight_number = flight.find(class_="no").text.strip()
            start_time = flight.find(class_="start").text.strip().split('\n')[-1]
            end_time = flight.find(class_="end").text.strip()
            start_airport = flight.find(class_="airport").find(class_="start").abbr.text.strip()
            end_airport = flight.find(class_="airport").find(class_="end").abbr.text.strip()
            
            # Append the extracted data as a dictionary to the 'data' list
            data.append({
                'Flight Number': flight_number,
                'Departure Time': start_time,
                'Arrival Time': end_time,
                'Departure IATA': start_airport,
                'Arrival IATA': end_airport
            })

        # Create a Pandas DataFrame from the extracted data
        df = pd.DataFrame(data)

        # TODO: Add airport names
        #airports = airportsdata.load('IATA')
        #df["Departure Airport"] = airports[]
        # Format Table
        
        df["Departure Time"] = pd.to_datetime(df["Departure Time"], format='%d.%m.%Y %H:%M')
        df["Arrival Time"] = pd.to_datetime(df["Arrival Time"], format='%H:%M')
        # This duration calculation does not account for possible time zone changes
        #df["Duration"] = (df["Arrival Time"]-(pd.to_datetime(df["Departure Time"].dt.strftime('%H:%M'), format='%H:%M')))
        df["Departure Date"] = pd.to_datetime(df["Departure Time"].dt.date, format='%Y-%m-%d') 
        df["Departure Time"] = df["Departure Time"].dt.strftime('%H:%M')
        df["Arrival Time"] = df["Arrival Time"].dt.strftime('%H:%M')
        df["Airline"] = "ExcellentAir"
        df["Price"] = "see below"
        df = df.drop("Flight Number", axis=1)

        # Print the DataFrame
        print("ExcellentAir:\n", df.head())
        logging.info("ExcellentAir finished")
        return df

class PlatoonAviationScraper(AirlineScraper):
    def login(self):
        self.driver.get("https://idtravel.flyplatoon.com/")
        # Login
        username_box = self.driver.find_element(By.ID, "username")
        username_box.send_keys(self.user)
        password_box = self.driver.find_element(By.ID, "password")
        password_box.send_keys(self.user_pw)
        login_button = self.driver.find_element(By.CLASS_NAME, "submit")
        login_button.click()
        accept_terms_button = self.driver.find_element(By.ID, "ctrl_5")
        accept_terms_button.click()
        self.driver.find_element(By.CSS_SELECTOR, 'select[name="firma"] option[value="Swiss"]').click()
        emp_no_box = self.driver.find_element(By.ID, "ctrl_58")
        emp_no_box.send_keys(self.user_empno)
        radio_isemp = self.driver.find_element(By.ID, "opt_59_0")
        radio_isemp.click()
        next_step_button = self.driver.find_element(By.ID, "ctrl_7")
        next_step_button.click()
        time.sleep(1)

    def html_to_df(self):

        html = self.driver.page_source 

        soup = BeautifulSoup(html, 'html.parser')

        # Find the main data container
        container_div = soup.find("div", class_="layout_full")
        divs = container_div.find_all("div", class_="item")

        # Initialize an empty list to store the extracted data
        data = []

        # Iterate over each div
        for div in divs:
            # Extract the flight information from the current div
            aircraft_type = div.find("div", class_="flights-left").find("span").find("b").text
            seats = div.find("div", class_="flights-left").find_all("span")[1].find("b").text

            departure_location = div.find("div", class_="flights-departure").find_all("span")[0].text
            departure_iata = div.find("div", class_="flights-departure").find_all("h3")[0].text
            departure_time = div.find("div", class_="flights-departure").find_all("span")[1].text

            duration = div.find("div", class_="flights-duration").find("span", class_="durationinfo").text[0:5]
            dep_date = div.find("div", class_="flights-duration").find("span", class_="distanceinfo").find("b").text

            arrival_location = div.find("div", class_="flights-arrival").find_all("span")[0].text
            arrival_iata = div.find("div", class_="flights-arrival").find_all("h3")[0].text
            arrival_time = div.find("div", class_="flights-arrival").find_all("span")[1].text

            price = div.find("div", class_="flights-right").find_all("span")[2].find("b").text
            
            # Create a dictionary for the current flight information
            flight_data = {
                "Aircraft": aircraft_type,
                "Available Seats": seats,
                "Departure IATA": departure_iata,
                "Departure Airport": departure_location,
                "Departure Time": departure_time,
                "Duration": duration,
                "Departure Date": dep_date,
                "Arrival IATA": arrival_iata,
                "Arrival Airport": arrival_location,
                "Arrival Time": arrival_time,
                "Price": price,
            }

            # Append the flight data to the list
            data.append(flight_data)

        # Create a Pandas DataFrame from the extracted data
        df = pd.DataFrame(data)

        # Set Datatypes and Carrier
        df["Departure Time"] = df["Departure Time"].apply(lambda x: datetime.datetime.strptime(x.strip(), "%H:%M").strftime("%H:%M"))
        df["Arrival Time"] = df['Arrival Time'].apply(lambda x: datetime.datetime.strptime(x.strip(), "%H:%M").strftime("%H:%M"))
        df["Duration"] = df['Duration'].apply(lambda x: datetime.datetime.strptime(x.strip(), "%H:%M").strftime("%H:%M") + " h")
        df["Departure Date"] = pd.to_datetime(df["Departure Date"], format='%d.%m.%Y')
        df["Airline"] = "Platoon Aviation"

        # Print the DataFrame
        print("Platoon Aviation:\n", df.head())
        logging.info("Platoon Aviation finished")
        return df
    
class SilverCloudAir(AirlineScraper):
    def login(self):
        self.driver.get("https://www.silver-cloud-air.com/id-travel/")
        accept_cookies_button = self.driver.find_element(By.ID, "cde-consent")
        accept_cookies_button.click()
        # Login
        password_box = self.driver.find_element(By.ID, "pwbox-3559")
        password_box.send_keys(self.user_pw)
        login_button = self.driver.find_element(By.NAME, "Submit")
        login_button.click()       

    def html_to_df(self):

        # Get the link to the API
        wait = WebDriverWait(self.driver, 20)  # Adjust the timeout as needed
        element = wait.until(EC.presence_of_element_located((By.ID, "avinodeApp")))
        div_content = element.get_attribute("innerHTML")
        soup = BeautifulSoup(div_content, 'html.parser')
        api_link = soup.find("iframe")["src"]

        # Get actual flights
        self.driver.get(api_link)
        html = self.driver.page_source 
        soup = BeautifulSoup(html, 'html.parser')

        # Dep Date
        dep_daterange = []
        dep_date = []
        for p_tag in soup.find("div", class_="search-hit-list").find_all("p")[::4]:
            if "to" in p_tag.get_text():
                dep_daterange.append(p_tag.get_text().replace("\xa0"," "))
            else:
                dep_daterange.append("")
            dep_date.append(p_tag.get_text()[11:21])

        flight_duration = [item.text for item in soup.find_all(class_='segment__flight-time')]
        flight_info = [item.text.split("arrow_forward") for item in soup.find_all(class_='lift__title')]
        actype = [item for sublist in flight_info[1::2] for item in sublist]
        oandd = flight_info[::2]
        dep = [leg[0].split("(") for leg in oandd]
        dep_city = [i[0] for i in dep]
        dep_iata = [i[1][:3] for i in dep]
        arr = [leg[1].split("(") for leg in oandd]
        arr_city = [i[0] for i in arr]
        arr_iata = [i[1][:3] for i in arr]

        data=[dep_date, dep_iata, dep_city, arr_iata, arr_city, flight_duration, actype, dep_daterange]
        columns=['Departure Date', 'Departure IATA', 'Departure Airport', 'Arrival IATA', 'Arrival Airport', 'Duration', 'Aircraft', 'Comment']
        data_dict = {col: lst for col, lst in zip(columns, data)}
        df = pd.DataFrame(data_dict)

        # Set Datatypes and Carrier
        df["Departure Date"] = pd.to_datetime(df["Departure Date"], format='%Y-%m-%d')
        df["Duration"] = df['Duration'].apply(lambda x: datetime.datetime.strptime(x.strip(), "%H:%M").strftime("%H:%M") + " h")
        df["Airline"] = "Silver Cloud Air"
        df["Price"] = "see below"

        print("Silver Cloud Air:\n", df.head())
        logging.info("Silver Cloud Air finished")
        return df