#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import pandas as pd
import numpy as np
import string
import re

# Add search terms from policy_common_data submodule repo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib", "policy_common_data"))
from commondata.softwaresearchterms import SoftwareSearchTerms

# Other global variables
DATAFILENAME = "./output/results-all/csv/final_df.csv"


def import_csv_to_df(filename):
    """
    Imports a csv file into a Pandas dataframe
    :params: a csv file
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

def term_of_interest(terms):

    for current in terms:
        print(str(terms.index(current)) + ': ' + current)

    term_index = int(input('What term shall we look for? '))
    choice = terms[term_index]
    print()
    print('Okay, looking for: ' + choice)

    return choice


def find_terms_and_context(df, term_of_focus_raw, search_places):

    # To ensure correct matches, convert term to lower case
    term_of_focus = term_of_focus_raw.lower()

    # Find cols that have the term_of_focus in them
    matching = [s for s in df.columns if term_of_focus in s]

    if len(matching) == 0:
        print('No matches for that term in the data')
        return
    else:
        cols_to_keep = matching + search_places


    # Limit df to just the rows where a term_of_focus has been found
    focus_df = df.dropna(subset=[cols_to_keep], how='all', axis=0)

    print('Results shown in format: row_index, search_term-search_field:count_of_matches')

    # Go through each row of the df
    for index, row in focus_df.iterrows():
        # Construct a col header in which we will find a word if that word exists in that col
        for current in search_places:
            col_to_check = current + '_' + term_of_focus
            # If the entry in the col_to_check row is not nan, then investigate further
            if isinstance(row[col_to_check], str):
                # Set variable to change how much text should be printed
                # around term of focus
                offset = 70
                # Get the actual text
                whole_string = row[current]
                # The next two lines remove punctuation from the string and convert to lower case
                regex = re.compile('[%s]' % re.escape(string.punctuation))
                cleaned_string = regex.sub(' ', whole_string).lower()
                # Now find how many times the term - as a whole word - appears in the sentence
                # the split allows us to find only the word bracketed by spaces
                how_many = len(re.findall(r'\b' + term_of_focus + r'\b', cleaned_string))

                # Now find the first match as a whole word so we can show it in context
                match_str = re.search(r'\b' + term_of_focus + r'\b', cleaned_string)
                start_index = match_str.start()
                end_index = start_index + len(term_of_focus)
                print(index, term_of_focus + '-' + current + ':' + str(how_many) + ' ...' + whole_string[(start_index-offset):(end_index+offset)] + '...')

    return


def main():
    """
    Main function to run program

    To change the word searched for in the case studies,
    change the global variable found at the very start of
    the program called WORD_TO_SEARCH_FOR
    """

    # A list of the different parts of the case study (i.e. columns) in which
    # we want to search. I've removed 'References to the research' from the list
    # because it's too uncoupled from the actual case study content
    possible_search_places = ['title', 'abstract']

    # Get our search terms from policy_common_data
    search_terms = SoftwareSearchTerms().data

    # Import case study data
    df = import_csv_to_df(DATAFILENAME)

    term_of_focus = term_of_interest(search_terms)

    find_terms_and_context(df, term_of_focus, possible_search_places)


if __name__ == '__main__':
    main()
