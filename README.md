### Taylor J. Weidman | taylorjweidman@gmail.com | https://taylorjweidman.com

# Voter Data Pipeline

The pipeline is broken into six steps. I use only the relevant variables in each step and include a linking variable to merge at any point in the pipeline. The idea for this pipeline is to start with cleaned data, then use just the subset of variables to perform the relevant data step. Then I'll bring everything together at the end, generating a voter class in the link step. The class should then give me a better sense of the voter in time series. But that last step is much later. I don't need to worry about time series at the moment. 


## Data 1 Clean

This step simply generates voter data files with a set of standardized (relabeling existing and generating new) variables from raw voter files.

## Data 2 Geocode

This step breaks cleaned voter data into batches and sends them to the Census Bureau Geocoder using the python API (https://pypi.org/project/censusgeocode/). The returned batches are saved and merged into a file containing geocoded variables from the geocoder and the linking variable.

I then perform an analysis of which types of voters were unable to be geocoded.

### To Do
1. Geocode the errors using another geocoder
2. Maybe geocode using shapefiles?

## Data 3 Neighborhoods

This step takes voters geocoded location, generates square neighborhoods, assigns voters to them, generates their statistics, and assigns neighborhood statistics to their voters.

I then perform an analysis of the square neighborhoods.

### To Do
1. Rewrite using raymond's video - https://youtu.be/OSGv2VnC0go

## Data 4 KNN

This step uses square neighborhoods to partition the geographic space, selects the nearest k voters for every voter, generates the statistics of this neighborhood, and assigns the statistics to the voter.

I then perform an anslysis of the KNNs. 

### To Do
1. Vectorize knn function
2. Parallelize using Concurrent Futures - https://docs.python.org/3/library/concurrent.futures.html
3. Rewrite using raymond's video - https://youtu.be/OSGv2VnC0go

## Data 5 Supplemental

This step brings in data external to the voter file and assigns it to voters in the relevant ways.

## Data -1 Link

This step brings all the data together and sends it to the relevant project files.

### To Do
1. Rewrite using classes