#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
from pandas import ExcelWriter
import numpy as np
import csv
import matplotlib.pyplot as plt
import math
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
        
    """
    The two date columns need to be viewed as dates by Pandas
    """
    
    df['startdate'] = pd.to_datetime(df['startdate'])
    df['enddate'] = pd.to_datetime(df['enddate'])

    logger.info('Converted dates into datetime format.')
    
    return df
    
    
def clean_data(df):

    """
    Couple of things we can do to make things cleaner. Drop all pre-2000 data (which 
    is of dubious quality) and remove records where the end date is earlier than the
    start date. If they can't get the date right... what else is wrong with the data?
    """

    before = len(df)
    # Keep data modern by removing all project that started before 2000
    df = df[(df['startdate'].dt.year >= 2000)]
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
        # that it was found
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


def get_annual_spend(df, years_in_data):

    """
    Need to work out how many years the grant spans and the amount of funding that is made each year

    NOTE: this assumes that the spend happens uniformly over the years, e.g. a project running from
          December 2015 to February 2017 spans three years (2015, 2016 & 2017) so the program will assume
          that 33 percent of the total award will be spent in each of those years. This assumption really
          simplifies the code without losing too much detail.
    """
    # The number of years in the grant is the end year minus the start year + 1
    df['no. years in grant'] = (df['enddate'].dt.year - df['startdate'].dt.year) + 1
    # Divide the total award over the years in the grant to get the annual spend
    df['spend per year'] = df['awardpounds']/df['no. years in grant']

    # Go through each year in the data and add it's annual spend to an appropriately named col
    for curr_year in years_in_data['all_years']:
        # Basically, if the curr_year is between the start and end date, then add the annual spend to the appropriate col
        df.loc[(df['startdate'].dt.year <= curr_year) & (df['enddate'].dt.year >= curr_year), 'spend in ' + str(curr_year)] = df['spend per year']
    
    logger.info('Calculated annual spend')

    return df


def get_summary_data(df, where_to_search, keyword_list, years_in_data):

    """
    Separate the df into years, and then count how many times each of the words
    are found in each part of the research grant
    """

    # Initialiase
    df_summary = pd.DataFrame(index=keyword_list)
    df_summary_percent = pd.DataFrame(index=keyword_list)

    # Get the number of records in the cleaned dataframe
    total_records = len(df)

    # Go through each of the start years in the data
    for curr_year in years_in_data['start_years']:
        # Create temp df containing only the current year's data
        df_temp = df[df['startdate'].dt.year == curr_year]
        # Go through each search col...
        for search_col in where_to_search:
            # ...create list of cols to search...
            cols_to_search = [search_col + '_' + s for s in keyword_list]
            # ...create df to hold counts of each unique value found
            df_counts = df_temp[cols_to_search].apply(pd.Series.value_counts)
            # ...store the name of the cols (i.e. where keywords were found)...
            orig_column_list = df_counts.columns
            # ...count the number of rows with keywords in, which is the same as the number of
            # grants that contained the keyword
            df_summary[str(curr_year) + '_' + search_col + '_count'] = df_counts[orig_column_list].sum(axis=1)
            # ...use that count to generate a percentage relative to all
            # the records in the dataframe
            df_summary_percent[str(curr_year) + '_' + search_col + '_%'] = round((df_counts[orig_column_list].sum(axis=1)/total_records)*100,2)

            print(df_summary_percent)

    export_to_csv(df_summary, STOREFILENAME, 'summary_found_keywords_count')
    export_to_csv(df_summary_percent, STOREFILENAME, 'summary_found_keywords_percentage')

    logger.info('Calculated summaries of data.')

    return


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

    # Get a dict of lists in which the years represented in the data are stored
    years_in_data = get_years(df)

    df = get_annual_spend(df, years_in_data)

    # Add new columns showing where each of the keywords was
    # found in the grant
    for search_col in where_to_search:
        find_keywords(df, keyword_list, search_col) 

    # Produce summaries of what was found, where and when
    get_summary_data(df, where_to_search, keyword_list, years_in_data)


if __name__ == '__main__':
    main()