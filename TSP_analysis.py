"""
TSP_analysis.py

Author: Kelly Harnish
Date:   18 October 2020

This file processes past TSP data to determine the best steps for future decisions.
"""
import pandas as pd
from scrape_data import scrape_data


def main():
    current_data = pd.read_csv('Share_Prices.csv')
    # print(current_data.tail())
    # current_data['DATE'] = pd.to_datetime(current_data['DATE'], format='%Y-%m-%d', infer_datetime_format=True)

    new_data = scrape_data()
    '''new_data = new_data.rename(columns={new_data.columns[0]: 'DATE', new_data.columns[1]: 'L-INC',
                                            new_data.columns[2]: 'L 2020', new_data.columns[3]: 'L 2030',
                                            new_data.columns[4]: 'L 2040', new_data.columns[5]: 'L 2050',
                                            new_data.columns[6]: 'G FUND', new_data.columns[7]: 'F FUND',
                                            new_data.columns[8]: 'C FUND', new_data.columns[9]: 'S FUND',
                                            new_data.columns[10]: 'I FUND'})'''
    print(new_data.head())

    # new_data['DATE'] = pd.to_datetime(new_data['DATE'], format='%Y-%m-%d', infer_datetime_format=True)

    # updated_data = pd.concat([new_data, current_data], ignore_index=True)

    # updated_data.to_csv('market_data.csv', index=False)


if __name__ == '__main__':
    main()