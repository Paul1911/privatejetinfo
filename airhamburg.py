import selenium 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import pandas as pd
from config import config

user = config['user_02']
user_pw = config['user_password_02']
user_airline = config['user_airline_02']
user_empno = config['user_empno_02']

# Using Chrome to access web
driver = webdriver.Firefox()# Open the website
driver.get("https://www.air-hamburg.de/de/login")
time.sleep(2)
cookie_decline_button = driver.find_element(By.CLASS_NAME, "cc-deny")
cookie_decline_button.click()

# Find input boxes
id_box = driver.find_element(By.ID,"username")

# Send id information
id_box.send_keys(user)

# Find password box
pass_box = driver.find_element(By.NAME, "password")
# Send password
pass_box.send_keys(user_pw)# Find login button
#login_button = driver.find_element_by_name('submit')# Click login
login_button = driver.find_element(By.CLASS_NAME,"btn-primary")
# Click login
login_button.click()
driver.get("https://www.air-hamburg.de/de/idtravel")
accept_continue_button = driver.find_element(By.CLASS_NAME,"uk-button-primary")
accept_continue_button.click()

time.sleep(2)
airline_box = driver.find_element(By.ID,"employee.fieldset[0].fields.em_airline")
time.sleep(2)

select = Select(airline_box)
select.select_by_value(user_airline)
emp_id_box = driver.find_element(By.CLASS_NAME,"field-text")
emp_id_box.send_keys(user_empno)
emp_ret_button = driver.find_element(By.CSS_SELECTOR, 'button[data-bind*="_onClick"]')
emp_ret_button.click()
next_button = driver.find_element(By.CLASS_NAME,"uk-button-primary")
driver.execute_script("window.scrollBy(0, 1000);")
next_button.click()

html = driver.page_source
from bs4 import BeautifulSoup
import pandas as pd

# Parse the HTML code with BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

flight_list = soup.find_all("ul", class_="flights-list")
html_string = ''.join(str(item) for item in flight_list)

# Parse the HTML
soup = BeautifulSoup(html_string, 'html.parser')

# Find all the flight items
flight_items = soup.find_all('li')

# Create lists to store the extracted values
# Create an empty dictionary to store the data
data = {
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

    departure_div = flight_item.find('div', {'class': 'departure'})
    arrival_div = flight_item.find('div', {'class': 'arrival'})

    # Add airline
    data['Airline'] = "Air Hamburg (02)"

    # Extract aircraft type
    aircraft_type = flight_item.find_all('span')[0].text.strip().split(":")[1]
    data['Aircraft Type'].append(aircraft_type if aircraft_type else '')

    # Extract seats
    seats = flight_item.find_all('span')[1].text.strip().split(" ")[1]
    data['Seats'].append(seats if seats else '')

    # Extract departure code
    departure_code = departure_div.find('h4').text.strip()
    data['Departure Code'].append(departure_code if departure_code else '')

    # Extract departure airport
    departure_airport = departure_div.find_all('span')[0].text.strip()
    data['Departure Airport'].append(departure_airport if departure_airport else '')

    # Extract departure time
    departure_time = departure_div.find_all('span')[1].text.strip()
    data['Departure Time'].append(departure_time if departure_time else '')

    # Extract duration
    duration = flight_item.find('span', {'class': 'durationinfo'}).text.strip().split("/")[0]
    data['Duration'].append(duration if duration else '')

    # Extract distance
    distance = flight_item.find('span', {'class': 'durationinfo'}).text.strip().split("/")[1]
    data['Distance'].append(distance if distance else '')

    # Extract arrival code
    arrival_code = arrival_div.find('h4').text.strip()
    data['Arrival Code'].append(arrival_code if arrival_code else '')

    # Extract arrival airport
    arrival_airport = arrival_div.find_all('span')[0].text.strip()
    data['Arrival Airport'].append(arrival_airport if arrival_airport else '')

    # Extract arrival time
    arrival_time = arrival_div.find_all('span')[1].text.strip()
    data['Arrival Time'].append(arrival_time if arrival_time else '')

    # Extract base price
    base_price = flight_item.find_all('span')[11].text.strip().split(":")[1].strip()
    data['Base Price'].append(base_price if base_price else '')

# Create a DataFrame from the extracted data
df = pd.DataFrame(data)

# Print the DataFrame
print(df)