# Amended code from @dddat1017
# https://github.com/dddat1017/Scraping-Youtube-Comments

# YouTubeTranscriptApi from https://github.com/jdepoix/youtube-transcript-api from @jdepoix

"""
Main script to scrape the comments of any Youtube video.

Example:
    $ python youtube_scraper.py YOUTUBE_VIDEO_URL
"""

import asyncio
# import glob
# import os
import sys
import time

import pandas as pd
from selenium import webdriver  # for webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.options import \
    Options  # for suppressing the browser
from youtube_transcript_api import YouTubeTranscriptApi


def scrape(url):
    scrape_comments(url)
    scrape_transcript(url)
    # merge_sheets()
    

# Method to scrape youtube comments and place into excel file
def scrape_comments(url):
    """
    Extracts the comments from the Youtube video given by the URL.

    Args:
        url (str): The URL to the Youtube video

    Raises:
        selenium.common.exceptions.NoSuchElementException:
        When certain elements to look for cannot be found
    """

    # Note: Download and replace argument with path to the driver executable.
    # Simply download the executable and move it into the webdrivers folder.
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome('./webdrivers/chromedriver', options=options)

    # Navigates to the URL, maximizes the current window, and
    # then suspends execution for (at least) 5 seconds (this
    # gives time for the page to load).
    driver.get(url)
    time.sleep(5)

    try:
        # Extract the elements storing the video title and
        # comment section.
        title = driver.find_element_by_xpath('//*[@id="container"]/h1/yt-formatted-string').text
        comment_section = driver.find_element_by_xpath('//*[@id="comments"]')
    except exceptions.NoSuchElementException:
        # Note: Youtube may have changed their HTML layouts for
        # videos, so raise an error for sanity sake in case the
        # elements provided cannot be found anymore.
        error = "Error: Double check selector OR "
        error += "element may not yet be on the screen at the time of the find operation"
        print(error)

    # Scroll into view the comment section, then allow some time
    # for everything to be loaded as necessary.
    driver.execute_script("arguments[0].scrollIntoView();", comment_section)
    time.sleep(7)

    # Scroll all the way down to the bottom in order to get all the
    # elements loaded (since Youtube dynamically loads them).
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        # Scroll down 'til "next load".
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

        # Wait to load everything thus far.
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # One last scroll just in case.
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

    try:
        # Extract the elements storing the usernames and comments.
        username_elems = driver.find_elements_by_xpath('//*[@id="author-text"]')
        comment_elems = driver.find_elements_by_xpath('//*[@id="content-text"]')
    except exceptions.NoSuchElementException:
        error = "Error: Double check selector OR "
        error += "element may not yet be on the screen at the time of the find operation"
        print(error)

    # print("VIDEO TITLE: " + title + "\n")

    usernames = [username.text for username in username_elems]
    comments = [comment.text for comment in comment_elems]

    # comments_df = pd.DataFrame(list(zip(usernames, comments)),
    #            columns =['commenter_username', 'comment_text'])

    comments_df = pd.DataFrame({
        'commenter_username': usernames,
        'comment_text': comments,
        })

    comments_df.to_excel(r'youtube_comments_output.xlsx', index = False)

    driver.close()


# Method to scrape youtube transcript and place into excel file
def scrape_transcript(url):
    video_id = url.split("watch?v=")[1]
    transcripts = YouTubeTranscriptApi.get_transcript(video_id)

    text = [transcripts['text'] for transcripts in transcripts]
    start_time = [transcripts['start'] for transcripts in transcripts]
    duration = [transcripts['duration'] for transcripts in transcripts]

    transcript_df = pd.DataFrame({
        'transcribed_text': text,
        'start_time': start_time,
        'duration': duration
        })

    transcript_df.to_excel(r'youtube_transcript_output.xlsx', index = False)


# Work in progress
# Method to merge both result output into one excel file with 2 sheets
# def merge_sheets():
#     writer = pd.ExcelWriter("youtube_scrape_output.xlsx")

#     for filename in glob.glob("*.xlsx"):
#         df_excel = pd.read_excel(filename, engine='openpyxl')

#         (_, f_name) = os.path.split(filename)
#         (f_short_name, _) = os.path.splitext(f_name)

#         df_excel.to_excel(writer, f_short_name, index=False)

#     writer.save()


if __name__ == "__main__":
    asyncio.run(scrape(sys.argv[1]))
