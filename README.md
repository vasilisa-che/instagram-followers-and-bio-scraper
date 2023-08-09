# Instagram followers and bio scraper

This is a modified version of the Instagram parser used for scraping followers. The source repository can be found at: https://github.com/redianmarku/instagram-follower-scraper

## Changes

1. Fixes implemented to support selenium 4.11.2.
2. Added code for pop-up window scrolling (adapted from this code: https://github.com/chenchih/Python-Project/tree/main/Selenium/Instagram-crawl/1.GetFollowing_FollowerList).
3. Added functionality for scraping Instagram account bios.

## Bio scraper

This script checks whether the account bio (profile description) or the link in bio contain words from your list.
To begin, you should edit the list with the words you are interested in. Then run the script using the following command: python bio-scraper.py. You will be prompted to input the Instagram usernames you wish to scrape.
Any users whose bios or links contain matching words will be automatically appended to a CSV file.
