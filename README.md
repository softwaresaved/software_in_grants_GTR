# A study of software mentions in grants

In this study, I'll investigate the successful grant applications provided by [Gateway to Research](http://gtr.rcuk.ac.uk/) to discover the prevalence of software in those grants, which will allow for an investigation into the amount invested into software by the Research Councils. The aim is to update the study described [in this post](https://www.software.ac.uk/blog/2016-09-12-ps840-million-uks-investment-software-reliant-research-2013).

## Important points

* Licence for the code and data can be found in the the LICENCE and LICENCE_DATA files respectively.
* The code runs on Python 3 and uses Pandas to conduct the analyses and Matplotlib to generate the PNG charts.
* The data derives from [Gateway to Research](http://gtr.rcuk.ac.uk/).

## Summary of analysis process

* Get summary data on all grants from Gateway to Research from the "All Data" CSV download [on this page](http://gtr.rcuk.ac.uk/search/project?term=*). Store this as ```projectsearch-1507107194469.csv``` (the number will change with each subsesquent download).
* Download details of all grants as XML documents using code written by [Steve Crouch](https://github.com/softwaresaved/training-set-collector).
* Combine summary data with titles and abstracts from XML data using ```combine_gtr_data.py```
* Analyse combined summary data in Python using ```gtr_analysis.py``` for two analyses: one for all grants data, and one just for those that identify as research grants
* Output results in CSV and PNG chart formats for each analysis

## Description of the output

* All output files are stored in the ```output``` directory, with each analyses' CSV results and PNG charts stored within separate subdirectories ```results-all``` and ```results-researchgrants```
* CSV results files
    * ```final_df``` & ```final_df.tar.gz```: a copy of the dataframe after the analysis has been completed. It's big, and it contains columns related to each of the analytical steps conducted to understand the data. ```final_df``` can be generated either by re-running the analysis or extracting it from ```final_df.tar.gz```
    * ```only_grants_related_to_software``` & ```only_grants_related_to_software.tar.gz```: a subset of ```final_df```, but this file contains only records that were found to be related to software. ```only_grants_related_to_software``` can be generated either by re-running the analysis or extracting it from ```only_grants_related_to_software.tar.gz```
    * ```keywords_found_count```: a summary count of keywords (the first column) that were found in each of the years and in each section of the grant that was searched
    * ```keywords_found_percentage```: the same as the above, but now as a percentage relative to the total number of grants recorded in the year in question (i.e. this is the percentage of all grants from that year that contained the keyword)
    * ```software_grants_by_funder```: for each funder, the number of software-related grants found for a particualr start year, and the percentage that this makes up of all the grants that the funder started in that year
    * ```search_term_popularity_all```: a summary count of the occurrences of all search terms across all funders
    * ```yearly_all_grants_costs_by_funder```: all grants costs by funder across each year included in the data
    * ```yearly_software_grants_costs_by_funder```: all software-related grants costs by funder across each year included in the data
    * ```all_grants_count```: a count of all grants in the data set divided into the year in which the grant starts
* PNG chart files
    * ```search_term_popularity_all``` & ```search_term_popularity_<funder>```: summaries of the popularity of search terms across all funders and each funder individually
    * ```software_spend_all``` & ```software_spend_<funder>```: summary of the spending on software across all funders and each funder individually, across each year in the data
    * ```software_spend_all_percent``` & ```software_spend_percent_<funder>```: summary of software spending as a percentage of funding for each year, for all funders and each funder individually
    * ```software_spend_all_average_amount```: summary of average software spending per year for each funder
    * ```software_spend_all_average_percent```: summary of average software spending per year for each funder, as a percentage of total funder's funding
* Background data about all grants - not just those related to software - are stored in the ```output/background_data``` directory
    * ```all_years_in_data```: a list spaning all years in the data from the start year of the earliest start date to the end year of the latest end date
    * ```end_years_in_data```: a list of all the years in which a grant ends
    * ```start_years_in_data```: a list of all the years in which a grant starts
    * ```funders_in_data```: a list of all the funders that funded projects in the dataset

## How to reproduce the results of this analysis

### Set up

Get the files and data:

1. [Clone the git repository](https://github.com/softwaresaved/software_in_grants_GTR)

Install the script prerequisites:

1. If not already installed, [install virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/):
   * ```pip install virtualenv```
1. Change directory into the cloned repository
   * ```cd software_in_grants_GTR```
1. Create a project folder:
   * ```virtualenv -p <location of Python3 install directory> venv```
1. Activate the virtual environment:
   * ```source venv/bin/activate ```
1. Install Python library dependencies:
   * ```pip install -r requirements.txt ```

If you wish to change the configuration of the combination or analysis processes, and not simply regenerate the output data,
you can edit ```config.py```.

Combine summary and abstract data and run the analyses:

1. Run the grants data combination script:
    * ```python combine_gtr_data.py```
    * This takes the ```gtrdata-clean-20180419``` CSV file, then populates it with title and abstract data downloaded using the Gateway to Research API
    * It drops any records that lack a title or abstract (they have "NA" or "N/A" in the title or abstract fields)
    * And then it saves the resulting dataframe as ```gtr_data_titles_and_abs-all.csv``` in the ```intermediate``` directory
1. Run the analysis script, which operates firstly over grants that are classified as 'Research Grants' and secondly over all grants, storing the results of each analysis within a subdirectory of ```output```:
    * ```python gtr_analysis.py```
    * This uses the ```gtr_data_titles_and_abs-all.csv``` file generated above
    * This drops all records from before the year 2000 (data collection was not as reliable before this date) and drops any record where the start date occurs after the end data (not trustworthy data)
    * It reviews the data and collects the years and funder names contained in it
    * It counts the total number of grants contained in the data
    * For each grant, it calculates how much of the funding would be spent each year if the funding was evenly spread over the years that the grant spans (i.e. over the grant's lifetime)
    * It analyses whether words from a list of keywords ```keyword_list``` are contained in each title and abstract
    * The script then extracts the subset of data related to software (i.e. those that contain at least one software-related keyword)
    * It then conducts an analysis on that subset of data, generating CSV and PNG chart results (as identified above) for each part of the analysis

If you just want to run the second step without having run the first step, first extract the ```gtr_data_titles_and_abs-all.csv``` from its pregenerated tarfile
within the ```intermediate``` subdirectory, e.g.:

* ```cd intermediate```
* ```tar -xzf gtr_data_titles_and_abs-all.tar.gz```
* ```cd ..```
