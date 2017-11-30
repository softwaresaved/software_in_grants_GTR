# A study of software mentions in grants

In this study, I'll investigate the successful grant applications provided by [Gateway to Research](http://gtr.rcuk.ac.uk/) to discover the prevalence of software in those grants, which will allow for an investigation into the amount invested into software by the Research Councils. The aim is to update the study described [in this post](https://www.software.ac.uk/blog/2016-09-12-ps840-million-uks-investment-software-reliant-research-2013).

## Important points

* Licence for the code and data can be found in the the LICENCE and LICENCE_DATA files respectively.
* The code runs on Python 3.
* The data derives from [Gateway to Research](http://gtr.rcuk.ac.uk/).

## Summary of process

* Get summary data on all research grants from Gateay to Research from the "All Data" csv download [on this page](http://gtr.rcuk.ac.uk/search/project?term=*). Store this as ```projectsearch-1507107194469.csv.```
* Download details of research grants as XML documents using code written by [Steve Crouch](https://github.com/softwaresaved/training-set-collector).
* Combine summary data with titles and abstracts from XML data (```combine_gtr_data.py``` used for this purpose)
* Analyse results in Python

## How to reproduce the results of this analysis

### Set up

Get the files and data:

1. [Clone the git repository](https://github.com/softwaresaved/software_in_grants_GTR)

Prepare for running Python:

1. If not already installed, [install virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/):
   * ```pip install virtualenv```
1. Create a project folder:
   * ```virtualenv -p <location of Python3 install directory> <name of project>```
1. Activate the virtual environment:
   * ```source <name of project>/bin/activate ```
1. Install libraries:
   * ```pip install -r requirements.txt ```

Combine summary and abstract data:

1. Run the script:
    * ```python combine_gtr_data.py```
    * This takes the "All Data" csv, drops any record not related to a research grant, then populates the research grants with title and abstract data downloaded from the Gateway to Research API.
    * It drops any records that lack an abstract (they have "NA" or "N/A" in the abstract field)
    * And then it saves the resulting dataframe as ```gtr_data_titles_and_abs.csv```
1. Run the analysis script:
    * ```python gtr_analysis.py```
    * This drops all records from before the year 2000 (data collection was not as reliable before this date) and drops any record where the start date occurs after the end data (not trustworthy data)
    * It reviews the data and collects the years and funder names contained in it
    * It counts the total number of grants contained in the data
    * It finds a whether words from a list of keywords ```keyword_list``` are contained in each title and abstract
    * For each grant, it calculates how much of the funding would be spent each year if the funding was evenly spread over the years that the grant spans (i.e. over the grant's lifetime)
    * It then calculates the important things:
            1. The number of software-related grants found with a keyword each year (both a count and a percentage)
            1. The number of software-related grants funded by each funder each year (both a count and a percentage)
            1. The amount of funding invested into software-related grants each year (just a value)
    
    
