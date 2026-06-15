import os
import re
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

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
processed_classes = []

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


    try: # Try to click the Submit button
        submit_btn = wait.until(EC.presence_of_element_located((By.ID, "submit-button"))) # Wait for the Submit button to appear
        submit_btn.click() # Click the Submit button

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
    class_cards = driver.find_elements(By.CSS_SELECTOR, "div[id^='class-card-']") # Find all class cards

    for card in class_cards: # Iterate over each class card
        day_group = card.find_element(By.XPATH, "./ancestor::div[contains(@id, 'day-group-')]") # Find the day group containing the class card
        day_title = day_group.find_element(By.TAG_NAME, "h2").text # Get the day title e.g. "Tue, Jun 16"

        if "Tue" not in day_title and "Thu" not in day_title: # Check if the class is not for Tuesday or Thursday
            continue

        time_text = card.find_element(By.CSS_SELECTOR, "p[id^='class-time-']").text # Get the time text e.g. "6:00 PM"
        if "6:00 PM" not in time_text: # Check if the class is not for 6:00 PM
            continue

        class_name = card.find_element(By.CSS_SELECTOR, "h3[id^='class-name-']").text # Get the class name e.g. "Yoga"

        button = card.find_element(By.CSS_SELECTOR, "button[id^='book-button-']") # Find the book button
        btn_text = button.text # Get the button text e.g. "Book Class"

        class_info = f"{class_name} on {day_title}" # Combine class name and day title e.g. "Yoga on Tue, Jun 16"

        if btn_text == "Booked":  # Check if the button text is "booked"
            print(f"ℹ️ Already booked: {class_info}")
            already_booked_count += 1
            processed_classes.append(f"[Booked] {class_info}")

        elif btn_text == "Waitlisted":  # Check if the button text is "waitlisted"
            print(f"ℹ️ Already on waitlist: {class_info}")
            already_booked_count += 1
            processed_classes.append(f"[Waitlisted] {class_info}")

        elif btn_text == "Join Waitlist":  # Check if the button text is "join waitlist"
            button.click()  # Click the button
            print(f"🟡 Joined waitlist for: {class_info}")
            waitlisted_count += 1
            processed_classes.append(f"[New Waitlist] {class_info}")
            time.sleep(0.5)  # Wait for 0.5 seconds

        elif btn_text == "Book Class":  # If the button text is neither "booked" nor "waitlisted", it must be "book class"
            button.click()  # Click the button
            print(f"✅ Successfully Booked: {class_info}")
            booked_count += 1
            processed_classes.append(f"[New Booking] {class_info}")
            time.sleep(0.5)  # Wait for 0.5 seconds

        else:  # Handle other button text cases
            print(f"❓ Unknown button state '{btn_text}' for {class_info}")

    return booked_count, waitlisted_count, already_booked_count
def check_bookings():
    """
    Check if all Tuesday/Thursday 6pm bookings are within the current week
    :return: count of Tuesday/Thursday 6pm bookings
    """
    driver.find_element(By.ID, "my-bookings-link").click() # Click the "My Bookings" link
    time.sleep(1)  # give page time to load

    verified_count = 0 # Initialize the counter for verified bookings

    all_cards = driver.find_elements(By.CSS_SELECTOR, "div[id*='card-']") # Find all booking cards

    for card in all_cards: # Iterate over each booking card
        try: # Try to find the "When:" paragraph within the card
            when_p = card.find_element(By.XPATH, ".//p[strong[text()='When:']]") # Find the "When:" paragraph
            when_text = when_p.text # Extract the text e.g. "When: Tue, Jun 16 at 6:00 PM"

            if ("Tue" in when_text or "Thu" in when_text) and "6:00 PM" in when_text: # Check if the booking is for Tuesday or Thursday and 6:00 PM
                print(f"✅ Verified {when_text}")
                verified_count += 1 # Increment the counter for Tuesday/Thursday 6pm bookings

        except NoSuchElementException: # If the "When:" paragraph is not found, skip to the next card
            continue

    return verified_count

login_success = login_automatically() # Call the login_automatically function
if login_success: # Check if login was successful
    print("✅ Login successful")

else: # If login failed
    print("❌ Login failed")

booked_count, waitlisted_count, already_booked_count = book_class(booked_count, waitlisted_count, already_booked_count) # Call the book_class function
total_booked = booked_count + waitlisted_count + already_booked_count

print(f"\n--- Total Tuesday/Thursday 6pm classes: {total_booked} ---")
print("\n--- VERIFYING ON MY BOOKINGS PAGE ---")
verified_count = check_bookings()

print(f"\n--- VERIFICATION RESULT ---")
print(f"Expected: {total_booked} bookings")
print(f"Found: {verified_count} bookings")

if total_booked == verified_count:
    print("✅ SUCCESS: All bookings verified!")
else:
    print(f"❌ MISMATCH: Missing {total_booked - verified_count} bookings")