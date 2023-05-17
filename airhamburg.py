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
print(user, user_pw)

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

"""flights = driver.find_element(By.CLASS_NAME,"flights-list")
table_html = flights.get_attribute("outerHTML")
df_list = pd.read_html(table_html)
df = df_list[0]
print(df)"""

html = driver.page_source
from bs4 import BeautifulSoup
import pandas as pd

# Parse the HTML code with BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Find all the flight list items
flight_list_items = soup.select('.flights-list')
print(flight_list_items)

# Loop through each flight and extract the data
data = []
for item in flight_list_items:
    flight_no = item.select_one('.flight_no').text
    aircraft_name = item.select_one('.aircraftInfo > .name').text
    seats = item.select_one('.seats').text
    factsheet_url = item.select_one('.aircraftInfo > .factsheet')['href']
    data.append([flight_no, aircraft_name, seats, factsheet_url])

# Create a pandas dataframe from the extracted data
df = pd.DataFrame(data, columns=['Flight No', 'Aircraft Name', 'Seats', 'Factsheet URL'])

# Print the dataframe
print(df)