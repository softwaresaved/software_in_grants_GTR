#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
from pandas import ExcelWriter
import numpy as np
import csv
import matplotlib.pyplot as plt
import math
from textwrap import wrap
import urllib.request
from xml.etree import cElementTree as et
import string
import time
import datetime
from dateutil.rrule import rrule, MONTHLY
import logging

DATAFILENAME = "./data/gtr_data_titles_and_abs.csv"
STOREFILENAME = "./output/"
LOGGERLOCATION = "./log_gtr_analysis.log"

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.FileHandler(LOGGERLOCATION)
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)


def import_csv_to_df(filename):
    """
    Imports a csv file into a Pandas dataframe
    :params: an xls file and a sheetname from that file
    :return: a df
    """
    
    return pd.read_csv(filename)


def export_to_csv(df, location, filename):
    """
    Exports a df to a csv file
    :params: a df and a location in which to save it
    :return: nothing, saves a csv
    """

    return df.to_csv(location + filename + '.csv')


def convert_to_date(df):
        
    df['startdate'] = pd.to_datetime(df['startdate'])
    df['enddate'] = pd.to_datetime(df['enddate'])

    logger.info('Converted dates into datetime format.')
    
    return df
    
    
def clean_data(df):

    before = len(df)
    # Keep data modern by removing all project that started before 2000
    df = df[(df['startdate'].dt.year > 2000)]
    after1 = len(df)

    logger.info(str(before - after1) + ' records were dropped because the project started before the year 2000.')

    # Remove records where the end date
    df = df[(df['enddate'] > df['startdate'])]
    after2 = len(df)

    logger.info(str(after1 - after2) + ' records were dropped because the start date was recorded as later than the end date.')

    return df
    

def find_keywords(df, keyword_list, search_col):
    """
    Finds a keyword in a dataframe
    :params: a dataframe and a column in which to search
    :refturn: a dataframe containing only the rows in which the term was found
    """

    # Set up a translator for removing punctuation
    translator = str.maketrans('', '', string.punctuation)

    for current_keyword in keyword_list:
        # This looks for a keyword in a string and, if it is found, adds that keyword to an appropriate col to show
        # that is was found
        df.loc[df[search_col].str.lower()                       # Get the string and lower case it
        .str.translate(translator)                              # Remove all punctuation from the string
        .str.contains(current_keyword),                         # Search for the keyword in the string
        search_col + '_' + current_keyword] = current_keyword   # If found, show this fact by adding the keyword to the appropriate col 
    
    return df


def get_years(df):

    """
    Want the unique years in the dataframe. Output this as a dict of lists
    for the unique years in the start dates, the unique years in the end dates and the
    unique years in both
    """

    # Get lists of the years in the data
    # The 'set' gets the unique values, and this is then converted back to a list
    
    start_years = list(set(df['startdate'].dt.year.tolist()))
    end_years = list(set(df['enddate'].dt.year.tolist()))
    all_years = list(set(start_years + end_years))

    # Combine the lists into a dict
    years_in_data = {'start_years':start_years, 'end_years':end_years, 'all_years':all_years}

    logger.info('There are ' + str(len(years_in_data['all_years'])) + ' years in the data')
    
    return years_in_data


def get_annual_spend(df):

    # Get the length of the project in months
    df['duration in years'] = round((df['enddate'] - df['startdate'])/ np.timedelta64(1, 'Y'),0)

    df['annnual spend'] = df['awardpounds']/df['duration in years']

    print(df['duration in years'])


#    months = [dt.strftime("%Y") for dt in rrule(MONTHLY, dtstart=startdate, until=enddate)]
#    print(months)
    logger.info('Calculated durations.')

    return df



def get_summary_data(df, where_to_search, keyword_list, years_in_data):

    """
    Separate the df into years, and then count how many times each of the words
    are found in each part of the research grant
    """

    total_records = len(df)
    searched_columns = []
    df_summary = pd.DataFrame(index=keyword_list)
    df_summary_percent = pd.DataFrame(index=keyword_list)
    
    start_years = years_in_data['start_years']

    for curr_year in start_years:
        df_temp = df[df['startdate'].dt.year == curr_year]
    
        for search_col in where_to_search:
            appended_keyword_list = [search_col + '_' + s for s in keyword_list]
            df_counts = df_temp[appended_keyword_list].apply(pd.Series.value_counts)
            orig_column_list = df_counts.columns
            searched_columns.append('keywords in ' + search_col) 
            df_summary[str(curr_year) + '_' + search_col + '_count'] = df_counts[orig_column_list].sum(axis=1)
            df_summary_percent[str(curr_year) + '_' + search_col + '_%'] = round((df_counts[orig_column_list].sum(axis=1)/total_records)*100,2)
#            export_to_csv(df_counts, STOREFILENAME + 'found_keywords/', str(curr_year) + '_found_keywords')
    logger.info('Calculated summaries of data.')

    return df


def main():

    # Set in which parts of the grant we're going to search, and what
    # we're going to search for
    where_to_search = ['title', 'abstract']

    keyword_list = ['software', 'software developer', 'software development', 'programming', 'program',
                    'computational', 'HPC', 'high performance computing', 'simulation', 'modeling',
                    'data visualisation', 'data visualization']

    # Get GTR summary data
    df = import_csv_to_df(DATAFILENAME)

    logger.info('Imported df includes ' + str(len(df)) + ' records')

    # Make the dates, er... well... dates
    df = convert_to_date(df)

    df = clean_data(df)

    df = get_annual_spend(df)

    # Add new columns showing where each of the keywords was
    # found in the grant
    for search_col in where_to_search:
        find_keywords(df, keyword_list, search_col) 

    # Get a dict of lists in which the years represented in the data are stored
    years_in_data = get_years(df)

    # Produce summaries of what was found, where and when
    df = get_summary_data(df, where_to_search, keyword_list, years_in_data)


if __name__ == '__main__':
    main()