#!/usr/bin/env python
# encoding: utf-8


#### Dataset combination config

# Where our GtR summary input CSV files are stored
COM_INPUTDIR = 'input'
COM_INPUTFILE = 'gtrdata-clean-20180419.csv'

# The downloaded XML summary files for each grant,
# containing the titles and abstracts we want
COM_INPUTXMLDIR = 'input/xml_data'

# The XML namespace we need to search the XML
COM_XMLNAMESPACE = 'http://gtr.ukri.org/api'

# Where our output CSV file is stored, with
# abstracts inserted
COM_OUTPUTDIR = 'intermediate'
COM_OUTPUTFILE = 'gtr_data_titles_and_abs-all.csv'

# Our combination process log file
COM_LOGFILE = 'log/combine_gtr_data.log'


#### Analysis config

# Scope of what subset of the input data to use
# for each separate analysis, indicated by what
# to match in the ProjectCategory field as a
# regular expression
ANA_ANALYSES = [
    # Includes just RCUK
    [ 'researchgrants', 'Research Grant' ],

    # Includes everything, including Innovate UK
    # and all grant types
    [ 'all', '' ],
]

# Which fields of the grant we're going to search
ANA_SEARCHFIELDS = ['title', 'abstract']

# Location of background data for verification
ANA_BACKGROUNDOUTPUTDIR = 'background_data'

# Where output CSV and PNG chart data will be stored, containing
# a subdirectory for each set of input data
ANA_OUTPUTDIR = 'output'
ANA_OUTPUTPNGSUBDIR = 'png'
ANA_OUTPUTCSVSUBDIR = 'csv'

# Subset of the years we wish to analyse
ANA_SUBSETYEARS = [2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017]

# Our analysis process log file
ANA_LOGFILE = 'log/gtr_analysis.log'
