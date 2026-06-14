import os
import re
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

load_dotenv()

GYM_URL = os.getenv("GYM_URL") # Get the GYM_URL from the .env file

chrome_options = webdriver.ChromeOptions() # Create a new option object
chrome_options.add_experimental_option("detach", True) # Attach the driver to the background
user_data_dir = os.path.join(os.getcwd(), "chrome_profile") # Set the user data directory
chrome_options.add_argument(f"--user-data-dir={user_data_dir}") # Add the user data directory argument

driver = webdriver.Chrome(options=chrome_options) # Instantiate the driver
driver.get(GYM_URL) # Navigate to the GYM_URL
wait = WebDriverWait(driver, 5) # Create a new wait object

booked_count = 0
waitlisted_count = 0
already_booked_count = 0

def login_automatically():
    """
    Login to the gym automatically
    :return: true if login was successful, false otherwise
    """
    try: # Try to click the login button
        login_btn = wait.until(EC.presence_of_element_located((By.ID, "login-button"))) # Wait for the login button to appear
        login_btn.click() # Click the login button

    except TimeoutException: # Handle timeout exceptions
        print("Login button not found")
        return False


    try: # Try to fill in the email and password fields
        email_input = wait.until(EC.presence_of_element_located((By.ID, "email-input"))) # Wait for the email input field to appear
        email_input.send_keys(os.getenv("ACCOUNT_EMAIL")) # Enter the email address from the .env file

        password_input = wait.until(EC.presence_of_element_located((By.ID, "password-input"))) # Wait for the password input field to appear
        password_input.send_keys(os.getenv("ACCOUNT_PASSWORD")) # Enter the password from the .env file

    except TimeoutException: # Handle timeout exceptions
        print("Email or password input fields not found")
        return False


    try: # Try to click the submit button
        submit_btn = wait.until(EC.presence_of_element_located((By.ID, "submit-button"))) # Wait for the submit button to appear
        submit_btn.click() # Click the submit button

    except TimeoutException: # Handle timeout exceptions
        print("Submit button not found")
        return False


    try: # Wait for the "Class Schedule" page to appear
        wait.until(EC.presence_of_element_located((By.ID, "schedule-page"))) # Wait for the "Class Schedule" page to appear
        return True

    except TimeoutException: # Handle timeout exceptions
        print("Class Schedule page not found")
        return False
def book_class(booked_count, waitlisted_count, already_booked_count):
    """
    Book all 6pm Tuesday and Thursday classes
    :param booked_count: Booked class count
    :param waitlisted_count: Waitlisted class count
    :param already_booked_count: Already booked/waitlisted class count
    :return: Updated booked_count, waitlisted_count, already_booked_count
    """
    day_groups = [] # Initialize an empty list to store day groups
    day_groups += driver.find_elements(By.CSS_SELECTOR, "div[id^='day-group-tue']") # Find all Tuesdays class
    day_groups += driver.find_elements(By.CSS_SELECTOR, "div[id^='day-group-thu']") # Find all Thursdays class

    for day in day_groups: # Iterate over each day group
        six_pm_classes = day.find_elements(By.CSS_SELECTOR, "div[id$='-1800']") # Find all 6pm classes on the current day

        for six_pm_class in six_pm_classes: # Iterate over each 6pm class
            name_class = six_pm_class.find_element(By.CSS_SELECTOR, "h3").text # Find the class name

            id_class = six_pm_class.get_attribute("id") # Get the class ID
            date_raw = re.search(r"\d{4}-\d{2}-\d{2}", id_class).group(0) # Extract the date from the class ID
            date_obj = datetime.strptime(date_raw, "%Y-%m-%d") # Convert the date string to a datetime object
            date_formatted = date_obj.strftime("%b %d") # Format the date as "Jan 01"

            try: # Try to find the button inside the class card
                btn = six_pm_class.find_element(By.CSS_SELECTOR, "div.ClassCard_cardActions__tVZBm button") # Find the button
                btn_text = btn.text.lower() # Convert the button text to lowercase

                if btn_text == "booked": # Check if the button text is "booked"
                    print(f"ℹ️ Already booked: {name_class} on {date_formatted}")
                    already_booked_count += 1

                elif btn_text == "waitlisted": # Check if the button text is "waitlisted"
                    print(f"ℹ️ Already on waitlist: {name_class} on {date_formatted}")
                    already_booked_count += 1

                elif btn_text == "join waitlist": # Check if the button text is "join waitlist"
                    btn.click()  # Click the button
                    print(f"🟡 Joined waitlist for: {name_class} on {date_formatted}")
                    waitlisted_count += 1
                    time.sleep(0.5) # Wait for 0.5 seconds

                elif btn_text == "book class": # If the button text is neither "booked" nor "waitlisted", it must be "book class"
                    btn.click() # Click the button
                    print(f"✅ Successfully Booked: {name_class} on {date_formatted}")
                    booked_count += 1
                    time.sleep(0.5)  # Wait for 0.5 seconds

                else: # Handle other button text cases
                    print(f"❓ Unknown button state '{btn_text}' for {name_class} on {date_formatted}")

            except NoSuchElementException: # Handle the case where the button is not found
                print(f"❌ Button not found for {name_class} on {date_formatted}")

    return booked_count, waitlisted_count, already_booked_count

login_success = login_automatically() # Call the login_automatically function
if login_success: # Check if login was successful
    print("✅ Login successful")

else: # If login failed
    print("❌ Login failed")


booked_count, waitlisted_count, already_booked_count = book_class(booked_count, waitlisted_count, already_booked_count) # Call the book_class function

# Print the booking summary
print("\n--- BOOKING SUMMARY ---")
print(f"Classes booked: {booked_count}")
print(f"Waitlists joined: {waitlisted_count}")
print(f"Already booked/waitlisted: {already_booked_count}")
print(f"Total Tuesday 6pm classes processed: {booked_count + waitlisted_count + already_booked_count}")