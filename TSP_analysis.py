"""
TSP_analysis.py

Author: Kelly Harnish
Date:   18 October 2020

This file processes past TSP data to determine the best steps for future financial decisions.
Obtain most current share price CSV from https://www.tsp.gov/fund-performance/share-price-history/
"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns


def import_data():
    """ Import share price and contribution history and format into dataframes. """
    current_data = pd.read_csv('share_prices.csv')
    current_data = current_data.set_index(['Date'])
    current_data.index = pd.to_datetime(current_data.index, format='%m/%d/%Y', infer_datetime_format=True)

    contrib = pd.read_csv('contributions.csv')
    contrib = contrib.set_index(['Date'])
    contrib.index = pd.to_datetime(contrib.index, format='%m/%d/%Y', infer_datetime_format=True)
    shares = contrib.drop(columns=['Traditional', 'Roth', 'Automatic_1', 'Matching', 'Total'])

    concat = pd.concat([current_data, shares])

    current_shares = []
    for account in shares:
        current_shares.append(sum(shares[account]))
    current_shares = np.array(current_shares)
    current_fund_value = current_shares * current_data.iloc[0]
    current_balance = sum(current_fund_value)
    current_distribution = current_fund_value / current_balance

    return current_data, shares, current_shares, current_fund_value, current_balance


def plot_history(data):
    """ Plot the share price history data from 2014 to current. """
    plt.figure(figsize=(15, 9))
    plt.grid()
    sns.color_palette("bright")
    sns.lineplot(data=data)
    plt.savefig("share_prices.png")
    plt.show()


def calculate_futures(current_balance, today_shares_owned, history, range_days, redistribution):
    """ Calculate future distributions of TSP funds. """
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
    """ Calculate monthly gains/losses of each fund over all years. """
    months = current_data.groupby(pd.Grouper(freq='MS'))
    losses_monthly = pd.DataFrame(0, columns=current_data.columns, index=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    for mo in months:
        diff = (mo[1].iloc[-1] - mo[1].iloc[0]).rename(mo[0])
        mon_str = str(diff.name.month_name()[:3])
        for index, val in diff.items():
            if val < 0:
                losses_monthly.loc[mon_str, index] = losses_monthly.loc[mon_str, index] + 1

    return losses_monthly


def main():
    prices_history, contrib_shares, current_shares, current_fund_value, current_balance = import_data()
    # plot_history(prices_history)
    print("Current total fund value:  $%.2f" % current_balance)

    # Test different distributions to see the possible gains/losses in switching to them, using the number code:
    # 7  = L 2055
    # 8  = L 2060
    # 9  = L 2065
    # 10 = G FUND
    # 11 = F FUND
    # 12 = C FUND
    # 13 = S FUND
    # 14 = I FUND
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
    # TODO: find a clean way to output the different distribution results

    gain_loss = monthly_gain_loss(prices_history)
    print(gain_loss[['C FUND', 'S FUND', 'I FUND', 'F FUND']])


if __name__ == '__main__':
    main()
