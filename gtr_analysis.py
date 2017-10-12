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



DATAFILENAME = "./data/projectsearch-1507107194469.csv"
STOREFILENAME = "./output/"





def import_csv_to_df(filename):
    """
    Imports a csv file into a Pandas dataframe
    :params: an xls file and a sheetname from that file
    :return: a df
    """
    
    return pd.read_csv(filename)
   
    
def drop_non_grants(df):

    df = df[df['ProjectCategory'] == 'Research Grant']

    return df


def populate_dataframe(df):

    """
    Convert XML files into a dataframe
    """

    XML_PREPEND = 'file:///Users/user/Desktop/Git/software_in_grants_GTR/data/xml_data/'
    XML_NAMESPACE = 'http://gtr.rcuk.ac.uk/gtr/api/project'



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


    # Get list of all files we're looking for
    all_xml_files = XML_PREPEND + df['ProjectId'].astype(str)

#    print(df['ProjectId'])

    for curr_xml in all_xml_files:
        print(curr_xml)
        xml_root = retrieve_xml_from_url(curr_xml)
        print(xml_root)
        xml_element = xml_root.find('.//gtr:title', {'gtr': XML_NAMESPACE})
        print(xml_element)

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

    all_data_df = populate_dataframe(df)

#    xml_root = retrieve_xml_from_url('file:///Users/user/Desktop/Git/software_in_grants_GTR/data/77AF9305-8F4F-43FA-8D92-675180CD46A4')

#    xml_element = xml_root.find('.//gtr:title', {'gtr': 'http://gtr.rcuk.ac.uk/api'})
    
#    print(xml_element.text)

#    df = find_keywords(df, 'Title')
    
#    print(df.columns)

if __name__ == '__main__':
    main()