#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
from pandas import ExcelWriter
import numpy as np
import csv
import math
import urllib.request
from xml.etree import cElementTree as et


DATAFILENAME = "./data/gtrdata-clean.csv"


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

    """ Only want 'Research Grant' categories in the data, so this drops everything but
        them from the dataframe
    """

    df = df[df['ProjectCategory'] == 'Research Grant']

    return df


def populate_dataframe(df):

    """
    Grab data from XML files and combine it with the gtr summary data
    """

    # Define where XML data is stored and the namespace it uses
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


    # Go through each project, get the corresponding XML file and
    # add the relevant title and abstract from the XML to the dataframe
    for curr_project in df['ProjectId'].astype(str):
        # It takes some time, so it's useful to have this outputted
        # just to see that the program is still working
        print(curr_project)
        xml_doc = FILE_PATH + curr_project
        xml_root = retrieve_xml_from_url(xml_doc)
        # The .text is needed to extract the text from the XML element rather than just getting some
        # nonsense summary data
        df['title'] = xml_root.find('./gtr:projectComposition/gtr:project/gtr:title', {'gtr': XML_NAMESPACE}).text
        df['abstract'] = xml_root.find('./gtr:projectComposition/gtr:project/gtr:abstractText', {'gtr': XML_NAMESPACE}).text

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