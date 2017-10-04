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
import untangle


DATAFILENAME = "./data/projectsearch-1507107194469.csv"
STOREFILENAME = "./output/"


def import_csv_to_df(filename):
    """
    Imports a csv file into a Pandas dataframe
    :params: an xls file and a sheetname from that file
    :return: a df
    """
    
    return pd.read_csv(filename)


def pull_data():

    response = urllib.request.urlopen('http://gtr.rcuk.ac.uk/gtr/api/projects/602FA30A-63E7-409F-A3CB-11504A7B204D')
    page =  response.read()

    print(type(page))
    obj = untangle.parse(str(page))

    return

def find_keywords(df, search_col):
    """
    Finds a keyword in a dataframe
    :params: a dataframe and a column in which to search
    :refturn: a dataframe containing only the rows in which the term was found
    """

    where_to_search = ['Title']

#    for current_search in where_to_search

    current_keyword = 'software'
    df = df[df[search_col].str.lower().str.contains(current_keyword)]    

#   http://gtr.rcuk.ac.uk/gtr/api/projects/<id>

    
    return df

def main():
    
    df = import_csv_to_df(DATAFILENAME)
    
    pull_data()

    df = find_keywords(df, 'Title')
    
    print(df.columns)

if __name__ == '__main__':
    main()