"""
TSP_analysis.py

Author: Kelly Harnish
Date:   18 October 2020

This file processes past TSP data to determine the best steps for your future financial decisions.
Obtain most current share price CSV from https://www.tsp.gov/fund-performance/share-price-history/
See personal TSP information at https://www.tsp.gov/
"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
# import seaborn as sns
import plotly.graph_objects as go


def import_data():
    """Import share price and contribution history and format into dataframes.
    :return: {Dataframe} share price history, {Dataframe} contribution history in dollars,
             {Dataframe} contribution history in shares, {ndarray} total shares owned,
             {Series} current dollar value per fund, {float} current total balance
    """
    current_data = pd.read_csv('share_prices.csv')
    current_data = current_data.set_index(['Date'])
    current_data.index = pd.to_datetime(current_data.index, format='%m/%d/%Y', infer_datetime_format=True)

    contrib = pd.read_csv('contributions.csv')
    contrib = contrib.set_index(['Date'])
    contrib.index = pd.to_datetime(contrib.index, format='%m/%d/%Y', infer_datetime_format=True)
    contributions = contrib[['Traditional', 'Roth', 'Automatic_1', 'Matching', 'Total']]
    shares = contrib.drop(columns=['Traditional', 'Roth', 'Automatic_1', 'Matching', 'Total'])
    concat = pd.concat([current_data, shares])

    current_shares = []
    for account in shares:
        current_shares.append(sum(shares[account]))
    current_shares = np.array(current_shares)
    current_fund_value = current_shares * current_data.iloc[0]
    current_balance = sum(current_fund_value)
    current_distribution = current_fund_value / current_balance

    return current_data, contributions, shares, current_shares, current_fund_value, current_balance


def plot_history(data):
    """Plot the share price history data from 2014 to current and just over the past year
    :param data: share price history
    :return: write and save plots
    """
    fig = go.Figure()
    for col in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data[col], mode='lines', name=col))
    fig.update_xaxes(title_text="Time",
                     showline=True, mirror=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinewidth=1, zerolinecolor='lightgrey',
                     showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(title_text="Share Price (USD)",
                     showline=True,  mirror=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinewidth=1, zerolinecolor='lightgrey',
                     showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        font=dict(family='Times New Roman', size=15), plot_bgcolor='rgba(0,0,0,0)')
    try:
        fig.write_image('share_prices_all_time.png', height=700, width=900, engine='kaleido')
    except TypeError:
        print('Could not write to static file')
    fig.write_html('share_prices_all_time.html')
    fig.show()

    recent = data[:data.first_valid_index() - pd.Timedelta(weeks=52)]
    fig = go.Figure()
    for col in data.columns:
        fig.add_trace(go.Scatter(x=recent.index, y=recent[col], mode='lines', name=col))
    fig.update_xaxes(title_text="Time",
                     showline=True, mirror=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinewidth=1, zerolinecolor='lightgrey',
                     showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(title_text="Share Price (USD)",
                     showline=True, mirror=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinewidth=1, zerolinecolor='lightgrey',
                     showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        font=dict(family='Times New Roman', size=15), plot_bgcolor='rgba(0,0,0,0)')
    try:
        fig.write_image('share_prices_past_year.png', height=700, width=900, engine='kaleido')
    except TypeError:
        print('Could not write to static file')
    fig.write_html('share_prices_past_year.html')
    fig.show()


def calculate_futures(current_balance, today_shares_owned, history, range_days, redistribution):
    """ Calculate future distributions of TSP funds.
    :param current_balance: current balance of TSP account
    :param today_shares_owned: current amount of shares owned
    :param history:
    :param range_days:
    :param redistribution:
    :return:
    """
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


def find_what_if_redis(ranges, redistribution, current_balance, current_shares, prices_history):
    df = pd.DataFrame(columns=['Redistribution', str(ranges[0])+' days', str(ranges[1])+' days', str(ranges[2])+' days', 'Over All Time'])
    for i in range(len(redistribution)):
        redis = redistribution[i, :]
        temp = [i]
        for days in [15, 30, 280, len(prices_history)]:
            temp.append(calculate_futures(current_balance, current_shares, prices_history, days, redis))
        df = df.append(pd.Series(temp, index=df.columns), ignore_index=True)
    return df.set_index('Redistribution')


def plot_what_if(df):
    """ Plot the share price history data from 2014 to current.
    :param df: dataframe of share price history
    :return:
    """
    plt.figure(figsize=(15, 9))
    plt.rc('axes', axisbelow=True)
    plt.grid(axis='y')
    width = 0.2
    plt.bar(df.index - width*1.5, df['15 days'], width)
    plt.bar(df.index - width/2, df['30 days'], width)
    plt.bar(df.index + width/2, df['280 days'], width)
    plt.bar(df.index + width*1.5, df['Over All Time'], width)
    plt.xticks(np.arange(min(df.index), max(df.index) + 1, 1))
    plt.xlabel('Redistribution')
    plt.ylabel('Gain/Loss ($)')
    plt.legend(['15 days', '30 days', '280 days', 'Over All Time'])
    plt.savefig("redistribution.png", bbox_inches='tight', pad_inches=0)
    plt.show()


def gain_loss_whole_month(current_data):
    """ Calculate monthly gains/losses of each fund over all years. """
    months = current_data.groupby(pd.Grouper(freq='MS'))
    losses_monthly = pd.DataFrame(0, columns=current_data.columns, index=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    for mo in months:
        # Per month per year, subtract final value from starting value
        diff = (mo[1].iloc[-1] - mo[1].iloc[0]).rename(mo[0])
        mon_str = str(diff.name.month_name()[:3])
        for index, val in diff.items():
            if val < 0:
                losses_monthly.loc[mon_str, index] = losses_monthly.loc[mon_str, index] + 1

    return losses_monthly


def gain_loss_month_daily(current_data):
    """ Calculate monthly sum of daily gains/losses of each fund over all years. """
    months = current_data.groupby(pd.Grouper(freq='MS'))
    losses_monthly = pd.DataFrame(0, columns=current_data.columns, index=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    for mo in months:
        # Per month per year, sum daily gains/losses
        monthly_sum = np.zeros((mo[1].shape[1],))
        for i in range(mo[1].shape[0] - 1):
            # loop over all days in month, except last day
            monthly_sum = monthly_sum + (mo[1].iloc[i+1] - mo[1].iloc[i])
        mon_str = str(mo[0].month_name()[:3])
        for index, val in monthly_sum.items():
            if val < 0:
                losses_monthly.loc[mon_str, index] = losses_monthly.loc[mon_str, index] + 1

    return losses_monthly


def main():
    prices_history, contribs, contrib_shares, current_shares, current_fund_value, current_balance = import_data()
    plot_history(prices_history)
    plot_history(prices_history)
    print("Total fund value:  $%.2f" % current_balance)
    my_input = np.sum(contribs['Traditional']) + np.sum(contribs['Roth'])
    all_input = np.sum(contribs['Total'])
    print('My Gain: \t\t$%.2f' % (current_balance - my_input))
    print('Total Gain: \t$%.2f' % (current_balance - all_input))

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
    df = find_what_if_redis(ranges, redistribution, current_balance, current_shares, prices_history)
    plot_what_if(df)
    print('\n\"What-if\" Resistribution Gains and Losses')
    print(df)

    gain_loss = gain_loss_whole_month(prices_history)
    print('\nWhole Month Monthly Losses')
    print(gain_loss[['C FUND', 'S FUND', 'I FUND', 'F FUND']])
    gain_loss2 = gain_loss_month_daily(prices_history)
    print('\nDaily Sum Monthly Losses')
    print(gain_loss2[['C FUND', 'S FUND', 'I FUND', 'F FUND']])


if __name__ == '__main__':
    main()