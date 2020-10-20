"""
TSP_analysis.py

Author: Trey Morris
Date:   18 October 2020

"""
import requests
import lxml.html as lh
import pandas as pd
from bs4 import BeautifulSoup


def scrape_data():
    # url = 'https://www.tsp.gov/InvestmentFunds/FundPerformance/index.html'

    url = 'https://www.tsp.gov/fund-performance/share-price-history/'
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find_all(id='dynamic-share-price-table')
    # print(results.prettify())

    table = soup.find(lambda tag: tag.name == 'table' and tag.has_attr('id') and tag['id'] == "dynamic-share-price-table")
    # rows = table.findAll(lambda tag: tag.name == 'tr')


    results = soup.find_all('tr')

    table = soup.find("table", {"title": "dynamic-share-price-table"})
    rows = list()
    for row in table.find_all("tr"):
        rows.append(row)


    '''Store the contents of the website under doc'''
    doc = lh.fromstring(page.content)

    '''Parse data that are stored between <tr>..</tr> of HTML'''
    tr_elements = doc.xpath('//*[@id="subPageContent"]/table')

    '''create iterator dummy variable to loop over'''
    i = 0

    '''initialize a pandas data frame'''
    final_df = pd.DataFrame()

    '''loop over all table elements on the webpage'''
    for elements in tr_elements:
        '''loop over each row in the table'''
        for element in elements:
            '''start to do some cleaning of the data inside each ceel for it has a standard format at the end'''
            clean_text = str(element.text_content()).replace('\n', '')
            clean_text = clean_text.replace(',', ' ')
            clean_text = clean_text.replace('           ', ';')
            clean_text = clean_text.replace(';', ',')
            clean_text = clean_text.replace('       ', '')
            clean_text = clean_text.split(',')

            '''put the string into a dataframe for later use'''
            clean_text_df = pd.DataFrame(clean_text)

            '''put the dataframe from 1-D coloumn into 1 row'''
            clean_text_df = clean_text_df.transpose()

            '''merge the new formatted row with the previously processed rows'''
            final_df = pd.concat([final_df, clean_text_df], ignore_index=True)

            '''increase the iterator so it goes to the next row'''
            i += 1
    '''drop any rows with NaN values which are usually a result of corner case errors'''
    final_df = final_df.dropna(axis=0)
    print(final_df.head())

    '''once this function is completed pass this pandas dataframe back to the function that invokes this function'''
    return final_df.head()
