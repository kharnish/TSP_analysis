from dotenv import load_dotenv
import os
from os.path import join
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time


class TSPInterface:
    def __init__(self, download_dir=os.getcwd()):
        self.download_dir = download_dir
        self.driver = None
        self.wait = None

    @staticmethod
    def load_driver(download_dir):
        """Load TSP web page

        :param download_dir: Default download directory
        """
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("prefs", {"download.default_directory": download_dir})
        driver = webdriver.Chrome(options=chrome_options)
        return driver, WebDriverWait(driver, 20)

    def login(self):
        """Log in to TSP"""
        # Load secret login strings
        load_dotenv()
        user = os.getenv("TSP_USER")
        password = os.getenv("TSP_PASS")
        mfa_key = os.getenv("TSP_MFA")

        # Load login URL
        url = 'https://www.tsp.gov/login/'
        self.driver.get(url)

        # Log in to TSP
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Acknowledge']"))).click()
        self.driver.find_element(by=By.NAME, value="username").send_keys(user)
        self.driver.find_element(by=By.NAME, value="password").send_keys(password)
        self.driver.find_element(by=By.ID, value="okta-signin-submit").click()
        self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "icon-dm"))).click()
        self.driver.find_element(by=By.XPATH, value="//a[text()='Security Question']").click()
        self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "password-with-toggle")))
        self.driver.find_element(by=By.CLASS_NAME, value="password-with-toggle").send_keys(mfa_key)
        time.sleep(2)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@class='button button-primary']"))).click()

    def scrape_contributions(self):
        """Download contributions CSV from the year to date"""
        # Instantiate driver
        self.driver, self.wait = self.load_driver(self.download_dir)

        # Log in to TSP to get contributions
        self.login()

        # Get contributions, waiting until page is fully loaded
        # The full XPATH is inconvenient, but so far is the only thing that I've found to work
        full_xpath = '/html/body/al-app/div[2]/app-page-host/div/al-primary-page/div/div/div/div/div[2]/div/worklife-' \
                     'home/div/div[1]/worklife-datacard-container-wc/div/div/worklife-datacard-retirementsavings-wc/' \
                     'worklife-datacard-template/section/div[4]/div[1]/div[2]/div[1]/div/a '
        self.wait.until(EC.element_to_be_clickable((By.XPATH, full_xpath))).click()

        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Account Activity']"))).click()
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Download']"))).click()
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='Download']"))).click()
        time.sleep(5)

        # Import contribution CSV
        csv_path = os.path.join(self.download_dir, 'InvestmentActivityDetail.csv')
        import_contributions(csv_path)
        self.driver.close()
        return csv_path

    def scrape_tsp_performance(self):
        """Scrape public TSP fund performance and append to personal Share_Prices.csv file"""
        # Instantiate driver
        self.driver, self.wait = self.load_driver(self.download_dir)

        # Load fund performance url
        url = 'https://www.tsp.gov/share-price-history/'
        self.driver.get(url)

        old_prices = pd.read_csv(os.path.join('resources', 'Share_Prices.csv'))

        # TODO Made the input date based on the last gotten share price
        # time.sleep(3)
        # self.driver.find_element(by=By.CLASS_NAME, value="date-range form-control input active").click()
        # self.driver.find_element(By.XPATH, "//input[@placeholder='Start Date..']").send_keys("2023-12-8")
        # self.driver.find_element(By.XPATH, "//*[@class='date-range form-control input']").click()#.send_keys("2023-12-8")
        # self.driver.find_element(by=By.ID, value="fundDateStart").click()#send_keys("2023-12-8")
        # self.driver.find_element(by=By.CLASS_NAME, value="usa-button").click()

        price_table = self.driver.find_element(by=By.ID, value="dynamic-share-price-table")

        d = [i.split('$') for i in price_table.text.split('\n')]
        cols = d[0][0][5:].split(' ')
        cols = ['date'] + [(' ').join(cols[i:i + 2]) for i in range(0, len(cols), 2)]
        df = pd.DataFrame(d[1:], columns=cols)
        df['date'] = pd.to_datetime(df['date'])
        for col in df.columns[1:]:
            df[col] = df[col].astype('float')

        # TODO add the updated prices and rewrite the table

        df_to_add = df[df['date'] > old_prices.iloc(0)['date']]

        self.driver.close()


def import_contributions(tsp_investment_activity_path):
    """
    Import InvestmentActivityDetail.csv file from TSP and personal contributions.csv file and append new
    contribution activity

    :param tsp_investment_activity_path:
    """
    contrib_file = pd.read_csv(join('resources', 'contributions.csv'))
    tsp_ia_file = pd.read_csv(tsp_investment_activity_path)
    ia_df = pd.DataFrame(columns=contrib_file.columns)
    for date, grp in tsp_ia_file.groupby('VALUATION DATE'):
        ia_row = {'Date': grp.values[0][0].replace('-', '/'),
                  'Traditional': grp[grp['ACTIVITY TYPE'] == 'Traditional']['AMOUNT'].sum(),
                  'Roth': grp[grp['ACTIVITY TYPE'] == 'Roth']['AMOUNT'].sum(),
                  'Automatic_1': grp[grp['ACTIVITY TYPE'] == 'Automatic (1%)']['AMOUNT'].sum(),
                  'Matching': grp[grp['ACTIVITY TYPE'] == 'Match']['AMOUNT'].sum(),
                  'Total': grp['AMOUNT'].sum()}
        for fund in contrib_file.columns[6:]:
            ia_row[fund] = grp[grp['FUND'] == fund]['FUND UNITS'].sum()
        ia_df = ia_df.append(ia_row, ignore_index=True)
        pass
    ia_df = ia_df.fillna(0)

    contrib_file2 = contrib_file.append(ia_df, ignore_index=True)
    contrib_file2.to_csv(join('resources', 'contributions2.csv'), index=False)
    pass


if __name__ == '__main__':
    tspi = TSPInterface()
    # iad_path = tspi.scrape_contributions()
    # import_contributions(iad_path)

    tspi.scrape_tsp_performance()
