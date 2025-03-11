# # src/fetch_data/fetch_data.py
#
# import logging
# from selenium import webdriver
# from selenium.webdriver.common.by import By  # Import necessary Selenium modules
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service as ChromeService
# from src.utils.logger import setup_logger
#
#
# logger = setup_logger(__name__) # Use the logger already configured
#
#
# def setup_webdriver():
#     """
#     Sets up and returns a Selenium WebDriver instance.
#
#     Returns:
#         webdriver.Chrome: A Selenium WebDriver instance, or None on failure.
#     """
#     try:
#         logger.info("Setting up WebDriver...")
#         # Use ChromeDriverManager to automatically download and manage ChromeDriver
#         service = ChromeService(executable_path=ChromeDriverManager().install())
#         driver = webdriver.Chrome(service=service)
#         logger.info("WebDriver initialized successfully.")
#         return driver
#     except Exception as e:
#         logger.error(f"Error initializing WebDriver: {e}")
#         return None
#
#
# def navigate_to_group(driver, group_url):
#     """
#     Navigates the WebDriver to the specified Facebook Group URL.
#
#     Args:
#         driver: Selenium WebDriver instance.
#         group_url: URL of the Facebook group.
#
#     Returns:
#         bool: True if navigation was successful, False otherwise.
#     """
#     pass  # Implementation will be added later
#
#
# def identify_user_posts(driver, user_id):
#     """
#     Identifies and returns Selenium WebElement objects representing posts
#     made by the specified user on the current Facebook group page.
#
#     Args:
#         driver: Selenium WebDriver instance.
#         user_id: Facebook User ID of the target user.
#
#     Returns:
#         list[WebElement]: A list of Selenium WebElement objects representing user posts.
#                           Returns an empty list if no posts are found or on error.
#     """
#     pass  # Implementation will be added later
#
#
# def extract_post_data(post_element):
#     """
#     Extracts relevant data (text, timestamp, reactions, comments) from a
#     single Selenium WebElement representing a Facebook post.
#
#     Args:
#         post_element: Selenium WebElement object representing a Facebook post.
#
#     Returns:
#         dict: A dictionary containing the extracted post data.
#               Returns None if data extraction fails for this post.
#     """
#     pass  # Implementation will be added later
#
#
# def fetch_user_posts(group_url, user_id):
#     """
#     Orchestrates the entire process of fetching user posts from a Facebook group
#     using Selenium. This is the main function to be called from outside this module.
#
#     Args:
#         group_url: URL of the Facebook group.
#         user_id: Facebook User ID of the target user.
#
#     Returns:
#         list[dict]: A list of dictionaries, where each dictionary represents a post
#                      and contains extracted data. Returns an empty list on failure.
#     """
#     pass  # Implementation will orchestrate calls to other functions
#
#
# if __name__ == "__main__":
#     # Example usage (for testing) - Keep this for now
#     group_url = "YOUR_FACEBOOK_GROUP_URL_HERE"
#     user_id = "YOUR_FACEBOOK_USER_ID_HERE"
#
#     driver = setup_webdriver()
#     if driver:
#         posts = fetch_user_posts(group_url, user_id)
#         if posts:
#             print("Extracted Posts:")
#             for post in posts:
#                 print(post)
#         else:
#             print("No posts fetched or an error occurred.")
#         # driver.quit() # Uncomment to close the browser after execution in final version


# from src.utils.logger import setup_logger
#
# logger = setup_logger(__name__)
#
# logger.info("Import and logger setup successful!")

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # Change to False for visual browser
    page = browser.new_page()
    page.goto('https://example.com')
    print(page.title())
    browser.close()