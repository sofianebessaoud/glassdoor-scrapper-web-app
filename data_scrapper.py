from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager


def get_jobs(keyword, num_jobs):
    '''Gathers jobs as a dataframe, scraped from Glassdoor'''

    # Change the path to where chromedriver is in your home folder.
    driver = webdriver.Chrome(ChromeDriverManager().install(),
                              options=webdriver.ChromeOptions())

    url = 'https://www.glassdoor.com/Job/' + keyword + '-jobs-SRCH_KO0,21.htm?'
    driver.get(url)
    jobs = []

    while len(jobs) < num_jobs:  # If true, should be still looking for new jobs.

        # cookies
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))).click()
        driver.get(url)

        # Test for the "Sign Up" prompt and get rid of it.
        try:
            driver.find_element_by_class_name("selected").click()
        except ElementClickInterceptedException:
            print("didn't work")
            pass

        # Going through each job in this page
        job_buttons = driver.find_elements_by_css_selector("li.react-job-listing")

        job_buttons[0].click()

        try:
            driver.find_element_by_css_selector("span[class='SVGInline modal_closeIcon']").click()
        except Exception:
            pass

        for job_button in job_buttons:
            print("Progress: {}".format("" + str(len(jobs)) + "/" + str(num_jobs)))
            if len(jobs) >= num_jobs:
                break

            job_button.click()  # You might
            time.sleep(1.2)

            company_name = driver.find_element_by_css_selector("div[class='css-87uc0g e1tk4kwz1']").text
            location = driver.find_element_by_css_selector("div[class='css-56kyx5 e1tk4kwz5']").text
            job_title = driver.find_element_by_css_selector("div[class='css-1vg6q84 e1tk4kwz4']").text
            job_description = driver.find_element_by_css_selector("div[class='css-jrwyhi e856ufb5']").text

            try:
                salary_estimate = driver.find_element_by_xpath(
                    '//*[@id="JDCol"]/div/article/div/div[1]/div/div/div[1]/div[3]/div[1]/div[4]/span').text
            except NoSuchElementException:
                salary_estimate = 'N/A'

            try:
                size = driver.find_element_by_css_selector("span[class='css-i9gxme e1pvx6aw2']").text
            except NoSuchElementException:
                size = 'N/A'

            try:
                industry = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[4]/span[2]').text
            except NoSuchElementException:
                industry = 'N/A'

            try:
                sector = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[5]/span[2]').text
            except NoSuchElementException:
                sector = 'N/A'

            try:
                revenue = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[6]/span[2]').text
            except NoSuchElementException:
                revenue = 'N/A'

            jobs.append({"Job Title": job_title,
                         "Salary Estimate": salary_estimate,
                         "Job Description": job_description,
                         "Company Name": company_name,
                         "Location": location,
                         "Size": size,
                         "Industry": industry,
                         "Sector": sector,
                         "Revenue": revenue})

        # Clicking on the "next page" button
        try:
            driver.find_element_by_xpath('.//li[@class="next"]//a').click()
        except NoSuchElementException:
            print("Scraping terminated before reaching target number of jobs. Needed {}, got {}.".format(num_jobs,
                                                                                                         len(jobs)))
            break

    return pd.DataFrame(jobs)  # This line converts the dictionary object into a pandas DataFrame.
