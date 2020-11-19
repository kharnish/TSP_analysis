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

    return current_data, shares


def calculate_futures(current_balance, today_shares_owned, history, range_days, redistribution):
    today_fund_value = today_shares_owned * history.iloc[0]
    current_distribution = today_fund_value / current_balance

    range_max_price = []
    for account in history:
        range_max_price.append(max(history[account][:range_days]))

    new_fund_distribution = redistribution * current_balance  # move dollar balance to new redistribution
    new_shares_after_distribution = new_fund_distribution/history.iloc[0]

    new_share_range_max_price = new_shares_after_distribution * range_max_price
    potential_range_gain_loss = new_share_range_max_price - new_fund_distribution
    potential_total = sum(new_share_range_max_price)
    total_gain_loss = sum(potential_range_gain_loss)

    range_high_current_distribution = total_gain_loss - current_balance

    return potential_total, total_gain_loss


def monthly_gain_loss(current_data):
    monthly_data = current_data.resample('M').sum
    return monthly_data


def main():
    prices_history, contrib_shares = import_data(False)

    current_shares = []
    for account in contrib_shares:
        current_shares.append(sum(contrib_shares[account]))
    current_fund_value = current_shares * prices_history.iloc[0]
    current_balance = sum(current_fund_value)
    current_distribution = current_fund_value/current_balance

    # L 2055, L 2060, L 2065, G FUND, F FUND, C FUND, S FUND, I FUND
    redis_1 = np.zeros([15])
    redis_1[14] = 1
    redis_2 = np.zeros([15])
    redis_2[13] = 1
    redistribution_3 = [0, 0, 0, 0, 0, 1, 0, 0]
    redistribution_4 = [0, 0, 1, 0, 0, 1, 0, 0]

    for redis in [redis_1, redis_2]:
        for days in [15, 30, 280, len(prices_history)]:
            potential_total, total_gain_loss = calculate_futures(current_balance, current_shares, prices_history, days, redis)
            print(potential_total, total_gain_loss)

    piv = monthly_gain_loss(prices_history)
    print(piv.tail())


if __name__ == '__main__':
    main()
