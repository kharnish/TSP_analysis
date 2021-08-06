"""
TSP_analysis.py

Author: Kelly Harnish
Date:   18 October 2020

This file processes past TSP data to determine the best steps for your future financial decisions.
Obtain most current share price CSV from https://www.tsp.gov/fund-performance/share-price-history/
See personal TSP information at https://www.tsp.gov/
"""
from os.path import join
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def import_data():
    """Import share price and contribution history and format into dataframes.
    :return: {Dataframe} share price history, {Dataframe} contribution history in dollars,
             {Dataframe} contribution history in shares, {ndarray} total shares owned,
             {Series} current dollar value per fund, {float} current total balance
    """
    current_share_prices = pd.read_csv(join('resources', 'share_prices.csv'))
    current_share_prices = current_share_prices.set_index(['Date'])
    current_share_prices.index = pd.to_datetime(current_share_prices.index, format='%m/%d/%Y', infer_datetime_format=True)

    contrib = pd.read_csv(join('resources', 'contributions.csv'))
    contrib = contrib.set_index(['Date'])
    contrib.index = pd.to_datetime(contrib.index, format='%m/%d/%Y', infer_datetime_format=True)
    contribs_dollars = contrib[['Traditional', 'Roth', 'Automatic_1', 'Matching', 'Total']]
    contribs_shares = contrib.drop(columns=['Traditional', 'Roth', 'Automatic_1', 'Matching', 'Total'])
    concat = pd.concat([current_share_prices, contribs_shares])

    current_shares = []
    for account in contribs_shares:
        current_shares.append(sum(contribs_shares[account]))
    current_shares = np.array(current_shares)
    current_dollars = current_shares * current_share_prices.iloc[0]
    balance_dollars = sum(current_dollars)
    current_distribution = current_dollars / balance_dollars

    return current_share_prices, contribs_dollars, contribs_shares, current_shares, current_dollars, balance_dollars


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
    fig.update_yaxes(title_text="Share Price ($ USD)",
                     showline=True,  mirror=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinewidth=1, zerolinecolor='lightgrey',
                     showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                      font=dict(family='Times New Roman', size=15), plot_bgcolor='rgba(0,0,0,0)',
                      margin_l=20, margin_r=20, margin_t=20, margin_b=20,)

    fig.write_image(join('..', 'docs', 'share_prices_all_time.png'), height=700, width=900, engine='kaleido')
    fig.write_html(join('..', 'docs', 'share_prices_all_time.html'))
    fig.show()

    recent = data[:data.first_valid_index() - pd.Timedelta(weeks=52)]
    fig = go.Figure()
    for col in data.columns:
        fig.add_trace(go.Scatter(x=recent.index, y=recent[col], mode='lines', name=col))
    fig.update_xaxes(title_text="Time",
                     showline=True, mirror=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinewidth=1, zerolinecolor='lightgrey',
                     showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(title_text="Share Price ($ USD)",
                     showline=True, mirror=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinewidth=1, zerolinecolor='lightgrey',
                     showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                      font=dict(family='Times New Roman', size=15), plot_bgcolor='rgba(0,0,0,0)',
                      margin_l=20, margin_r=20, margin_t=20, margin_b=20,)

    fig.write_image(join('..', 'docs', 'share_prices_past_year.png'), height=700, width=900, engine='kaleido')
    fig.write_html(join('..', 'docs', 'share_prices_past_year.html'))
    fig.show()


def plot_my_history(share_history, contrib_shares, contrib_dollars):
    """Plot personal contributions and fund value over time.
    :param share_history: share price history
    :param contrib_shares: contribution in share amounts
    :param contrib_dollars: contribution in dollar amount
    :return: write and save plots
    """
    color = ['royalblue', 'crimson', 'mediumseagreen', 'mediumpurple', 'darkorange', 'turquoise', 'deeppink', 'gold',
             'lawngreen', 'sienna']

    for i in range(len(contrib_shares)):
        # Concatenate share values
        try:
            temp_df = contrib_shares_compound.iloc[i - 1] + contrib_shares.iloc[i]
            temp_df = temp_df.to_frame().transpose()
            temp_df['Date'] = [contrib_shares.index.values[i]]
            temp_df = temp_df.set_index('Date', drop=True)
            contrib_shares_compound = pd.concat([contrib_shares_compound, temp_df])
        except UnboundLocalError:
            contrib_shares_compound = contrib_shares.iloc[i].to_frame().transpose()

        # Convert shares to dollar values
        contrib_value = contrib_shares_compound.iloc[i] * share_history.iloc[i]
        contrib_value['Total Value'] = contrib_value.sum()
        try:
            contrib_value['Total Contribution'] = contrib_dollars.iloc[i]['Total'] + contrib_dollars_compound.iloc[i - 1]['Total Contribution']
        except UnboundLocalError:
            contrib_value['Total Contribution'] = contrib_dollars.iloc[i]['Total']
        contrib_value['Fund Gain'] = contrib_value['Total Value'] - contrib_value['Total Contribution']
        temp_df = contrib_value.to_frame().transpose()
        temp_df['Date'] = [contrib_shares.index.values[i]]
        temp_df = temp_df.set_index('Date', drop=True)
        try:
            contrib_dollars_compound = pd.concat([contrib_dollars_compound, temp_df])
        except UnboundLocalError:
            contrib_dollars_compound = temp_df

    # Plot fund value
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=contrib_dollars_compound.index, y=contrib_dollars_compound['Total Value'],
                             name='Total Value', mode='lines+markers', line=dict(color=color[0], width=2)),
                  secondary_y=False,)
    fig.add_trace(go.Scatter(x=contrib_dollars_compound.index, y=contrib_dollars_compound['Total Contribution'],
                             name='Total Contribution', mode='lines+markers', line=dict(color=color[1], width=2)),
                  secondary_y=False,)
    fig.add_trace(go.Scatter(x=contrib_dollars_compound.index, y=contrib_dollars_compound['Fund Gain'], # fill='tozeroy',
                             name='Fund Gain', mode='lines', line=dict(color=color[2], width=2)), secondary_y=True, )
    i = 3
    for col in contrib_dollars_compound.columns:
        if max(contrib_dollars_compound[col]) > 0 and col != 'Total Value' and col != 'Total Contribution' and col != 'Fund Gain':
            fig.add_trace(go.Scatter(x=contrib_dollars_compound.index, y=contrib_dollars_compound[col], mode='lines', name=col,
                                     line=dict(color=color[i], width=2)), secondary_y=False,)
            i += 1

    fig.update_xaxes(title_text="Time",
                     showline=True, mirror=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinewidth=1, zerolinecolor='lightgrey',
                     showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(title_text="Value ($ USD)", secondary_y=False, rangemode='tozero',
                     showline=True,  mirror=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinewidth=1, zerolinecolor='lightgrey',
                     showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(title_text="Fund Gains ($ USD)", secondary_y=True, rangemode='tozero',
                     showline=True, mirror=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinewidth=1, zerolinecolor='lightgrey',
                     showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                      font=dict(family='Times New Roman', size=15), plot_bgcolor='rgba(0,0,0,0)',
                      margin_l=20, margin_r=20, margin_t=20, margin_b=20,)

    fig.write_image(join('..', 'docs', 'my_fund_value.png'), height=700, width=900, engine='kaleido')
    fig.write_html(join('..', 'docs', 'my_fund_value.html'))
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
    fig = go.Figure()
    for col in df.columns:
        fig.add_trace(go.Bar(x=df[col].index, y=df[col].values, name=col))
    fig.update_xaxes(title_text="Gains/Losses ($ USD)",
                     showline=True, mirror=True, linewidth=1, linecolor='black',
                     zeroline=False, zerolinewidth=1, zerolinecolor='lightgrey',
                     showgrid=False, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(title_text="Gains/Losses ($ USD)",
                     showline=True, mirror=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinewidth=2, zerolinecolor='grey',
                     showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                      font=dict(family='Times New Roman', size=15), plot_bgcolor='rgba(0,0,0,0)',
                      margin_l=20, margin_r=20, margin_t=20, margin_b=20,
                      xaxis=dict(tickmode='linear', tick0=1, dtick=1,))


    fig.write_image(join('..', 'docs', 'redistribution.png'), height=700, width=900, engine='kaleido')
    fig.write_html(join('..', 'docs', 'redistribution.html'))
    fig.show()


def gain_loss_whole_month(current_data):
    """ Calculate monthly gains/losses of each fund over all years. """
    months = current_data.groupby(pd.Grouper(freq='MS'))
    losses_monthly = pd.DataFrame(0, columns=current_data.columns, index=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
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
    losses_monthly = pd.DataFrame(0, columns=current_data.columns, index=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
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
    prices_history, contrib_dollars, contrib_shares, current_shares, current_dollars, current_balance = import_data()
    plot_history(prices_history)
    plot_my_history(prices_history, contrib_shares, contrib_dollars)
    print("Total fund value: \t\t\t  $%.2f" % current_balance)
    my_input = np.sum(contrib_dollars['Traditional']) + np.sum(contrib_dollars['Roth'])
    all_input = np.sum(contrib_dollars['Total'])
    print('Gain on my raw contribution:   $%.2f' % (current_balance - my_input))
    print('Gain on total contribution:    $%.2f' % (current_balance - all_input))
    print('Current shares')
    for i in range(len(current_shares)):
        if current_shares[i] > 0.001:
            print(current_dollars.axes[0][i] + ': %.4f' % current_shares[i] + '    $%.4f' % current_dollars[i] +
                  '    %.2f%%' % (100*current_dollars[i]/current_balance))

    # Test different distributions to see the possible gains/losses in switching to them, using the number code:
    # 7  = L 2055
    # 8  = L 2060
    # 9  = L 2065
    # 10 = G FUND
    # 11 = F FUND
    # 12 = C FUND
    # 13 = S FUND
    # 14 = I FUND
    redistribution = np.zeros(([9, 15]))
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
