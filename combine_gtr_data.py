#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
from pandas import ExcelWriter
import numpy as np
import csv
import math
import urllib.request
from xml.etree import cElementTree as et
import xml.etree
import time
import logging

DATASTORE = './data/'
DATAFILENAME = 'gtrdata-clean-20180406.csv'
LOGGERLOCATION = "./log_combine_gtr_data.log"


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


def prepare_df(df):
    
    # Use the project ID as the index
    df.set_index('ProjectId', inplace=True)

    # Make column headers lowercase
    df.columns = [x.lower() for x in df.columns]

    return df


def drop_non_grants(df):

    """ Only want 'Research Grant' categories in the data, so this drops everything but
        them from the dataframe
    """

    logger.info('Imported df includes ' + str(len(df)) + ' records')

    df = df[df['projectcategory'] == 'Research Grant']

    logger.info('After restricting df to Research Grants only, the df has ' + str(len(df)) + ' records')

    return df


def populate_dataframe(df):

    """
    Grab data from XML files and combine it with the gtr summary data
    """

    # Define where XML data is stored and the namespace it uses
    FILE_PATH = 'file:///Users/user/Projects/SSI/software_in_grants_GTR/data/xml_data/'
    #XML_NAMESPACE = 'http://gtr.rcuk.ac.uk/api'
    XML_NAMESPACE = 'http://gtr.ukri.org/api'


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
        except (urllib.request.HTTPError, urllib.request.URLError,
                xml.etree.ElementTree.ParseError) as err:
            print(filename + ": " + str(err))

        return xml_root


    # Go through each project, get the corresponding XML file and
    # add the relevant abstract from the XML to the dataframe
    for curr_project in df.index.astype(str):
        # It takes some time, so it's useful to have this outputted
        # just to see that the program is still working
        print(curr_project)
        xml_doc = FILE_PATH + curr_project
        xml_root = retrieve_xml_from_url(xml_doc)
        # The .text is needed to extract the text from the XML element rather than just getting some
        # nonsense summary data
        if xml_root:
            df.loc[curr_project, 'abstract'] = xml_root.find('./gtr:projectComposition/gtr:project/gtr:abstractText', {'gtr': XML_NAMESPACE}).text
        else:
            df.loc[curr_project, 'abstract'] = ''

    return df


def kill_the_spare(df):

    # Remove any grants that do not have a title or abstract to search
    # These are the ones with "N/A" in the appropriate field

    df = df[df['abstract']!='N/A']
    df = df[df['abstract']!='NA']

    logger.info('After removing blank titles or abstracts, the df has ' + str(len(df)) + ' records')

    return(df)

def main():

    start_time = time.time()

    # Get GTR summary data
    logger.info('Importing data...')
    df = import_csv_to_df(DATASTORE + DATAFILENAME)

    df = prepare_df(df)

    # Remove anything that isn't a grant
    df = drop_non_grants(df)

    df = populate_dataframe(df)

    df = kill_the_spare(df)

    export_to_csv(df, DATASTORE, 'gtr_data_titles_and_abs')

    execution_time = (time.time() - start_time)/60
    
    logger.info('The program took ' + str(execution_time) + ' minutes to complete')


if __name__ == '__main__':
    main()
