import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import scrapping_tools


def get_jobs(job_name: str, location: str, num_jobs: int) -> pd.DataFrame:
    """
    Glassdoor jobs scrapper

    returns: pd.DataFrame
    """
    # set up a Chrome webdriver
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    # set the URL for the Glassdoor job search page
    url = "https://www.glassdoor.com/Job/index.htm"

    # create an empty list to store the job listings
    jobs = []  # type: list[dict]

    # set the page number to 1
    page_number = 1

    # navigate to the Glassdoor job search page
    driver.get(url)

    # find the search bar on the page and enter the job name and location
    driver.find_element_by_id("KeywordSearch").send_keys(job_name)
    driver.find_element_by_id("LocationSearch").clear()
    driver.find_element_by_id("LocationSearch").send_keys(location)

    # click the search button to submit the search
    driver.find_element_by_id("HeroSearchButton").click()

    # loop through the job listings until the desired number of jobs is reached
    while len(jobs) < num_jobs:
        # if this is the first page, close the cookies popup
        if page_number == 1:
            scrapping_tools.click_popup(driver, "cookies")

        # close the signup popup
        scrapping_tools.click_popup(driver, "signup")

        # find all of the job listing buttons on the page and click the first one
        job_buttons = driver.find_elements_by_css_selector("li.react-job-listing")
        job_buttons[0].click()

        # close the login popup
        scrapping_tools.click_popup(driver, "login")

        # scrape the job data from the current job listing and add it to the jobs list
        jobs = scrapping_tools.scrap_data(driver, job_buttons, num_jobs, jobs)

        # try to click the "next page" button, and break the loop if it doesn't exist
        try:
            next_page_button = driver.find_element(
                By.CSS_SELECTOR, '[data-test="pagination-next"]'
            )
            next_page_button.click()

        except Exception:
            print("scrapped all pages")
            break

        # increase the page number counter and close the second signup popup
        page_number += 1
        scrapping_tools.click_popup(driver, "signup2")

    # print a success message and return the job listings as a pandas dataframe
    print(f"{len(jobs)} job listings scraped with success")
    return pd.DataFrame(jobs)


if __name__ == "__main__":
    df = get_jobs("data scientist intern", "us", 62)
    df.to_excel("output.xlsx")
