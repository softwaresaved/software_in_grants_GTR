#!/usr/bin/env python
# encoding: utf-8

import os
import math
import string
import time
import tarfile
import logging

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from config import (COM_OUTPUTDIR, COM_OUTPUTFILE, ANA_ANALYSES, ANA_SEARCHFIELDS,
                    ANA_BACKGROUNDOUTPUTDIR, ANA_OUTPUTDIR, ANA_OUTPUTPNGSUBDIR, ANA_OUTPUTCSVSUBDIR,
                    ANA_SUBSETYEARS, ANA_LOGFILE)

from search_terms import SEARCH_TERM_LIST


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.FileHandler(ANA_LOGFILE)
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)


def import_csv_to_df(filepath):
    """Imports a csv file into a Pandas dataframe.

       :params: an xls file and a sheetname from that file
       :return: a df
    """

    return pd.read_csv(filepath)


def export_to_csv(df, filepath, index_write, compress=False):
    """Exports a df to a csv file, with an optional compressed copy.

       :params: a df and a path in which to save it
       :return: nothing, saves a csv and optionally a .tar.gz copy
    """

    filepath = os.path.join(ANA_OUTPUTCSVSUBDIR, filepath)
    df.to_csv(filepath + '.csv', index=True)

    if compress:
        with tarfile.open(filepath + '.tar.gz', 'w:gz') as targz:
            targz.add(filepath + '.csv')


def convert_to_date(df):
    """The two date columns need to be viewed as dates by Pandas."""

    df['startdate'] = pd.to_datetime(df['startdate'])
    df['enddate'] = pd.to_datetime(df['enddate'])

    logger.info('Converted dates into datetime format.')

    return df


def clean_input_data(df):
    """Clean grants input dataframe.

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


def save_bar_chart(df, x_col, y_col, file, percentage):
    """Generate a bar chart from the dataframe via Matplotlib."""
    # Must clear the plot first, or labels from previous plots are included
    plt.clf()

    ax = df.plot(kind='bar', legend=False)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)

    # If wanting to display percentage on y axis, set limits accordingly
    if percentage:
        plt.ylim([0, 100])

    fig = ax.get_figure()
    fig.tight_layout()

    filepath = os.path.join(ANA_OUTPUTPNGSUBDIR, file)
    fig.savefig(filepath + '.png')


def get_years(df):
    """Extract the unique years within the dataset.

       Output this as a dict of lists for the unique years in the start dates,
       the unique years in the end dates and the unique years in both
    """
    # Get lists of the years in the data
    # The 'set' gets the unique values, and this is then converted back to a list
    # Each of these is sorted so that they years run in order
    start_years = list(set(df['startdate'].dt.year.tolist()))
    start_years.sort()
    end_years = list(set(df['enddate'].dt.year.tolist()))
    end_years.sort()

    # Get a spread of the years across the data
    all_years = list(range(start_years[0], end_years[-1]+1))

    # Combine the lists into a dict
    years_in_data = {'start_years':start_years, 'end_years':end_years, 'all_years':all_years}

    logger.info('There are ' + str(len(years_in_data['all_years'])) + ' years in the data')

    # Write to a file for future reference
    for key in years_in_data:
        writing = open(ANA_BACKGROUNDOUTPUTDIR + '/' + key + '_in_data.csv','w')
        for item in years_in_data[key]:
            writing.write(str(item) + '\n')
        writing.close()

    return years_in_data


def get_funders(df):
    """Return a list of the unique funders found in the data."""

    funders_in_data = df['fundingorgname'].unique()
    funders_in_data.sort()

    # Write out the funders for future reference
    outputfile = os.path.join(ANA_BACKGROUNDOUTPUTDIR, 'funders_in_data.csv')
    funders = open(outputfile, 'w')
    for item in funders_in_data:
        funders.write(item + '\n')
    funders.close()

    return funders_in_data


def get_total_grants(df, years_in_data):
    """Calculate grants started in each year in the data.

       Used to calculate percentages later on. Collecting count of grants
       over all years too, because it looks like it might be important...
    """
    # How many grants are there in total (i.e. over all years)
    total_records = len(df)
    num_of_grants_started = {'all years': total_records}

    # Want to save the number of grants started for later reference, so setting up a
    # df for this purpose
    number_of_grants_started_df = pd.DataFrame(index=years_in_data['start_years'])

    # Go through each start year and count how many grants were started
    # in that year
    for current_year in years_in_data['start_years']:
        df_temp = df[df['startdate'].dt.year==current_year]
        number_started = len(df_temp)
        num_of_grants_started[current_year] = number_started
        number_of_grants_started_df.loc[current_year, 'how many grants started in year'] = number_started

    # Write out to a file for future reference
    #background_filepath = os.path.join(ANA_BACKGROUNDOUTPUTDIR, 'all_grants_count')
    export_to_csv(number_of_grants_started_df, 'all_grants_count', index_write=True)

    return num_of_grants_started


def find_keywords(df, keyword_list, where_to_search):
    """Finds a keyword in a dataframe.

       :params: a dataframe and a column in which to search
       :return: a dataframe containing only the rows in which the term was found
    """
    # Initialise
    all_columns = []

    # Go through each column in which to search. Typically, just
    # title and abstract (but you never know)
    for search_col in where_to_search:
        # Go through each of the keywords we're looking for and record that keyword in a new col
        # if it is found
        for current_keyword in keyword_list:
            # This looks for a keyword in a string and, if it is found, adds that keyword to an appropriate col to show
            # that it was found
            new_col_name = search_col + '_' + current_keyword
            all_columns.append(new_col_name)
            df.loc[df[search_col].str.lower()                       # Get the string and lower case it
            .str.replace('[^\w\s]','')                              # Remove all punctuation from the string (i.e. remove anything that's not alphanumeric or whitespace)
            .str.contains(r'\b' + current_keyword + r'\b', regex=True, na=False), # Search for the keyword in the string as a separate word
            new_col_name] = current_keyword                         # If found, show this fact by adding the keyword to the appropriate column
        # Add a new column that summarises how many times each of the words were found in each grant
        # This will be used later so that we don't double count grants
        df[search_col + '_all_terms'] = df[all_columns].apply(lambda x: x.count(), axis=1)

    return df


def get_annual_spend(df, years_in_data):
    """Calculates yearly duration for each grant and the amount of funding that is made each year.

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


def output_summary_data(df, where_to_search, keyword_list, years_in_data, num_of_grants_started, funders_in_data):
    """Save a summary of the keyword search results by year.

       Separate the df into years, and then count how many times each of the words
       are found in each part of the research grant
    """

    # Get the start years from the dict of lists
    start_years = years_in_data['start_years']

    # Initialise
    df_where_found = pd.DataFrame(index=keyword_list)
    df_where_found_percent = pd.DataFrame(index=keyword_list)
    df_summary = pd.DataFrame(index=start_years)

    # Go through each of the start years in the data
    for curr_year in start_years:
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
            df_where_found[str(curr_year) + '_' + search_col + '_count'] = df_counts[orig_column_list].sum(axis=1)
            # ...use that count to generate a percentage relative to all
            # the records in the dataframe from the year in question
            df_where_found_percent[str(curr_year) + '_' + search_col + '_%'] = round((df_counts[orig_column_list].sum(axis=1)/num_of_grants_started[curr_year])*100,2)

    export_to_csv(df_where_found, 'keywords_found_count', index_write=True)
    export_to_csv(df_where_found_percent, 'keywords_found_percentage', index_write=True)

    return


def save_only_software_grants(df, where_to_search):
    """Extract only those entries that are related to software.

       Return a df that contains only grants that are related to software, i.e. that
       have a keyword found in the title of abstract.
    """
    # Create a list that contains the names of the summary cols
    # typically "abstract_all_terms" and "title_all_terms"
    summary_cols = [s + '_all_terms' for s in where_to_search]

    # Drop all columns where the summary cols are 0. This is like saying
    # delete all cols where a word wasn't found in either the title of the
    # or the abstract. In other words, it leaves us with a df that contains
    # only records where a keyword was found.
    df_only_found = df.loc[(df[summary_cols]!=0).any(axis=1)]
    export_to_csv(df_only_found, 'only_grants_related_to_software', index_write=True, compress=True)

    logger.info('Saved data on all grants related to software')

    return df_only_found


def software_grants_by_funder(df, df_only_found, years_in_data, num_of_grants_started, funders_in_data):
    """Save a summary of software grants by funder."""

    start_years = years_in_data['start_years']

    # Initialise
    df_summary = pd.DataFrame(index=start_years)

    # Get a summary of how many software related grants were found each year
    # and for each funder and in each year. Doing this in two loops, because it
    # makes the process a lot clearer.
    for curr_year in start_years:
        df_temp = df_only_found[df_only_found['startdate'].dt.year == curr_year]
        df_summary.at[curr_year, 'all funders grants count'] = len(df_temp)
        df_summary.at[curr_year, 'all funders grants %'] = round((len(df_temp)/num_of_grants_started[curr_year])*100,2)

    for funder in funders_in_data:
        # All grants by this funder
        df_funder = df[df['fundingorgname'] == funder]

        # Get total number of grants started by this funder for each year (for percentage calculation)
        funder_num_grants_started = get_total_grants(df_funder, years_in_data)

        # Grants by this funder related to software
        df_funder_sw = df_only_found[df_only_found['fundingorgname'] == funder]

        # Get total grants count and percentage by year
        for curr_year in start_years:
            df_funder_swyear = df_funder_sw[df_funder_sw['startdate'].dt.year == curr_year]
            df_summary.loc[curr_year, str(funder) + ' grants count'] = len(df_funder_swyear)
            if funder_num_grants_started[curr_year] > 0:
                df_summary.loc[curr_year, str(funder) +  ' grants %'] = round((len(df_funder_swyear)/funder_num_grants_started[curr_year])*100,2)

    export_to_csv(df_summary, 'software_grants_by_funder', index_write=True)

    logger.info('Calculated summaries of data.')

    return


def get_software_grants_cost_by_funder(df_only_found, df, years_in_data, num_of_grants_started, funders_in_data):
    """Save a summary of software grant costs by funder, for each year we want."""

    # Get all years contained in data
    all_years = years_in_data['all_years']

    # Initialise
    df_cost = pd.DataFrame(index=all_years)

    for curr_year in all_years:
        # Sum all of the funding for software-related grants in each year
        df_cost.loc[curr_year, 'all funders software spend'] = df_only_found['spend in ' + str(curr_year)].sum()
        # Sum all of the funding for all kinds of grants in each year
        df_cost.loc[curr_year, 'all funders spend'] = df['spend in ' + str(curr_year)].sum()

    # What percentage of total funding is spent on software-reliant grants?
    df_cost['software spend as percentage of spend on all grants'] = round((df_cost['all funders software spend']/df_cost['all funders spend'])*100, 2)

    for funder in funders_in_data:
        df_all_temp = df[df['fundingorgname'] == funder]
        df_sw_temp = df_only_found[df_only_found['fundingorgname'] == funder]
        for curr_year in all_years:
            all_funder_spend = df_all_temp['spend in ' + str(curr_year)].sum()
            sw_funder_spend = df_sw_temp['spend in ' + str(curr_year)].sum()
            df_cost.loc[curr_year, str(funder) + ' total spend'] = all_funder_spend
            df_cost.loc[curr_year, str(funder) + ' software spend'] = sw_funder_spend
            df_cost.loc[curr_year, str(funder) +  ' software spend %'] = round((sw_funder_spend/all_funder_spend)*100, 2)

    # Create and save bar charts for all funding over years Institute has existed until 2017
    df_cost_sub = df_cost.loc[ANA_SUBSETYEARS, 'all funders software spend']
    save_bar_chart(df_cost_sub, 'Year', 'Spend (£)', 'software_spend_all', False)

    df_cost_pct_sub = df_cost.loc[ANA_SUBSETYEARS, 'software spend as percentage of spend on all grants']
    save_bar_chart(df_cost_pct_sub, 'Year', 'Spend (%)', 'software_spend_all_percent', True)

    # As previously, but just for each funder
    for funder in funders_in_data:
        df_cost_funder_sub = df_cost.loc[ANA_SUBSETYEARS, funder + ' software spend']
        save_bar_chart(df_cost_funder_sub, 'Year', funder + ' spend (£)', 'software_spend_' + funder, False)

        df_cost_pct_sub = df_cost.loc[ANA_SUBSETYEARS, funder + ' software spend %']
        save_bar_chart(df_cost_pct_sub, 'Year', funder + ' spend (%)', 'software_spend_percent_' + funder, True)

    export_to_csv(df_cost, 'yearly_all_grants_costs_by_funder', index_write=True)
    export_to_csv(df_cost_sub, 'yearly_software_grants_costs_by_funder', index_write=True)

    logger.info('Calculated yearly costs of software-related grants.')

    return df_cost


def average_annual_spend_on_software(df_cost, years_in_data, funders_in_data):
    """Output a summary of the average annual software spend (as % of funding), across all funders."""

    # Get average figures only for the years we're interested in
    df_cost_sub = df_cost.loc[ANA_SUBSETYEARS]

    # Date range for chart title
    drange = str(ANA_SUBSETYEARS[0]) + '-' + str(ANA_SUBSETYEARS[-1])

    # Initialise
    df_av_cost = pd.DataFrame(index=funders_in_data)

    for funder in funders_in_data:
        # Calculate average spend on software for funder
        df_av_cost.loc[funder, 'Average software spend (£) ' + drange] = df_cost_sub[funder + ' software spend'].sum() / len(ANA_SUBSETYEARS)

        # Determine overall average % of software spending over the period
        total_spend = df_cost_sub[funder + ' total spend'].sum()
        total_sw_spend = df_cost_sub[funder + ' software spend'].sum()
        df_av_cost.loc[funder, 'Average software spend (% of all funding) ' + drange] = round((total_sw_spend/total_spend)*100, 2)

    # Extract amount average column, sort, and plot
    df_av_spend_amount = df_av_cost['Average software spend (£) ' + drange]
    df_av_spend_amount = df_av_spend_amount.sort_values(ascending=True)
    save_bar_chart(df_av_spend_amount, 'Funder', 'Average software spend (£) ' + drange,
        'software_spend_all_average_amount', False)

    # Extract % average column, sort, and plot
    df_av_spend_pct = df_av_cost['Average software spend (% of all funding) ' + drange]
    df_av_spend_pct = df_av_spend_pct.sort_values(ascending=True)
    save_bar_chart(df_av_spend_pct, 'Funder','Average software spend (% of all funding) ' + drange,
        'software_spend_all_average_percent', True)

    # Sort overall costs and save
    df_av_cost = df_av_cost.sort_values(by='Average software spend (£) ' + drange, ascending=True)
    export_to_csv(df_av_cost, 'average_software_grants_costs_by_funder', index_write=True)

    logger.info('Calculated average costs of software-related grants.')


def search_term_popularity(df_only_found, keyword_list, funders_in_data):
    """Output search term popularity across each funder in the data."""

    # Our results dataframe for keyword counts per funder
    df_term_pop = pd.DataFrame()
    for funder in funders_in_data:

        # Only want subset of those by this funder
        df_funder = df_only_found[df_only_found['fundingorgname'] == funder]

        # Count occurences of each keyword in either abstract or title
        for keyword in keyword_list:
            # Extract the abstract and title columns for that keyword,
            # and drop rows with nothing in both columns (i.e. no match)
            df_funder_terms = df_funder[['abstract_' + keyword, 'title_' + keyword]]
            has_term_df = df_funder_terms.dropna(how='all')

            # Add the count of occurrences to our results dataframe for that funder
            df_term_pop.loc[keyword, funder + '_count'] = len(has_term_df)

        # Sort ascending by count and generate bar chart
        df_chart_funder = df_term_pop[funder + '_count'].sort_values(ascending=True)

        save_bar_chart(df_chart_funder, 'Keyword', 'Keyword count',
            'search_term_popularity_' + funder, False)

    df_term_pop['Total'] = df_term_pop.sum(axis=1)
    df_chart_term_pop = df_term_pop.sort_values(by='Total', ascending=True)
    save_bar_chart(df_chart_term_pop['Total'], 'Keyword', 'Keyword count',
        'search_term_popularity_all', False)

    export_to_csv(df_term_pop, 'search_term_popularity_all', index_write=True)

    logger.info('Calculated search term popularity across search results.')


def process_dataset(df, desc, where_to_search):
    # If the output directory for this dataset doesn't exist, create it
    dir_path = os.path.join(ANA_OUTPUTDIR, 'results-' + desc)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        os.makedirs(os.path.join(dir_path, ANA_BACKGROUNDOUTPUTDIR))
        os.makedirs(os.path.join(dir_path, ANA_OUTPUTCSVSUBDIR))
        os.makedirs(os.path.join(dir_path, ANA_OUTPUTPNGSUBDIR))

    # Change to the directory in which all CSV and PNG results
    # will be created
    os.chdir(dir_path)

    # Get a dict of lists in which the years represented in the data are stored
    years_in_data = get_years(df)

    # Find which funders are contained in the data
    funders_in_data = get_funders(df)

    # How many grants started in each year?
    num_of_grants_started = get_total_grants(df, years_in_data)

    df = get_annual_spend(df, years_in_data)

    # Add new columns showing where each of the keywords was
    # found in the grant
    find_keywords(df, SEARCH_TERM_LIST, where_to_search)

    # Produce summaries of what was found, where and when
    output_summary_data(df, where_to_search, SEARCH_TERM_LIST, years_in_data, num_of_grants_started, funders_in_data)

    # Produce a df of the details of only grants related to software and save this to csv
    df_only_found = save_only_software_grants(df, where_to_search)

    # Find relative popularity of the search terms
    search_term_popularity(df_only_found, SEARCH_TERM_LIST, funders_in_data)

    # Split the data by funder
    software_grants_by_funder(df, df_only_found, years_in_data, num_of_grants_started, funders_in_data)

    # Find costs of software-related grants by year, per funder
    df_cost = get_software_grants_cost_by_funder(df_only_found, df, years_in_data, num_of_grants_started, funders_in_data)

    # Find average costs of software-related grants by year, per funder
    average_annual_spend_on_software(df_cost, years_in_data, funders_in_data)

    # Output entire processing dataframe
    export_to_csv(df, 'final_df', index_write=False, compress=True)

    # Revert to root directory
    os.chdir('../..')


def main():
    # Get GTR summary data from our combination process output directory
    input_filepath = os.path.join(COM_OUTPUTDIR, COM_OUTPUTFILE)
    df = import_csv_to_df(input_filepath)
    logger.info('Imported df includes ' + str(len(df)) + ' records')

    # Make the dates, er... well... dates
    df = convert_to_date(df)

    # Clean GtR summary data
    df = clean_input_data(df)

    # Loop through each of the input files we wish to process, and run
    # the analysis on each. CSV and PNG results are stored in subdirectories
    # of ANA_OUTPUTDIR, one subdirectory for each analysis
    for desc, projectcategory_match in ANA_ANALYSES:
        logger.info('------ Processing analysis: ' + desc + ' ------')
        subset_df = df.loc[df['projectcategory'].str.contains(projectcategory_match, regex=True)]

        # Suppress irrelevant SettingWithCopyWarning, since we
        # _want_ to conduct operations on the copied dataframe
        # and not the original
        subset_df.is_copy = False

        process_dataset(subset_df, desc, ANA_SEARCHFIELDS)


if __name__ == '__main__':
    main()
