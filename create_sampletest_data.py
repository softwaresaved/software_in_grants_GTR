#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
import numpy as np
import csv
import os

DATAFILENAME = "./data/gtr_data_titles_and_abs.csv"
DATASTORENAME = "./data/"
# The df will be reduced by a factor of...
CUTDOWNFACTOR = 10

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


def reduce_size(df):
    
    df['random_number'] = np.random.randint(0,CUTDOWNFACTOR, size=len(df))
    print('Length before cut down... ' + str(len(df)))
    df = df[df['random_number']==0]
    print('Length AFTER cut down... ' + str(len(df)))

    return df

def main():
    
    
    
    df = import_csv_to_df(DATAFILENAME)
    
    df = reduce_size(df)
    
    filename = os.path.basename(DATAFILENAME)[:-4] + '_testdata'
        
    df = export_to_csv(df, DATASTORENAME, filename)

if __name__ == '__main__':
    main()