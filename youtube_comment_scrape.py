'''
Helper for Comments Scraping

Requirements:
- Excel sheet named 'youtube_input.xlsx' with columns 'Channel', 'Type', 'Year' and 'Link'


What it does:
- Calls comment scraping functions
- Saves output as excel file
'''

# Import required packages
# Basic Python Packages
import asyncio
import os
import re
import sys
import time
from typing import DefaultDict

# External Packages
import lxml
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver  # for webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Method to scrape youtube comments
# Output: dataframe
def scrape_comments(channel, channel_type, year, link):
    '''
    Extracts the comments from the Youtube video given by the URL.

    Args:
        channel (str): The channel name
        channel_type (str): The type of channel
        year (str): Year that the Youtube video was uploaded
        link (str): The URL to the Youtube video

    Raises:
        selenium.common.exceptions.NoSuchElementException:
        When certain elements to look for cannot be found
    '''

    # Note: Download and replace argument with path to the driver executable.
    # Simply download the executable and move it into the webdrivers folder.
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('./chromedriver', options=options)

    # Navigates to the URL, maximizes the current window, and
    # then suspends execution for (at least) 5 seconds (this
    # gives time for the page to load).
    driver.get(link)
    time.sleep(5)

    try:
        comment_section = driver.find_element_by_xpath('//*[@id="comments"]')
    except exceptions.NoSuchElementException:
        # Note: Youtube may have changed their HTML layouts for
        # videos, so raise an error for sanity sake in case the
        # elements provided cannot be found anymore.
        error = 'Error: Double check selector OR '
        error += 'element may not yet be on the screen at the time of the find operation'
        print(error)

    # Scroll all the way down to the bottom 5 times in order to get all the
    # elements loaded (since Youtube dynamically loads them).
    for i in range(5):
        driver.execute_script(
            'window.scrollTo(0, document.documentElement.scrollHeight);')
    time.sleep(4)

    try:
        # Extract the elements storing the usernames and comments.
        username_elems = driver.find_elements_by_xpath(
            '//*[@id="author-text"]')
        comment_elems = driver.find_elements_by_xpath(
            '//*[@id="content-text"]')
    except exceptions.NoSuchElementException:
        error = 'Error: Double check selector OR '
        error += 'element may not yet be on the screen at the time of the find operation'
        print(error)

    comments_df = pd.DataFrame({
        'Channel': [channel] * len(username_elems),
        'Type': [channel_type] * len(username_elems),
        'Year': [year] * len(username_elems),
        'commenter_username': [username.text for username in username_elems],
        'comment_text': [comment.text for comment in comment_elems],
        'url': [link] * len(username_elems)
    })

    driver.close()
    return comments_df


input_df = pd.read_excel(r'./youtube_input.xlsx')
comments_df = pd.DataFrame()

for i, v in input_df.iterrows():
    print(i, v)
    new_df = scrape_comments(v['Channel'], v['Type'], v['Year'], v['Link'])
    if new_df is not None:
        comments_df = pd.concat([comments_df, new_df])
    else:
        continue

comments_df.reset_index(drop=True, inplace=True)
comments_df.head()

comments_df.to_excel(r'youtube_comments_output.xlsx', index=False)
