#!/usr/bin/env python
# encoding: utf-8

import os
import math
import time
import tarfile
import logging
import urllib.request
import xml.etree
from xml.etree import cElementTree as et

import pandas as pd
from pandas import ExcelWriter

from config import (COM_INPUTDIR, COM_INPUTFILE, COM_INPUTXMLDIR,
                    COM_XMLNAMESPACE, COM_OUTPUTDIR, COM_OUTPUTFILE, COM_LOGFILE)


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.FileHandler(COM_LOGFILE)
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


def export_to_csv(df, filepath):
    """Exports a df to a csv file and a tar-gzipped csv file.

    :params: a df and a location in which to save it
    :return: nothing, saves a csv
    """
    df.to_csv(filepath)

    # Remove file extension then add it to a tar-gzipped file
    tar_filepath = os.path.splitext(filepath)[0]
    with tarfile.open(tar_filepath + '.tar.gz', 'w:gz') as targz:
        targz.add(filepath)


def clean_input_data(df):
    """Clean GtR input CSV file.

       Set the index to the unique project ID and make column headers lowercase.
    """
    df.set_index('ProjectId', inplace=True)
    df.columns = [x.lower() for x in df.columns]

    return df


def drop_non_grants(df):
    """Drop all non-'Research Grant' category entries in the data."""
    logger.info('Imported df includes ' + str(len(df)) + ' records')

    df = df[df['projectcategory'] == 'Research Grant']

    logger.info('After restricting df to Research Grants only, the df has ' + str(len(df)) + ' records')

    return df


def combine_gtr_abstracts(df):
    """Combine GtR summary data and XML file data.

       Combine the project title and abstract data from XML files for each row in the GtR summary data.
    """
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
            url_filepath = 'file://' + os.path.dirname(os.path.realpath(__file__))
            xml_str = urllib.request.urlopen(url_filepath + '/' + filename).read()

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
        xml_doc = os.path.join(COM_INPUTXMLDIR, curr_project)
        xml_root = retrieve_xml_from_url(xml_doc)
        # The .text is needed to extract the text from the XML element rather than just getting some
        # nonsense summary data
        if xml_root:
            df.loc[curr_project, 'abstract'] = xml_root.find('./gtr:projectComposition/gtr:project/gtr:abstractText', {'gtr': COM_XMLNAMESPACE}).text
        else:
            df.loc[curr_project, 'abstract'] = ''

    return df


def remove_null_entries(df):
    """Remove any grants that do not have an abstract or title to search.

       Drop those grant entries with "N/A" or "N/A" in the abstract and title fields.
    """
    df = df[df['title'] != 'N/A']
    df = df[df['title'] != 'NA']

    df = df[df['abstract'] != 'N/A']
    df = df[df['abstract'] != 'NA']

    logger.info('After removing blank titles or abstracts, the df has ' + str(len(df)) + ' records')

    return(df)

def main():
    start_time = time.time()

    # Cycle through each input GtR summary CSV file and add in abstracts
    # for each project, extracting from the XML project data
    logger.info('Importing data ' + COM_INPUTFILE + '...')

    # Import and clean our input dataset
    input_filepath = os.path.join(COM_INPUTDIR, COM_INPUTFILE)
    df = import_csv_to_df(input_filepath)
    df = clean_input_data(df)

    # For each project row in the input dataset, add in corresponding
    # abstract extracted from its XML project metadata, then remove
    # any entries with no title or abstract
    df = combine_gtr_abstracts(df)
    df = remove_null_entries(df)

    # Save our output dataset with abstracts inserted
    output_filepath = os.path.join(COM_OUTPUTDIR, COM_OUTPUTFILE)
    export_to_csv(df, output_filepath)

    # Display script run time and exit
    execution_time = (time.time() - start_time)/60
    logger.info('The program took ' + str(execution_time) + ' minutes to complete')


if __name__ == '__main__':
    main()
