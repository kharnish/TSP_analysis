"""
TSP_analysis.py

Author: Kelly Harnish
Date:   18 October 2020

This file processes past TSP data to determine the best steps for future decisions.
Obtain current price data from https://www.tsp.gov/fund-performance/share-price-history/
"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns


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
    overall_max_price = []
    for account in history:
        range_max_price.append(max(history[account][:range_days]))
        overall_max_price.append(max(history[account][:]))

    new_fund_distribution = redistribution * current_balance  # move dollar balance to new redistribution
    new_shares_after_distribution = new_fund_distribution/history.iloc[0]

    new_share_range_max_price = new_shares_after_distribution * range_max_price
    potential_range_gain_loss = new_share_range_max_price - new_fund_distribution
    potential_total = sum(new_share_range_max_price)
    total_gain_loss = potential_total - current_balance

    current_shares_at_range_max_price = today_shares_owned * range_max_price
    tot = sum(current_shares_at_range_max_price)
    est_gain_loss = tot - current_balance
    current_distrib_v_scenario = total_gain_loss - est_gain_loss

    return current_distrib_v_scenario


def monthly_gain_loss(current_data):
    monthly_data = current_data.resample('M').sum
    return monthly_data


def main():
    prices_history, contrib_shares = import_data(False)

    current_shares = []
    for account in contrib_shares:
        current_shares.append(sum(contrib_shares[account]))
    current_shares = np.array(current_shares)
    current_fund_value = current_shares * prices_history.iloc[0]
    current_balance = sum(current_fund_value)
    current_distribution = current_fund_value/current_balance

    # 7       8       9       10      11      12      13      14
    # L 2055, L 2060, L 2065, G FUND, F FUND, C FUND, S FUND, I FUND
    redistribution = np.zeros(([10, 15]))
    redistribution[0, 14] = 1
    redistribution[1, 13] = 1
    redistribution[2, 12] = 1
    redistribution[3, 9] = 1
    redistribution[4, 8] = 1
    redistribution[5, 7] = 1
    redistribution[6, 12:14] = 1/3
    redistribution[7, 12], redistribution[7, 14] = 0.5, 0.5
    redistribution[8, 12:13] = 0.5

    ranges = [15, 30, 280, len(prices_history)]
    df = pd.DataFrame(columns=['Redistribution', 'Range: '+str(ranges[0])+' days', 'Range: '+str(ranges[1])+' days', 'Range: '+str(ranges[2])+' days', 'Over All Time'])
    for i in range(len(redistribution)):
        redis = redistribution[i, :]
        temp = [i]
        for days in [15, 30, 280, len(prices_history)]:
            temp.append(calculate_futures(current_balance, current_shares, prices_history, days, redis))
        df = df.append(pd.Series(temp, index=df.columns), ignore_index=True)

    piv = monthly_gain_loss(prices_history)


if __name__ == '__main__':
    main()
