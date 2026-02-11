# 🚆 FOIS Data Extractor

A robust Streamlit application to automate data extraction from the Indian Railways FOIS (Freight Operations Information System) website.

## 🌟 Features

-   **Interactive CAPTCHA Handling**: Displays the live CAPTCHA from the FOIS portal for manual entry.
-   **Smart Querying**:
    -   **Outstanding ODR(s)**
    -   **Matured Indents** (with Date Ranges: Last 7, 15, or 30 days).
    -   **Zone Selection**: Support for all zones (CR, ECO, NR, WR, etc.).
-   **Resilient Automation**:
    -   Built with **Selenium** and **Chromedriver**.
    -   Uses "Eager" loading strategy for speed.
    -   Handles slow server responses with extended timeouts (up to 10 minutes).
    -   Safe extraction using JavaScript to prevent browser hangs.
-   **Instant Excel Export**: Converts the raw HTML data table into a clean, downloadable `.xlsx` file.

## 🛠️ Technology Stack

-   **Python 3.8+**
-   **Streamlit**: For the web interface.
-   **Selenium**: For browser automation.
-   **Pandas**: For data parsing and Excel generation.

## 🚀 How to Run Locally

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/fois-data-extractor.git
    cd fois-data-extractor
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

4.  **Use**:
    -   Open `http://localhost:8501` in your browser.
    -   Select your parameters.
    -   Click "Initialize".
    -   Enter CAPTCHA and Submit.

## 📦 Deployment (Streamlit Cloud)

This app is ready for [Streamlit Community Cloud](https://streamlit.io/cloud):
1.  Push this code to a public GitHub repository.
2.  Login to Streamlit Cloud.
3.  Click "New App" and select your repository.
4.  Deploy! (The `packages.txt` file handles the Chrome installation automatically).

## ⚠️ Note
This tool is for internal use to facilitate data access. Please respect the FOIS website's usage policies.
