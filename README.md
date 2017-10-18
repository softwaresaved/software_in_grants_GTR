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
    * ```python 
