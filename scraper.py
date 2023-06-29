import logging
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class AirlineScraper:
    def __init__(self, user, user_pw, user_airline, user_empno):
        self.user = user
        self.user_pw = user_pw
        self.user_airline = user_airline
        self.user_empno = user_empno

    def __enter__(self):
        self.driver = webdriver.Edge()
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
            data['Airline'] = "Air Hamburg (AHO)"

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
        print("Air Hamburg:\n", df)
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
        concatenated_tables["Departure Date"] = concatenated_tables["Departure Date"].astype('datetime64[ns]')
        concatenated_tables["From"] = concatenated_tables["From"].str[:-4]
        concatenated_tables["To"] = concatenated_tables["To"].str[:-4]
        concatenated_tables["Departure Time"] = pd.to_datetime(concatenated_tables["Time"].str[0:5],  format='%H:%M').dt.strftime('%H:%M')
        concatenated_tables["Arrival Time"] = pd.to_datetime(concatenated_tables["Time"].str[5:],  format='%H:%M').dt.strftime('%H:%M')
        concatenated_tables["Aircraft"] = concatenated_tables["Aircraft"].str[:-11]
        concatenated_tables["Price"] = concatenated_tables["Price"].str[:-15].astype('float64')
        concatenated_tables["Airline"] = "PAD Aviation (PVD)"
        concatenated_tables = concatenated_tables.drop(["Time", "Unnamed: 5"], axis=1).reset_index(drop=True)

        print("PADAviation:\n", concatenated_tables)
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
                'Start Time': start_time,
                'End Time': end_time,
                'Start Airport': start_airport,
                'End Airport': end_airport
            })

        # Create a Pandas DataFrame from the extracted data
        df = pd.DataFrame(data)
        # Format Table
        
        df["Start Time"] = pd.to_datetime(df["Start Time"], format='%d.%m.%Y %H:%M')
        df["End Time"] = pd.to_datetime(df["End Time"], format='%H:%M')
        df["Departure Date"] = df["Start Time"].dt.date
        df["Start Time"] = df["Start Time"].dt.strftime('%H:%M')
        df["Airline"] = "ExcellentAir (ECA)"
        df = df.drop("Flight Number", axis=1)
        # TODO: Add price

        # Print the DataFrame
        print("ExcellentAir:\n", df)
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
                "Aircraft Type": aircraft_type,
                "Seats": seats,
                "Departure IATA Code": departure_iata,
                "Departure Location": departure_location,
                "Departure Time": departure_time,
                "Duration": duration,
                "Departure Date": dep_date,
                "Arrival IATA Code": arrival_iata,
                "Arrival Location": arrival_location,
                "Arrival Time": arrival_time,
                "Price": price,
            }

            # Append the flight data to the list
            data.append(flight_data)

        # Create a Pandas DataFrame from the extracted data
        df = pd.DataFrame(data)

        # Set Datatypes and Carrier
        df["Departure Time"] = pd.to_datetime(df["Departure Time"], format='%H:%M')
        df["Arrival Time"] = pd.to_datetime(df["Arrival Time"], format='%H:%M')
        df["Duration"] = pd.to_datetime(df["Duration"], format='%H:%M')
        df["Departure Date"] = pd.to_datetime(df["Departure Date"], format='%d.%m.%Y').dt.date
        df["Airline"] = "Platon Aviation (05)"

        # Print the DataFrame
        print("Platoon Aviation:\n", df)
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
        print(api_link)

        # Get actual flights
        self.driver.get(api_link)
        html = self.driver.page_source 
        soup = BeautifulSoup(html, 'html.parser')
        flight_times = [item.text for item in soup.find_all(class_='segment__flight-time')]
        flight_info = [item.text.split("arrow_forward") for item in soup.find_all(class_='lift__title')]
        actype = [item for sublist in flight_info[1::2] for item in sublist]
        oandd = flight_info[::2]
        dep = [leg[0].split("(") for leg in oandd]
        dep_city = [i[0] for i in dep]
        dep_iata = [i[1][:3] for i in dep]
        arr = [leg[1].split("(") for leg in oandd]
        arr_city = [i[0] for i in arr]
        arr_iata = [i[1][:3] for i in arr]
        print(dep_city, dep_iata, arr_city, arr_iata)

        raise
        


        soup2 = soup.body.find_all("div", class_='search-hit-list-item')

        print(soup2)

        # Extracting information
        data = []
        for item in soup2:
            try:
                row = {}
                soup = BeautifulSoup(str(item), 'html.parser')
                
                # Extracting airport and airport code
                airports = soup.find('span', class_='lift__title').text.split('arrow_forward')
                row['Departure Airport'] = airports[0].strip()
                row['Destination Airport'] = airports[1].strip()
                row['Departure Airport Code'] = airports[0].strip().split('(')[1].split(')')[0]
                row['Destination Airport Code'] = airports[1].strip().split('(')[1].split(')')[0]
                
                # Extracting departure time
                row['Departure Date'] = soup.select_one('p:contains("Available:") span').text.strip().split(" ")[0]
                row['Comment'] = "Valid departure dates: " + soup.select_one('p:contains("Available:") span').text.strip()
                
                # Extracting flight time
                row['Flight Time'] = soup.find(class_='segment__flight-time').text.strip()
                print(row['Flight Time'])
                
                # AC type
                row['Aircraft Type'] = soup.find(class_='lift__title').text.strip()
                print(row)

                data.append(row)
            except:
                pass
            

        # Creating DataFrame
        df = pd.DataFrame(data)
        raise

        print(df)
        raise

        test = soup.body.div

        iframe = soup.find("iframe", id="avinodeSearchForm")
        iframe_src = iframe["src"]

        # Load the content of the iframe separately
        import requests
        iframe_html = requests.get(iframe_src).text
        iframe_soup = BeautifulSoup(iframe_html, 'html.parser')

        divs = iframe_soup.find_all("div", class_="search-hit-list-item-details__lift-itinerary")
        for div in divs:
            print(div)

        raise

        

        data = []
        divs = soup.find_all("div", class_="search-hit-list-item-details__lift-itinerary")

        print("divs: ", divs)

        for div in divs:
            origin = div.find("span", class_="lift__title t-empty-leg-description").span.text.split(',')[0].strip()
            origin_iata = div.find("span", class_="lift__title t-empty-leg-description").span.text.split('(')[1].split(')')[0]
            destination = div.find("span", class_="lift__title t-empty-leg-description").find_all('span')[-1].text.split(',')[0].strip()
            destination_iata = div.find("span", class_="lift__title t-empty-leg-description").find_all('span')[-1].text.split('(')[1].split(')')[0]
            dep_date = div.find("p", text="Available:").next_sibling.strip()
            ac_type = div.find("span", class_="lift__title").text.strip()
            seats_avl = div.find("span", class_="lift__pax").text.split(' ')[-1]
            flt_duration = div.find("td", class_="segment__flight-time").text.strip()

            data.append([origin, origin_iata, destination, destination_iata, dep_date, ac_type, seats_avl, flt_duration])

        # Create DataFrame
        columns = ['origin', 'origin_iata', 'destination', 'destination_iata', 'dep_date', 'ac_type', 'seats_avl', 'flt_duration']
        df = pd.DataFrame(data, columns=columns)
        print(df)







        '''
        # Find the main data container
        divs = soup.find_all("div", class_="search-hit-list-item-details__lift-itinerary")

        # Initialize an empty list to store the extracted data
        data = []

        print(divs)
        # Iterate over each div
        for div in divs:
            dep_iata = div.find("td", class_="segment__start-end").text
            print("iata code: ", dep_iata)
            raise
        

            lift_pax = div.find('span', class_='lift__pax').text


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
                "Aircraft Type": aircraft_type,
                "Seats": seats,
                "Departure IATA Code": departure_iata,
                "Departure Location": departure_location,
                "Departure Time": departure_time,
                "Duration": duration,
                "Departure Date": dep_date,
                "Arrival IATA Code": arrival_iata,
                "Arrival Location": arrival_location,
                "Arrival Time": arrival_time,
                "Price": price,
            }

            # Append the flight data to the list
            data.append(flight_data)

        # Create a Pandas DataFrame from the extracted data
        df = pd.DataFrame(data)

        # Set Datatypes and Carrier
        df["Departure Time"] = pd.to_datetime(df["Departure Time"], format='%H:%M')
        df["Arrival Time"] = pd.to_datetime(df["Arrival Time"], format='%H:%M')
        df["Duration"] = pd.to_datetime(df["Duration"], format='%H:%M')
        df["Departure Date"] = pd.to_datetime(df["Departure Date"], format='%d.%m.%Y').dt.date
        df["Airline"] = "Platon Aviation (05)"

        # Print the DataFrame
        print("Platoon Aviation:\n", df)
        logging.info("Platoon Aviation finished")
        return df'''