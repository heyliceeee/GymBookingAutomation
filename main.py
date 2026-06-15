import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    login_btn = wait.until(EC.presence_of_element_located((By.ID, "login-button"))) # Wait for the login button to appear
    login_btn.click() # Click the login button

    email_input = wait.until(EC.presence_of_element_located((By.ID, "email-input"))) # Wait for the email input field to appear
    email_input.clear() # Clear the email input field
    email_input.send_keys(os.getenv("ACCOUNT_EMAIL")) # Enter the email address from the .env file

    password_input = wait.until(EC.presence_of_element_located((By.ID, "password-input"))) # Wait for the password input field to appear
    password_input.clear() # Clear the password input field
    password_input.send_keys(os.getenv("ACCOUNT_PASSWORD")) # Enter the password from the .env file

    submit_btn = wait.until(EC.presence_of_element_located((By.ID, "submit-button"))) # Wait for the Submit button to appear
    submit_btn.click() # Click the Submit button

    wait.until(EC.presence_of_element_located((By.ID, "schedule-page"))) # Wait for the "Class Schedule" page to appear
def click_and_verify(button):
    """
    Click a button and verify the button text
    :param button: button to click
    """
    button.click() # Click the button
    wait.until(lambda d: button.text in ["Booked", "Waitlisted"]) # Wait for the button text to change to "Booked" or "Waitlisted"
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
            retry(lambda: click_and_verify(button), description=f"Waitlist {class_info}")  # Call click_and_verify with retries
            print(f"🟡 Joined waitlist for: {class_info}")
            waitlisted_count += 1
            processed_classes.append(f"[New Waitlist] {class_info}")

        elif btn_text == "Book Class":  # If the button text is neither "booked" nor "waitlisted", it must be "book class"
            retry(lambda: click_and_verify(button), description=f"Booking {class_info}")  # Call click_and_verify with retries
            print(f"✅ Successfully Booked: {class_info}")
            booked_count += 1
            processed_classes.append(f"[New Booking] {class_info}")

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

    all_cards = driver.find_elements(By.CSS_SELECTOR, "div[id^='booking-']") # Find all booking cards

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
def retry(func, retries=7, description=None):
    """
    Retry a function if it fails
    :param func: a function to retry
    :param retries: retry count
    :param description: description of the function
    :return: function result
    """
    for attempt in range(1, retries + 1): # Retry up to retries times
        try: # Try to execute the function
            print(f"Attempt {attempt}/{retries} → {description}") # Print the attempt number
            return func() # Return the function result

        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException, Exception) as e:
            print(f"Failed attempt {attempt}: {e}") # Print the failure message
            time.sleep(1) # Wait for 1 second before retrying

    raise Exception(f"❌ All retries failed for: {description}") # If all retries fail, raise an exception

retry(login_automatically, description="Login") # Call the login_automatically function with retries

booked_count, waitlisted_count, already_booked_count = retry(lambda: book_class(booked_count, waitlisted_count, already_booked_count), description="Booking classes") # Call the book_class function with retries
total_booked = booked_count + waitlisted_count + already_booked_count

print(f"\n--- Total Tuesday/Thursday 6pm classes: {total_booked} ---")
print("\n--- VERIFYING ON MY BOOKINGS PAGE ---")

verified_count = retry(check_bookings, description="Check bookings") # Call the check_bookings function with retries

print(f"\n--- VERIFICATION RESULT ---")
print(f"Expected: {total_booked} bookings")
print(f"Found: {verified_count} bookings")

if total_booked == verified_count:
    print("✅ SUCCESS: All bookings verified!")
else:
    print(f"❌ MISMATCH: Missing {total_booked - verified_count} bookings")