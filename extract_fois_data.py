
import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Initializes the Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Commented out to see the browser
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def main():
    driver = setup_driver()
    try:
        url = "https://www.fois.indianrail.gov.in/FOISWebPortal/pages/FWP_ODROtsgDtls.jsp"
        print(f"Navigating to {url}...")
        driver.get(url)

        wait = WebDriverWait(driver, 20)

        # 1. Select "Outstanding ODR(s)"
        print("Locating 'Outstanding ODR(s)' radio button...")
        try:
            # Try finding by label text
            outstanding_odr_radio = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//label[contains(text(), 'Outstanding ODR')]/preceding-sibling::input[@type='radio'] | //input[@type='radio' and @value='O'] | //td[contains(text(), 'Outstanding ODR')]//input")
            ))
            if not outstanding_odr_radio.is_selected():
                outstanding_odr_radio.click()
                print("Selected 'Outstanding ODR(s)'.")
            else:
                print("'Outstanding ODR(s)' is already selected.")
        except Exception as e:
            print(f"Warning: Could not specifically select 'Outstanding ODR(s)' radio. It might be default or the selector failed. \nError: {e}")

        # 2. Select Zone "ECO"
        print("Locating Zone dropdown...")
        try:
            # Look for a select element that contains "ECO" option
            zone_dropdown_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "select")))
            
            # If there are multiple selects, we might need to be more specific. 
            # For now, let's try to find the one that has "CR" (default) or "ECO".
            select = Select(zone_dropdown_element)
            
            # Debug: print options to be sure
            # options = [o.text for o in select.options]
            # print(f"Dropdown options found: {options[:5]}...")

            select.select_by_value('ECO') 
            print("Selected Zone 'ECO'.")
        except Exception as e:
            print(f"Could not select 'ECO' by value. Trying by visible text...")
            try:
                select.select_by_visible_text('ECO')
                print("Selected Zone 'ECO' by text.")
            except Exception as e2:
                 print(f"Error selecting Zone: {e2}")

        # 3. Handling CAPTCHA
        print("\nPlease look at the browser window causing the CAPTCHA image.")
        captcha_input = input("Enter the CAPTCHA text shown in the browser: ")

        print("Locating CAPTCHA input field...")
        # Assuming the input is near the captcha image or by name/id. 
        # Common IDs/Names: 'txtCaptcha', 'captcha', 'securityCode'. 
        # Since I can't see the source, I'll try generic input text fields.
        try:
             # Try identifying the input field. 
             # Usually the captcha input is type='text' and often has a max length or specific class.
             # We can try to find the input that is empty and visible.
            captcha_box = driver.find_element(By.ID, "txtCaptcha") # Common guess
        except:
            try:
                 captcha_box = driver.find_element(By.NAME, "txtCaptcha")
            except:
                 # Fallback: find all text inputs and ask user which one or pick the most likely (e.g. following the zone dropdown)
                 inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                 print(f"Found {len(inputs)} text inputs. Using the last one (often captcha).")
                 captcha_box = inputs[-1]
        
        captcha_box.clear()
        captcha_box.send_keys(captcha_input)
        print("Entered CAPTCHA.")

        # 4. Submit
        print("Locating Submit button...")
        try:
            submit_btn = driver.find_element(By.XPATH, "//input[@type='button' and @value='Submit'] | //button[text()='Submit']")
            submit_btn.click()
            print("Clicked Submit.")
        except Exception as e:
            print(f"Error finding Submit button: {e}")
            # Try JavaScript click if standard click fails
            try:
                print("Attempting JavaScript click...")
                driver.execute_script("arguments[0].click();", submit_btn)
            except:
                 pass

        # 5. Extract Data
        print("Waiting for data table to load...")
        time.sleep(10) # wait for iframe load
        
        try:
            print("Switching to results iframe...")
            # Switch to the iframe where results are loaded
            driver.switch_to.frame("frmDtls")
            
            from io import StringIO
            # Locate table by ID or tag
            # We will grab the page source and use pandas
            dfs = pd.read_html(StringIO(driver.page_source))
            
            # Filter for the correct table. It likely has many rows or specific headers.
            # We'll save the largest table found.
            target_df = None
            max_rows = 0
            
            for i, df in enumerate(dfs):
                print(f"Table {i}: {df.shape} shape")
                if df.shape[0] > max_rows:
                    max_rows = df.shape[0]
                    target_df = df
            
            if target_df is not None:
                output_file = "fois_data.xlsx"
                try:
                    target_df.to_excel(output_file) # Default index=True handles MultiIndex columns
                except:
                     # Fallback: flatten columns
                    target_df.columns = [' '.join(map(str, col)).strip() if isinstance(col, tuple) else col for col in target_df.columns]
                    target_df.to_excel(output_file, index=False)
                print(f"Data successfully saved to {output_file}")
            else:
                print("No data tables found in the response.")
                if "WE ARE UNABLE TO PROCESS YOUR REQUEST CURRENTLY" in driver.page_source:
                    print("Server Error detected: 'WE ARE UNABLE TO PROCESS YOUR REQUEST CURRENTLY'.")
                
                with open("debug_iframe_source.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print("Saved debug_iframe_source.html for inspection.")
                
            # Switch back to default content if needed later
            driver.switch_to.default_content()

        except Exception as e:
            print(f"Error extracting data: {e}")
            with open("debug_error_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Saved debug_error_page.html")


    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        input("Press Enter to close the browser...")
        driver.quit()

if __name__ == "__main__":
    main()
