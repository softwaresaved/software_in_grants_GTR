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


DATAFILENAME = "./data/gtrdata-clean.csv"
STOREFILENAME = "./output/"


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


def drop_non_grants(df):

    df = df[df['ProjectCategory'] == 'Research Grant']

    return df


def populate_dataframe(df):

    """
    Convert XML files into a dataframe
    """

    FILE_PATH = 'file:///Users/user/Desktop/Git/software_in_grants_GTR/data/xml_data/'
    XML_NAMESPACE = 'http://gtr.rcuk.ac.uk/api'


    def retrieve_xml_from_url(filename):
        """
        This was copied from Steve Crouch's training set collector repo:
        https://github.com/softwaresaved/training-set-collector
    
        It's purpose is to retrieve and return a GtR XML document from a given URL source.
        """

        # Initialise
        xml_root = None

        try:
            # Get XML from file
            xml_str = urllib.request.urlopen(filename).read()

            # Some returned xml contains unicode, so need to ensure it's ascii
            xml_str = xml_str.decode('utf8').encode('ascii', 'replace')
            # Use Elementtree to extract XML
            xml_root = et.fromstring(xml_str)
        # The except part is mainly needed if you're getting the data from the API
        # rather than dragging it in from a file like we're doing in this program
        except (urllib.request.HTTPError, urllib.request.URLError) as err:
            print(filename + ": " + str(err))

        return xml_root


    for curr_project in df['ProjectId'].astype(str):
        print(curr_project)
        xml_doc = FILE_PATH + curr_project
        xml_root = retrieve_xml_from_url(xml_doc)
        df['title'] = xml_root.find('./gtr:projectComposition/gtr:project/gtr:title', {'gtr': XML_NAMESPACE}).text
        df['abstract'] = xml_root.find('./gtr:projectComposition/gtr:project/gtr:abstractText', {'gtr': XML_NAMESPACE}).text

    return df


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
    
    # Get GTR summary data
    df = import_csv_to_df(DATAFILENAME)

    # Remove anything that isn't a grant
    df = drop_non_grants(df)

    df = populate_dataframe(df)

    export_to_csv(df, DATAFILENAME, 'gtr_data_titles_and_abs')


if __name__ == '__main__':
    main()