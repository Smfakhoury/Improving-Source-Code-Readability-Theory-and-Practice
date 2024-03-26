## Replication package for 'Improving Source Code Readability Theory and Practice'


### Our data:
* change-distiller.csv 
    * contains ChangeDistiller data
* ref-miner.csv 

    * contains RefactoringMiner data
* source-file-samples/* 
    * contains all before/after code samples (For downloading this content see [download-samples.py](#download-samplespy))
* after-checkstyle.csv 
    * checkstyle warnings for all after files
* before-checkstyle.csv 
    * checkstyle warnings for all before files
* oracle.csv 
    * our oracle of commits, files in the commits and the commit message
* readability-metrics.csv 
    * contains readability scores calculated using Scalabrino's model, Dorn's model and Combined Model.

### download-samples.py

A python script for downloading the before and after version of the files from the commits
into the source-file-samples directory.
It reads the metadata of the commits and files from the oracle.csv.

#### Dependencies

Make sure you have the required python packages installed.
For this you can run the following command to install them with pip:

```bash
pip install "requests==2.*"
pip install "patch==1.*"
```

#### Usage

Create a GitHub API token with at least the right to read public repositories [here](https://github.com/settings/tokens).
Then call the script with the token as parameter, like this:

```bash
./download-samples.py GitHub_API_Token_place_here
```

The download takes about 30 minutes.