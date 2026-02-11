# Deploying FOIS Extractor to Streamlit Cloud

Streamlit Community Cloud is **free** and is the easiest way to host this application.

## 1. Prepare GitHub Repository
1.  Create a new repository on your [GitHub](https://github.com/).
2.  Upload the following files to the repository:
    -   `app.py`
    -   `requirements.txt`
    -   `packages.txt`

## 2. Deploy on Streamlit Cloud
1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Sign in with your GitHub account.
3.  Click **"New app"**.
4.  Select your new repository (`Repository`), branch (`Main`), and file path (`app.py`).
5.  Click **"Deploy"**.

## 3. Usage
-   The app will spin up (this takes a minute).
-   Once active, you can share the URL with your team.
-   **New Features**:
    -   Select **Query Type** (Outstanding or Matured).
    -   Select **Zone** from the dropdown.
    -   Select **Date Range** (Last 7/15/30 Days) for Matured Indents.
-   Click "Initialize", enter CAPTCHA, and download the Excel file.

## Important Note
-   Streamlit Cloud apps are public by default. If this data is sensitive, ensure you use Streamlit's "Private app" feature (you get 1 private app for free) or handle data carefully.
