import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import re
import pandas as pd


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
    time.sleep(2)

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


def scrape_description(bot, username):
    bot.get(f'https://www.instagram.com/{username}/')

    print(f"[Info] - Scraping description for {username}...")
    time.sleep(5)

    user_description = dict()

    # check the account bio
    try:
        description = bot.find_element(By.TAG_NAME, 'h1').text.lower()
    except:
        description = ''

    # check the link in bio
    link = ''
    try:
        html_source = bot.page_source
        urls = re.findall(r'href=[\'"]?([^\'" >]+)', html_source)
        for url in urls:
            if re.match(r'https://l\.instagram\.com/\?u=(.*)', url):
                link = url
                break
    except:
        link = ''

    # words (in lower case) you need to find in the bio or link
    word_list = ['journalist', 'reporter', 'correspondent', 'editor', 'news', 'columnist', 'writer', 'commentator',
                 'blogger', 'reviewer']

    df_descriptions = pd.read_csv('descriptions.csv', encoding="utf-8")

    # look for words from the list in the bio or link, if there is a match, add that account to the csv file
    for word in word_list:
        if (word in description) or (word in link):
            user_description['username'] = [username]
            user_description['description'] = [description]
            user_description['link'] = [link]
            df_user = pd.DataFrame.from_dict(user_description)
            df_descriptions = pd.concat([df_descriptions, df_user])
            break

    print(f"[Info] - Saving descriptions for {username}...")

    df_descriptions.to_csv('descriptions.csv', encoding='utf-8', index=False)
    time.sleep(10)


def scrape():
    credentials = load_credentials()

    if credentials is None:
        username, password = prompt_credentials()
    else:
        username, password = credentials

    usernames = input("Enter the Instagram usernames you want to scrape (separated by commas): ").split(",")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/90.0.1025.166 Mobile Safari/535.19"}
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    bot = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    login(bot, username, password)

    df = pd.DataFrame({'username': [], 'description': [], 'link': []})
    df.to_csv('descriptions.csv', encoding='utf-8', index=False)

    for user in usernames:
        user = user.strip()
        time.sleep(5)
        scrape_description(bot, user)

    bot.quit()


if __name__ == '__main__':
    TIMEOUT = 15
    scrape()
