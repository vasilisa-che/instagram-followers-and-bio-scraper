import time
from random import randint
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException


def save_credentials(username, password):
    with open('credentials.txt', 'w') as file:
        file.write(f"{username}\n{password}")


def load_credentials():
    if not os.path.exists('credentials.txt'):
        return None

    with open('credentials.txt', 'r') as file:
        lines = file.readlines()
        if len(lines) >= 2:
            return lines[0].strip(), lines[1].strip()

    return None


def prompt_credentials():
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")
    save_credentials(username, password)
    return username, password


def login(bot, username, password):
    bot.get('https://www.instagram.com/accounts/login/')
    time.sleep(randint(1, 5))

    # Check if cookies need to be accepted
    try:
        element = bot.find_element(By.XPATH, "/html/body/div[4]/div/div/div[3]/div[2]/button")
        element.click()
    except NoSuchElementException:
        print("[Info] - Instagram did not require to accept cookies this time.")

    print("[Info] - Logging in...")
    username_input = WebDriverWait(bot, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    password_input = WebDriverWait(bot, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

    username_input.clear()
    username_input.send_keys(username)
    password_input.clear()
    password_input.send_keys(password)

    login_button = WebDriverWait(bot, 2).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    login_button.click()
    time.sleep(10)


def scrape_following(bot, username):
    bot.get(f'https://www.instagram.com/{username}/')
    # get the number of following accounts
    # following_elements = wait.until(ec.visibility_of_all_elements_located((By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[3]/a/span')))
    # following_number = int(following_elements[0].text)
    time.sleep(3.5)
    WebDriverWait(bot, TIMEOUT).until(ec.presence_of_element_located(
        (By.XPATH, "//a[contains(@href, '/followers')]"))).click()  # for following accounts change to '/following'
    time.sleep(randint(2, 8))

    # scroll the pop-up window with accounts
    scroll_box = bot.find_element(By.XPATH, '//div[@class="xyi19xy x1ccrb07 xtf3nb5 x1pc53ja x1lliihq x1iyjqo2 xs83m0k xz65tgg x1rife3k x1n2onr6"]')
    actions = ActionChains(bot)
    time.sleep(5)
    last_ht, ht = 0, 1  # height variable
    while last_ht != ht:
        last_ht = ht
        time.sleep(randint(10, 20))
        ht = bot.execute_script("""
                arguments[0].scrollTo(0, arguments[0].scrollHeight);
                return arguments[0].scrollHeight; """, scroll_box)
        time.sleep(randint(2, 8))

        actions.move_to_element(scroll_box).perform()
        time.sleep(5)

    users = set()

    print(f"[Info] - Scraping followers for {username}...")

    followers = bot.find_elements(By.XPATH, "//a[contains(@href, '/')]")

    for i in followers:
        time.sleep(1.5)
        if i.get_attribute('href'):
            users.add(i.get_attribute('href').split("/")[3])
        else:
            continue

        ActionChains(bot).send_keys(Keys.END).perform()
        time.sleep(1)

    users = list(users)

    print(f"[Info] - Saving followers for {username}...")
    # append accounts to the existing file – followers.txt
    with open(f'{username}_followers.txt', 'a') as file:
        file.write('\n'.join(users) + "\n")


def scrape():
    credentials = load_credentials()

    if credentials is None:
        username, password = prompt_credentials()
    else:
        username, password = credentials

    usernames = input("Enter the Instagram usernames you want to scrape (separated by commas): ").split(",")

    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Linux; Android 10; SM-G970F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36"}
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    bot = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    login(bot, username, password)

    for user in usernames:
        user = user.strip()
        scrape_following(bot, user)

    bot.quit()


if __name__ == '__main__':
    TIMEOUT = 15
    scrape()
