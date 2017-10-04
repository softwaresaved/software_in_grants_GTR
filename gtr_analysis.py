#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
from pandas import ExcelWriter
import numpy as np
import csv
import matplotlib.pyplot as plt
import math
from textwrap import wrap


DATAFILENAME = "./data/projectsearch-1507107194469.csv"
STOREFILENAME = "./output/"


def import_csv_to_df(filename):
    """
    Imports a csv file into a Pandas dataframe
    :params: get an xls file and a sheetname from that file
    :return: a df
    """
    
    return pd.read_csv(filename)


def main():
    
    df = import_csv_to_df(DATAFILENAME)
    print(len(df))


if __name__ == '__main__':
    main()