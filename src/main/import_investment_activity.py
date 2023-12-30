from os.path import join
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from dotenv import load_dotenv
import os


def scrape_contributions():
    """Download contributions CSV from the year to date

    :return:
    """
    # TODO Make it click the Contributions tab

    # Import secret from .env file
    load_dotenv()
    user = os.getenv("TSP_USER")
    password = os.getenv("TSP_PASS")
    mfa = os.getenv("TSP_MFA")

    # Load TSP webpage
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", {"download.default_directory": os.getcwd()})
    driver = webdriver.Chrome(options=chrome_options)
    url = 'https://www.tsp.gov/login/'
    driver.get(url)
    time.sleep(3)

    # Log in to TSP
    driver.find_element(by=By.XPATH, value="//button[text()='Acknowledge']").click()
    driver.find_element(by=By.NAME, value="username").send_keys(user)
    driver.find_element(by=By.NAME, value="password").send_keys(password)
    driver.find_element(by=By.ID, value="okta-signin-submit").click()
    time.sleep(3)
    driver.find_element(by=By.CLASS_NAME, value="icon-dm").click()
    driver.find_element(by=By.XPATH, value="//a[text()='Security Question']").click()
    time.sleep(1)
    driver.find_element(by=By.NAME, value="answer").send_keys(mfa)
    time.sleep(1)
    driver.find_element(by=By.XPATH, value="//*[@class='button button-primary']").click()
    time.sleep(15)

    # Get contributions
    # full_xpath = '/html/body/al-app/div[2]/app-page-host/div/al-primary-page/div/div/header/div/al-layout-header-wc/div/div/div/thrive-header-widget-wc/div/div/div[2]/div[1]/div[1]/div/ul/li[5]/span/a'
    # driver.find_element(by=By.XPATH, value=full_xpath).click()
    # driver.find_element(by=By.XPATH, value="//a[text()='Contributions']").click()

    # TODO get it to work regardless of window size
    #  options.add_argument("window-size=1200x600")
    # try:
    #     driver.find_element(by=By.ID, value="primary__3272f498_6961_431d_a2cb_848499a7113esptr58e0cd48_33a7_493c_a6f6_e46d599cca72").click()
    #     # driver.find_element(by=By.XPATH, value="//a[text()='Contributions']").click()
    #     # primary__3272f498_6961_431d_a2cb_848499a7113esptr58e0cd48_33a7_493c_a6f6_e46d599cca72
    #     time.sleep(1)
    # except:
    #     driver.find_element(by=By.ID, value="mob-menu-icon']").click()
    #     driver.find_element(by=By.XPATH, value="//a[text()='Contributions']").click()
    #     time.sleep(1)

    driver.find_element(by=By.XPATH, value="//a[text()='Account Activity']").click()
    time.sleep(2)
    driver.find_element(by=By.XPATH, value="//span[text()='Download']").click()
    time.sleep(1)
    driver.find_element(by=By.XPATH, value="//button[@title='Download']").click()
    time.sleep(3)

    # Import contribution CSV
    import_contributions(os.path.join(os.getcwd(), 'InvestmentActivityDetail.csv'))
    driver.close()


def import_contributions(tsp_investment_activity_path):
    """
    Import InvestmentActivityDetail.csv file from TSP and personal contributions.csv file and append new
    contribution activity

    :param tsp_investment_activity_path:
    :return:
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


def scrape_tsp_performance():
    """
    Scrape public TSP fund performance and append to personal Share_Prices.csv file

    :return:
    """
    current_prices = pd.read_csv(os.path.join('resources', 'Share_Prices.csv'))

    tsp_url = 'https://www.tsp.gov/share-price-history/'
    driver = webdriver.Chrome()
    driver.get(tsp_url)

    # TODO Made the input date based on the last gotten share price
    # driver.find_element(by=By.CLASS_NAME, value="date-range form-control input active").click()
    # driver.find_element(by=By.ID, value="fundDateStart").send_value("value", "2023-12-8")
    # driver.find_element(by=By.CLASS_NAME, value="usa-button").click()

    price_table = driver.find_element(by=By.ID, value="dynamic-share-price-table")

    d = [i.split('$') for i in price_table.text.split('\n')]
    cols = d[0][0][5:].split(' ')
    cols = ['date'] + [(' ').join(cols[i:i + 2]) for i in range(0, len(cols), 2)]
    df = pd.DataFrame(d[1:], columns=cols)
    df['date'] = pd.to_datetime(df['date'])
    for col in df.columns[1:]:
        df[col] = df[col].astype('float')

    # TODO add the updated prices and rewrite the table

    driver.close()

    print('done')


if __name__ == '__main__':
    import_contributions(os.path.join(os.getcwd(), 'InvestmentActivityDetail.csv'))

    # import_contributions()
    # scrape_tsp_performance()
    # grab_contributions()
