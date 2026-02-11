
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import pandas as pd
import time
import os
import shutil
from io import BytesIO, StringIO

# Page Config
st.set_page_config(page_title="FOIS Data Extractor", page_icon="🚆", layout="wide")

st.title("🚆 FOIS Data Extractor")
st.markdown("""
This tool automates data extraction from the [FOIS Website](https://www.fois.indianrail.gov.in/FOISWebPortal/pages/FWP_ODROtsgDtls.jsp).
**Instructions:**
1. Configure your query (Type, Zone, Period).
2. Click **Initialize & Load CAPTCHA**.
3. Enter the CAPTCHA code shown in the screenshot.
4. Click **Submit & Extract**.
""")

# --- Helper Functions ---

def get_driver():
    """Initializes and returns a headless Chrome driver with Cloud support."""
    options = Options()
    options.add_argument("--headless") # Standard headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222") # Critical for cloud
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1920,1080")
    
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-features=NetworkService")
    options.add_argument("--page-load-strategy=none") 
    
    # Cloud Environment Specifics
    try:
        # Check standard Streamlit Cloud paths
        chromium_path = "/usr/bin/chromium"
        driver_path = "/usr/bin/chromedriver"
        
        if os.path.exists(chromium_path) and os.path.exists(driver_path):
            options.binary_location = chromium_path
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            # Fallback (Native Manager)
            driver = webdriver.Chrome(options=options)
            
        driver.set_page_load_timeout(600) 
        driver.set_script_timeout(600)
        
        # CRITICAL FIX: Increase internal socket timeout
        try:
            driver.command_executor.set_timeout(600)
        except:
            pass # Newer selenium versions might handle this differently
            
    except Exception as e:
        raise e
        
    return driver

# --- Session State Management ---

if 'driver_active' not in st.session_state:
    st.session_state.driver_active = False

if 'driver' not in st.session_state:
    st.session_state.driver = None

# --- UI Logic ---

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Configuration")
    
    # Query Type
    query_type = st.radio(
        "Select Query Type:",
        options=["Outstanding ODR(s)", "Matured Indents (Last 30 Days)"],
        index=0
    )
    
    # Zone
    zone_options = [
        "CR", "DFCR", "EC", "ECO", "ER", "KR", "NC", "NE", "NF", 
        "NPLR", "NR", "NW", "SC", "SE", "SEC", "SR", "SW", "WC", "WR"
    ]
    selected_zone = st.selectbox("Select Zone:", zone_options, index=3) # Default ECO
    
    # Period (Conditional)
    selected_period_val = None
    if query_type == "Matured Indents (Last 30 Days)":
        period_days = st.radio(
            "Select Period:",
            options=["Last 7 Days", "Last 15 Days", "Last 30 Days"],
            index=0
        )
        period_map = {"Last 7 Days": "7", "Last 15 Days": "15", "Last 30 Days": "30"}
        selected_period_val = period_map[period_days]

    st.write("---")

    if st.button("Initialize & Load CAPTCHA", type="primary"):
        with st.spinner("Initializing Browser..."):
            try:
                # Close existing
                if st.session_state.driver:
                    try:
                        st.session_state.driver.quit()
                    except:
                        pass
                    st.session_state.driver = None
                
                st.session_state.driver = get_driver()
                driver = st.session_state.driver
                
                url = "https://www.fois.indianrail.gov.in/FOISWebPortal/pages/FWP_ODROtsgDtls.jsp"
                driver.get(url)
                
                wait = WebDriverWait(driver, 15)
                
                # A. Select Query Type
                try:
                    if query_type == "Outstanding ODR(s)":
                        selector = "input[value='ODR_RK_OTSG']"
                    else:
                        selector = "input[value='MATURED_INDENTS']"
                    
                    radio_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    if not radio_btn.is_selected():
                        radio_btn.click()
                        time.sleep(1)
                except Exception as e:
                    st.warning(f"Note: Could not select Query Type (might be default). Error: {e}")

                # B. Select Zone
                try:
                    zone_dropdown = wait.until(EC.presence_of_element_located((By.TAG_NAME, "select")))
                    select = Select(zone_dropdown)
                    select.select_by_value(selected_zone)
                except:
                    try:
                        select.select_by_visible_text(selected_zone)
                    except Exception as e:
                        st.error(f"Failed to select Zone {selected_zone}: {e}")

                # C. Select Period
                if selected_period_val:
                    try:
                        period_rad = driver.find_element(By.CSS_SELECTOR, f"input[name='Optn'][value='{selected_period_val}']")
                        if not period_rad.is_selected():
                            period_rad.click()
                    except Exception as e:
                        st.warning(f"Could not select Period: {e}")

                # Screenshot
                time.sleep(2)
                screenshot = driver.get_screenshot_as_png()
                st.session_state.captcha_image = screenshot
                st.session_state.driver_active = True
                st.success("Page Loaded!")
                
            except Exception as e:
                st.error(f"Initialization Error: {e}")
                if st.session_state.driver:
                    st.session_state.driver.quit()
                    st.session_state.driver = None

with col2:
    st.subheader("2. Action")
    if st.session_state.driver_active and 'captcha_image' in st.session_state:
        st.image(st.session_state.captcha_image, caption="Current Page Screenshot", use_container_width=True)
        
        with st.form("captcha_form"):
            col_caps, col_sub = st.columns([2, 1])
            with col_caps:
                captcha_text = st.text_input("Enter CAPTCHA:", placeholder="Type code from image")
            with col_sub:
                st.write("") # Spacer
                st.write("")
                submit_button = st.form_submit_button("Submit & Extract")
            
        if submit_button and captcha_text:
            driver = st.session_state.driver
            if not driver:
                st.error("Browser session lost.")
            else:
                with st.spinner("Extracting data..."):
                    try:
                        # 1. Enter CAPTCHA
                        try:
                            try:
                                captcha_box = driver.find_element(By.ID, "txtCaptcha")
                            except:
                                captcha_box = driver.find_element(By.NAME, "txtCaptcha")
                            captcha_box.clear()
                            captcha_box.send_keys(captcha_text)
                        except:
                            inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                            if inputs:
                                inputs[-1].send_keys(captcha_text)
                        
                        # 2. Click Submit
                        try:
                            submit_btn = driver.find_element(By.XPATH, "//input[@type='button' and @value='Submit'] | //button[text()='Submit']")
                            submit_btn.click()
                        except:
                            driver.execute_script("arguments[0].click();", submit_btn)

                        # 3. Wait & Extract
                        time.sleep(5) # Valid wait for server to start processing
                        
                        # Define wait (fix for NameError)
                        wait = WebDriverWait(driver, 300)

                        if "WE ARE UNABLE TO PROCESS YOUR REQUEST CURRENTLY" in driver.page_source:
                            st.error("FOIS Server Error: Unable to process request. Please try again.")
                        else:
                            try:
                                # Switch to iframe
                                wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "frmDtls")))
                                
                                # Use JS to get content (faster/safer than page_source)
                                # Wait for table to be present inside iframe
                                try:
                                    wait.until(
                                        EC.presence_of_element_located((By.TAG_NAME, "table"))
                                    )
                                except:
                                    st.warning("Table might not have loaded fully, attempting extraction anyway...")

                                html_content = driver.execute_script("return document.body.innerHTML;")
                                
                                dfs = pd.read_html(StringIO(html_content))
                                target_df = None
                                max_rows = 0
                                for df in dfs:
                                    if df.shape[0] > max_rows:
                                        max_rows = df.shape[0]
                                        target_df = df
                                
                                if target_df is not None:
                                    st.success(f"Success! Extracted {target_df.shape[0]} rows.")
                                    
                                    # Clean Columns
                                    try:
                                        target_df.columns = [' '.join(map(str, col)).strip() if isinstance(col, tuple) else col for col in target_df.columns]
                                    except:
                                        pass
                                    
                                    # Preview Data (User Request)
                                    st.write("### Data Preview")
                                    st.dataframe(target_df.head(50), use_container_width=True)

                                    # Excel Download
                                    output = BytesIO()
                                    target_df.to_excel(output, index=False)
                                    output.seek(0)
                                    
                                    st.download_button(
                                        label="📥 Download Excel File",
                                        data=output,
                                        file_name="fois_data.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        type="primary"
                                    )
                                else:
                                    st.error("No data found. Check CAPTCHA.")
                                
                                driver.switch_to.default_content()
                            except Exception as e:
                                st.error(f"Extraction Error (Iframe): {e}")

                    except Exception as e:
                        st.error(f"Execution Error: {e}")

if st.sidebar.button("Reset / Close Browser"):
    if st.session_state.driver:
        st.session_state.driver.quit()
        st.session_state.driver = None
    st.session_state.driver_active = False
    st.rerun()
