"""
TSP_analysis.py

Author: Kelly Harnish
Date:   18 October 2020

This file processes past TSP data to determine the best steps for future decisions.
"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from scrape_data import scrape_data


def import_data(plot_it):
    current_data = pd.read_csv('Share_Prices.csv')
    current_data = current_data.set_index(['Date'])
    current_data.index = pd.to_datetime(current_data.index, format='%m/%d/%Y', infer_datetime_format=True)

    if plot_it:
        plt.figure()
        sns.color_palette("bright")
        sns.lineplot(data=current_data)
        plt.show()

    contrib = pd.read_csv('Contribution.csv')
    contrib = contrib.set_index(['Date'])
    contrib.index = pd.to_datetime(contrib.index, format='%m/%d/%Y', infer_datetime_format=True)
    shares = contrib.drop(columns=['Traditional', 'Roth', 'Automatic_1', 'Matching', 'Total'])

    concat = pd.concat([current_data, shares])

    return current_data, concat


def calculate_futures(current_balance, range_days, redistribution, current_data):
    today_price = current_data.tail(1).values
    today_shares_owned = current_data.tail(10).values  # TODO: this is just a placeholder. Fix is
    today_fund_value = today_shares_owned * today_price
    today_balance = sum(today_fund_value)
    current_distribution = today_fund_value / today_balance

    range_max_price = np.array([max(current_data['L 2055'][-range_days:]), max(current_data['L 2060'][-range_days:]),
                                max(current_data['L 2065'][-range_days:]), max(current_data['G FUND'][-range_days:]),
                                max(current_data['F FUND'][-range_days:]), max(current_data['C FUND'][-range_days:]),
                                max(current_data['S FUND'][-range_days:]), max(current_data['I FUND'][-range_days:])])

    new_fund_distribution = redistribution * current_balance
    new_shares_after_distribution = new_fund_distribution/today_shares_owned

    new_share_range_max_price = new_shares_after_distribution * range_max_price
    potential_range_gain_loss = new_share_range_max_price - new_fund_distribution
    potential_total = sum(new_share_range_max_price)
    total_gain_loss = sum(potential_range_gain_loss)

    range_high_current_distribution = total_gain_loss - current_balance

    return potential_total, total_gain_loss


def get_today_stats(current_data):
    today_price = current_data.tail(1).values
    today_shares_owned = np.array([0, 0, 0, 0, 0, 0, 0, 1])
    today_fund_value = today_shares_owned * today_price
    today_balance = sum(today_fund_value)
    current_distribution = today_fund_value/today_balance


def monthly_gain_loss(current_data):
    monthly_data = current_data.resample('M').sum
    return monthly_data


def main():
    current_prices, contribution = import_data(False)

    # new_data = scrape_data()
    '''new_data = new_data.rename(columns={new_data.columns[0]: 'DATE', new_data.columns[1]: 'L-INC',
                                            new_data.columns[2]: 'L 2020', new_data.columns[3]: 'L 2030',
                                            new_data.columns[4]: 'L 2040', new_data.columns[5]: 'L 2050',
                                            new_data.columns[6]: 'G FUND', new_data.columns[7]: 'F FUND',
                                            new_data.columns[8]: 'C FUND', new_data.columns[9]: 'S FUND',
                                            new_data.columns[10]: 'I FUND'})'''

    # new_data['DATE'] = pd.to_datetime(new_data['DATE'], format='%m/%d/%Y', infer_datetime_format=True)
    # updated_data = pd.concat([new_data, current_data], ignore_index=True)
    # updated_data.to_csv('Share_Prices.csv', index=False)

    # L 2055, L 2060, L 2065, G FUND, F FUND, C FUND, S FUND, I FUND
    redistribution_1 = np.zeros([15])
    redistribution_1[14] = 1
    redistribution_2 = [0, 0, 0, 0, 0, 0, 1, 0]
    redistribution_3 = [0, 0, 0, 0, 0, 1, 0, 0]
    redistribution_4 = [0, 0, 1, 0, 0, 1, 0, 0]

    '''current_balance = 1000
    for redis in [redistribution_1]:
        for days in [len(current_prices), 15, 30, 280]:
            calculate_futures(current_balance, days, redis, current_prices)'''

    print(current_prices.tail())
    piv = monthly_gain_loss(current_prices)
    print(piv.tail())


if __name__ == '__main__':
    main()
