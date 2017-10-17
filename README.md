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

