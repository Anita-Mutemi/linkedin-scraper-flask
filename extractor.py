from selenium import webdriver  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore
from bs4 import BeautifulSoup as bs
import re
import time
from threading import Lock

# Initialize Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--log-level=3")  # Suppress console logs

# LinkedIn Credentials
email = "anitajehu13@gmail.com"
password = "0714676921akm"

# URL of the LinkedIn Page you want to scrape

scraped_data = []
data_lock = Lock()


def get_linkedin_data(user_id):
    global scraped_data
    # Access WebDriver
    browser = webdriver.Chrome(options=chrome_options)
    page = f"https://www.linkedin.com/in/{user_id}/recent-activity/all/"

    try:
        # Open login page
        browser.get(
            "https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin"
        )

        # Enter login info
        elementID = browser.find_element(By.ID, "username")
        elementID.send_keys(email)
        elementID = browser.find_element(By.ID, "password")
        elementID.send_keys(password)
        elementID.submit()

        # Wait for login to complete
        time.sleep(5)

        # Verify login was successful
        if "feed" not in browser.current_url:
            raise Exception("Login failed")

        # Go to posts page
        post_page = page + "/posts"
        post_page = post_page.replace("//posts", "/posts")
        browser.get(post_page)

        # Scroll the page to load all posts
        SCROLL_PAUSE_TIME = 1.5
        MAX_SCROLLS = 10

        SCROLL_COMMAND = "window.scrollTo(0, document.body.scrollHeight);"
        GET_SCROLL_HEIGHT_COMMAND = "return document.body.scrollHeight"

        last_height = browser.execute_script(GET_SCROLL_HEIGHT_COMMAND)
        scrolls = 0
        no_change_count = 0

        while True:
            browser.execute_script(SCROLL_COMMAND)
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = browser.execute_script(GET_SCROLL_HEIGHT_COMMAND)

            no_change_count = no_change_count + 1 if new_height == last_height else 0
            if no_change_count >= 3 or (MAX_SCROLLS and scrolls >= MAX_SCROLLS):
                break

            last_height = new_height
            scrolls += 1

        # Collect page source and parse it
        company_page = browser.page_source
        linkedin_soup = bs(
            company_page.encode("utf-8"), "html.parser"
        )  # Add parser argument
        containers = linkedin_soup.find_all("div", {"class": "feed-shared-update-v2"})
        containers = [
            container
            for container in containers
            if "activity" in container.get("data-urn", "")
        ]

        # print ('containers', containers)

        # Extract required data
        posts_data = []

        for container in containers:
            post_id = container.get("data-urn")
            user_id = (
                container.find("div", {"class": "update-components-actor__container"})
                .find("a")
                .get("href")
                .split("/")[-1].split("?")[0]
            )
            reactions_element = container.find_all(
                lambda tag: tag.name == "button"
                and "aria-label" in tag.attrs
                and "reaction" in tag["aria-label"].lower()
            )
            reactions_idx = 1 if len(reactions_element) > 1 else 0
            likes = (
                reactions_element[reactions_idx].text.strip()
                if reactions_element
                and reactions_element[reactions_idx].text.strip() != ""
                else "0"
            )
            likes = int(re.sub("[^0-9]", "", likes))

            posts_data.append({"post_id": post_id, "user_id": user_id, "likes": likes})
            # break

            if len(posts_data) == 3:
                break

        with data_lock:
            scraped_data = posts_data

        print ('scraped_data', scraped_data)

    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        browser.quit()

def start_scraping():
    while True:
        get_linkedin_data()
        time.sleep(3600)  # Run every hour
