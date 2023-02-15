import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
# from bs4 import BeautifulSoup
import time
import pandas as pd

LICENSETYPE = ["Pharmacist"]

def search(licenseType, letter):

    url = r'https://idbop.mylicense.com/verification/Search.aspx'

    driver = webdriver.Chrome()

    data = []

    driver.get(url)

    ddLicenseType = Select(driver.find_element(By.XPATH, '//*[@id="t_web_lookup__license_type_name"]'))
    ddLicenseType.select_by_visible_text(licenseType)

    driver.find_element(By.XPATH, '//*[@id="t_web_lookup__last_name"]').send_keys(letter)

    driver.find_element(By.XPATH, '//*[@id="sch_button"]').click()

    page = 1
    
    while True:
        results = openLink(driver)
        data.extend(results)
        page += 1
        nextLink = driver.find_elements(By.XPATH, f'//a[text()="{page}"]')
        if nextLink:
            nextLink[0].click()
            print(str(page))
        else:
            break       
    
    df = pd.DataFrame(data)

    df.to_csv("output.csv", encoding="utf-8-sig")
    # time.sleep(120)
    driver.quit()

def openLink(driver):


    tBody = driver.find_elements(By.XPATH, '//td[@rowspan="0"]')
    timeout = 60
    try:
        element_present = EC.presence_of_element_located((By.XPATH, '//*[@id="datagrid_results"]'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")
    
    results = []
    for link in tBody:
        aLink = link.find_element(By.TAG_NAME, 'a')
        aLink.click()
        print(aLink.text)
        
        try:
            element_present = EC.presence_of_element_located((By.XPATH, '//*[@id="TheForm"]/table/tbody/tr[2]/td[2]/table[2]'))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
        
        result = scraper(driver)
        results.append(result)
    
    return results

def scraper(driver):   
    
    driver.switch_to.window(driver.window_handles[1])
    dictFName = driver.find_element(By.XPATH, '//*[@id="_ctl27__ctl1_first_name"]').text
    dictMName = driver.find_element(By.XPATH, '//*[@id="_ctl27__ctl1_m_name"]').text
    dictLName = driver.find_element(By.XPATH, '//*[@id="_ctl27__ctl1_last_name"]').text
    dictLNumber = driver.find_element(By.XPATH, '//*[@id="_ctl36__ctl1_license_no"]').text
    dictLType = driver.find_element(By.XPATH, '//*[@id="_ctl36__ctl1_license_type"]').text
    dictStatus = driver.find_element(By.XPATH, '//*[@id="_ctl36__ctl1_status"]').text
    dictIssueD = driver.find_element(By.XPATH, '//*[@id="_ctl36__ctl1_issue_date"]').text
    dictExp = driver.find_element(By.XPATH, '//*[@id="_ctl36__ctl1_expiry"]').text
    dictRenew = driver.find_element(By.XPATH, '//*[@id="_ctl36__ctl1_last_ren"]').text
                
    data = {'First Name': dictFName, 'Middle Name': dictMName, 'Last Name': dictLName, 'License Number': dictLNumber, 'License Type': dictLType, 'Status': dictStatus, 'Original Issued Date': dictIssueD, 'Expiry': dictExp, 'Renewed': dictRenew}
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return data


if __name__ == "__main__":
    licenseType = input("What license type? ")
    letter = input("What letter? ")
    if licenseType in LICENSETYPE:
        search(licenseType, letter)
    else:
        print("License type not supported. ")