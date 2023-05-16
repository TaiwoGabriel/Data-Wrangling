import time, os, re
import pickle
import pandas as pd
from collections import defaultdict
from fastprogress import progress_bar
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from pathlib import Path
from concat_entries import update_logger
from selenium.common.exceptions import NoSuchElementException

curr_dir = os.path.dirname(os.path.realpath(__file__))
dwn_path = os.path.join(curr_dir, "MSCI_Reports")
logger_path = os.path.join(curr_dir, "logger.csv")
records_path = os.path.join(curr_dir, "dwn_map.pkl")

# Method to check if a download has finished or not
def is_download_finished():
    firefox_temp_file = sorted(Path(dwn_path).glob('*.part'))
    downloaded_files = sorted(Path(dwn_path).glob('*.*'))
    return len(firefox_temp_file) == 0 and len(downloaded_files) >= 1

# Method to get name of downloaded file
def getDownLoadedFileName():
    driver.get("about:downloads")
    return driver.execute_script("return document.querySelector('#contentAreaDownloadsView .downloadMainArea .downloadContainer description:nth-of-type(1)').value")

# Method to get total number of reports available in the page
def getResults(driver):
    s = driver.find_element(By.XPATH, "//div[@id='tbtext-1070']").text
    return int(re.findall(r'\d+', s)[0])

# Method to scroll on each record and download the esg report
def download_reports(driver):
    driver.get("https://esgdirect.msci.com/")
    delay = 120

    try:
        # Wait until all results are loaded
        _ = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, "tbtext-1070")))
        time.sleep(10)
        results = getResults(driver)
        dwn_map = defaultdict(list)
        last_id = -1 
        df = pd.read_csv(logger_path)
        df.drop(columns=["Unnamed: 0"], inplace=True)
        max_id = max(df["data-record-id"])
        last_id = 0 if max_id < 0 else max_id
        curr_id = 0 if max_id < 0 else last_id + 1

        
        scroll_len = last_id * 33

        # Scroll to the report that needs to be downloaded
        driver.execute_script('document.getElementById("gridview-1061").scrollTop = 0')
        driver.execute_script('document.getElementById("gridview-1061").scrollTop += '+str(scroll_len))
        sleep_time = (last_id // 500)*3
        time.sleep(sleep_time)

        # Assert that the when error was encountered, we restart from last id
        if last_id > 0:
            prev_dwn_map = None
            with open("dwn_map.pkl", "rb") as handle:
                prev_dwn_map = pickle.load(handle)
            prev_last_id = max(prev_dwn_map["data-record-id"])
            assert last_id == prev_last_id

        print(f"Starting from idx = {curr_id}")
        last_downloaded_id = -1

        for idx in progress_bar(range(curr_id, results)):
            
            add_scroll = 0 if idx == 0 else 33
            driver.execute_script('document.getElementById("gridview-1061").scrollTop += '+str(add_scroll))
            time.sleep(2)
            found = False
            try:
                # Find the table row
                table = driver.find_element(By.XPATH, "//table[@data-recordindex="+str(idx)+"]")

                # Get the clickable link and the name of the company. Remove special characters to save as file name.
                curr_row = table.find_element(By.XPATH, ".//span")
                comp_name = " ".join(re.sub('[^A-Za-z0-9\s]+', '', curr_row.text).split())
                rep_name = os.path.join(dwn_path,comp_name+" Report.pdf")
                curr_row.click()
                time.sleep(1)
                try:
                    report = driver.find_element(By.XPATH, "//*[text()='Download ESG Ratings Report']")
                    found = True
                    time.sleep(1)
                except NoSuchElementException as e:
                    report = driver.find_element(By.XPATH, "//*[text()='Download Industry Report']")
                    time.sleep(1)
                    raise NoSuchElementException("no report")
                report.click()
                time.sleep(10)

                # Wait until download is finished, once done, break and get the filename
                for _ in range(100):
                    if is_download_finished():
                        handles = list(driver.window_handles)
                        driver.switch_to.window(handles[1])
                        break
                    time.sleep(3)
                filename = getDownLoadedFileName()
                if filename is not None:
                    curr_name = os.path.join(dwn_path,filename)
                else:
                    raise NoSuchElementException("no report")
                driver.close()
                handles = list(driver.window_handles)
                assert len(handles) == 1
                driver.switch_to.window(handles[0])

                # As all reports are downloaded with generic name, rename it with the company's name
                os.rename(curr_name, rep_name)
                dwn_map["report"].append("Yes")
                dwn_map["tearsheet"].append("No")
                dwn_map["industry-report"].append("No")                
                dwn_map["data-record-id"].append(idx)
                dwn_map["name"].append(comp_name)
            except Exception as ee:
                dwn_map["report"].append("No")
                dwn_map["tearsheet"].append("No")
                dwn_map["industry-report"].append("No")                
                dwn_map["data-record-id"].append(idx)
                if found:
                    if "no report" in str(ee):
                        dwn_map["name"].append(f"{comp_name} -> found but report does not exist")
                    else:
                        dwn_map["name"].append(f"{comp_name} -> found but other error")
                else:
                    dwn_map["name"].append(f"{comp_name} -> not found")

            # Create a checkpoint in dwn_map.pkl for every 7 records downloaded
            last_downloaded_id = idx
            if idx > curr_id and idx%7 == 0:
                with open(records_path, 'wb') as handle:
                    pickle.dump(dwn_map, handle, protocol=pickle.HIGHEST_PROTOCOL)
                print(f"Checkpoint saved at idx = {idx}")
            time.sleep(2)

        return True

    # For any unknown exception, print it and create a checkpoint too.
    except Exception as e:
        print(e)
        if dwn_map is not None and "data-record-id" in dwn_map and len(dwn_map["data-record-id"]) > 0:
            with open(records_path, 'wb') as handle:
                pickle.dump(dwn_map, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"Failed at id = {last_downloaded_id}")
        return False
            

if __name__ == "__main__":

    # Set firefox options and download directory to MSCI_Reports/
    firefox_options = Options()
    firefox_options.set_preference("browser.download.alwaysOpenPanel", False)
    firefox_options.set_preference("browser.download.folderList", 2)
    firefox_options.set_preference("browser.download.dir", dwn_path)
    successfully_updated = True
    while successfully_updated:
        driver = webdriver.Firefox(options = firefox_options)
        driver.maximize_window()
        status_complete = download_reports(driver)
        if status_complete:
            break 
        driver.quit()
        time.sleep(3)

        # If error encountered, status will be false so update CSV files with latest checkpoint
        successfully_updated = update_logger()