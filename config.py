#!/usr/bin/env python
# encoding: utf-8

# The downloaded and prepared GtR summary CSV files we wish to process
# via combination, each with an output file path for each generated
# CSV file. Each output CSV file contains the input GtR summary file
# with abstracts inserted
INPUTOUTPUT_PROCESSFILES = [
    ['gtrdata-all-clean-20180419.csv', 'gtr_data_titles_and_abs-all.csv'],
    ['gtrdata-researchgrants-clean-20180419.csv', 'gtr_data_titles_and_abs-researchgrants.csv'],
]

#### Dataset combination config

# Where our GtR summary input CSV files are stored
COM_INPUTDIR = 'input'

# The downloaded XML summary files for each grant,
# containing the titles and abstracts we want
COM_INPUTXMLDIR = 'input/xml_data'

# The XML namespace we need to search the XML
COM_XMLNAMESPACE = 'http://gtr.ukri.org/api'

# Where our output CSV files are stored
COM_OUTPUTDIR = 'intermediate'

# Our combination process log file
COM_LOGFILE = 'log/combine_gtr_data.log'


#### Analysis config

# Which fields of the grant we're going to search
ANA_SEARCHFIELDS = ['title', 'abstract']

# Location of background data for verification
ANA_BACKGROUNDOUTPUTDIR = 'background_data'

# Where output CSV and PNG chart data will be stored, containing
# a subdirectory for each set of input data
ANA_OUTPUTDIR = 'output'

# Years that the Institute has existed, except 2018
ANA_SUBSETYEARS = [2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017]

# Our analysis process log file
ANA_LOGFILE = 'log/gtr_analysis.log'
