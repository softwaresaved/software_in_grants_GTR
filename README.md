# A study of software mentions in grants

In this study, I'll investigate the successful grant applications provided by [Gateway to Research](http://gtr.rcuk.ac.uk/) to discover the prevalence of software in those grants, which will allow for an investigation into the amount invested into software by the Research Councils. The aim is to update the study described [in this post](https://www.software.ac.uk/blog/2016-09-12-ps840-million-uks-investment-software-reliant-research-2013).

## Important points

* Licence for the code and data can be found in the the LICENCE and LICENCE_DATA files respectively.
* The code runs on Python 3.
* The data derives from [Gateway to Research](http://gtr.rcuk.ac.uk/).

## Summary of process

* Get summary data on all research grants from Gateay to Research from the "All Data" csv download [on this page](http://gtr.rcuk.ac.uk/search/project?term=*). Store this as ```projectsearch-1507107194469.csv.``` (the number will change with each subsesquent download.
* Download details of research grants as XML documents using code written by [Steve Crouch](https://github.com/softwaresaved/training-set-collector).
* Combine summary data with titles and abstracts from XML data (```combine_gtr_data.py``` used for this purpose)
* Analyse results in Python

## Description of the output

* All output files are stored in the ```output``` directory as ```.csv``` files
    * ```final_df```: a copy of the dataframe after the analysis has been compeleted. It's big, and it contains columns related to each of the analytical steps conducted to understand the data.
    * ```only_grants_related_to_software```: the same as above, but this file contains only records that were found to be related to software
    * ```keywords_found_count```: shows the number of times keywords (the first column) were found in each of the years and in each section of the grant that was searched
    * ```keywords_found_percentage```: the same as the above, but now as a percentage relative to the total number of grants recorded in the year in question (i.e. this is the percentage of all grants from that year that contained the keyword)
    * ```software_grants_by_funder```: for each funder, the number of software-related grants found for a particualr start year, and the percentage that this makes up of all the grants that the funder started in that year
    * ```software_grants_total_funding```:  the total amount of funding invested each year by all funders into software-related grants
* Background data about all grants - not just those related to software - are stored in the ```output/background_data``` directory
    * ```all_grants_count```: a count of all grants in the data set divided into the year in which the grant starts
    * ```all_years_in_data```: a list spaning all years in the data from the start year of the earliest start date to the end of the latest end date
    * ```end_years_in_data```: a list of all the years in which a grant ends
    * ```start_years_in_data```: a list of all the years in which a grant starts
    * ```funders_in_data```: a list of all the funders that funded projects in the dataset
    
## How to reproduce the results of this analysis

### Set up

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
    
    
