import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from rfile import get_users
from tqdm import tqdm

def parse_arguments():
    parser = argparse.ArgumentParser(description="Automate web tasks using Selenium.")
    parser.add_argument("--url", required=True, default="$R_HOST", help="URL of the target server.")
    parser.add_argument("--username", required=True, default="$USERNAME", help="Username for logging in.")
    parser.add_argument("--password", required=True, default="$PASSWORD", help="Password for logging in.")
    parser.add_argument("--port", required=True, default="$R_PORT", help="Port number of the target server.")
    parser.add_argument("--date", required=True, help="The date to set for users. Formet 'YYYY-MM-DD'")
    parser.add_argument("--headless", action="store_true", help="Run the browser in headless mode.")
    return parser.parse_args()

def main():
    args = parse_arguments()
    # Set Chrome options to disable logging for DevTools
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = setup_webdriver(args.headless,chrome_options)
    log_in(driver,args.url, args.port, args.username, args.password)
    user_list = get_users()
    print(f"Total users: {len(user_list)}")
    change_date(driver, args.url, args.port, user_list, args.date)
    driver.quit()
    print("----------------------------------")
    print("Automation completed successfully!")

def setup_webdriver(headless, chrome_options):
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--log-level=3")  # Mute the logging to suppress warnings
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
    )


def log_in(driver, url, port, username, password):
    driver.get(f'http://{url}:{port}/radiusmanager/admin.php')
    user_name_box = driver.find_element(By.ID, 'managername')
    user_name_box.send_keys(username)
    password_box = driver.find_element(By.ID, 'password')
    password_box.send_keys(password)
    submit_button = driver.find_element(By.ID, 'submit')
    submit_button.click()

def change_date(driver, url, port, user_list, date):
    with tqdm(total=len(user_list), desc="Processing Users", unit="user") as pbar:
        for user in user_list:
            user_url = f'http://{url}:{port}/radiusmanager/admin.php?cont=edit_user&username={user}'
            driver.get(user_url)
            expiration_box = driver.find_element(By.ID, 'expiration')
            expiration_box.clear()
            expiration_box.send_keys(date)
            submit_button = driver.find_element(By.ID, 'submit')
            submit_button.click()
            pbar.set_description(f"Processing {user}")  # Display the current user name in the loading bar
            pbar.update(1)  # Update the loading bar for each iteration

if __name__ == '__main__':
    main()

