from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.webelement import WebElement

import scrapping_url
from scrapping_url import info_url


def click_popup(driver, category: str) -> None:
    """
    Popups clicker to keep scrapping & avoid errors due to cookies, sign-in & sign-up alerts

    returns: None.
    """
    if category == "cookies":
        try:
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            ).click()
        except Exception:
            driver.refresh()
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            ).click()
    elif category == "signup":
        try:
            driver.find_element_by_class_name("selected").click()
        except Exception:
            pass

    elif category == "login":
        try:
            driver.find_element_by_css_selector(
                "span[class='SVGInline modal_closeIcon']"
            ).click()
            print("it activated")
        except Exception:
            print("not triggered")
            pass

    elif category == "signup2":
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="JAModal"]/div/div[2]/span')
                )
            ).click()
        except Exception:
            pass

    return


def try_load(driver, category: str) -> str:
    """
    Function used to scrap every category of the job offer

    returns: str
    """
    if category in ["company_name", "location", "job_title", "job_description"]:
        if category == "company_name":
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, info_url[category])
                    )
                )
                result = driver.find_element_by_css_selector(info_url[category]).text
            except Exception:
                result = "nan"
        else:
            try:
                result = driver.find_element_by_css_selector(info_url[category]).text
            except Exception:
                result = "nan"

            return result
    else:
        try:
            result = driver.find_element_by_xpath(info_url[category]).text

        except Exception:
            result = "nan"
    return result


def scrap_data(
    driver, job_buttons: list[WebElement], num_jobs: int, jobs: list[dict]
) -> list[dict]:
    """
    Main function called by scraper.py. It iterates through all the job offers and
    keep track of the data scrapped.

    returns: list.
    """
    for i in range(len(job_buttons)):
        print("Progress: {}".format("" + str(len(jobs)) + "/" + str(num_jobs)))

        if len(jobs) >= num_jobs:
            break

        job_buttons = driver.find_elements_by_css_selector("li.react-job-listing")

        try:
            job_buttons[i].click()
        except Exception:
            click_popup(driver, "login")
            job_buttons[i].click()

        additional_info = {}

        for category in scrapping_url.info_url.keys():
            additional_info[category] = try_load(driver, category)

        jobs.append(additional_info)

    return jobs
