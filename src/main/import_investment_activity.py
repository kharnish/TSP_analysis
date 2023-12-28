from os.path import join
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By


def import_contributions():
    contrib_file = pd.read_csv(join('resources', 'contributions.csv'))
    tsp_ia_file = pd.read_csv(join('resources', 'InvestmentActivityDetail.csv'))
    ia_df = pd.DataFrame(columns=contrib_file.columns)
    for date, grp in tsp_ia_file.groupby('VALUATION DATE'):
        ia_df = ia_df.append({'Date': grp.values[0][0].replace('-', '/'),
                              'Traditional': grp[grp['ACTIVITY TYPE'] == 'Automatic (1%)']['AMOUNT'].sum(),
                              'Roth': grp[grp['ACTIVITY TYPE'] == 'Roth']['AMOUNT'].sum(),
                              'Automatic_1': grp[grp['ACTIVITY TYPE'] == 'Automatic (1%)']['AMOUNT'].sum(),
                              'Matching': grp[grp['ACTIVITY TYPE'] == 'Match']['AMOUNT'].sum(),
                              'Total': grp['AMOUNT'].sum(),
                              'C FUND': grp[grp['FUND'] == 'C Fund']['FUND UNITS'].sum(),
                              'S FUND': grp[grp['FUND'] == 'S Fund']['FUND UNITS'].sum(),
                              }, ignore_index=True)
        pass
    ia_df = ia_df.fillna(0)

    contrib_file2 = contrib_file.append(ia_df, ignore_index=True)
    pass


def scrape_tsp_performance():
    current_prices = pd.read_csv('resources\\Share_Prices.csv')

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
    # import_contributions()
    scrape_tsp_performance()
