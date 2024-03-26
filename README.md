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
into the `source-file-samples` directory.
It reads the metadata of the commits and files from the `oracle.csv`.

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

#### Known issues

##### Commit not found

Some commits are not available anymore.
Actual known (in March 2024):

| Reason                                                                                 | Affected rows |
|----------------------------------------------------------------------------------------|---------------|
| [Repository](https://github.com/Dexels/dexels.repository) is not available anymore.    | 410 to 456    |
| [Repository](https://github.com/eclipse/eclipse.platform.ui) is not available anymore. | 1850 to 1866  |
| [Repository](https://github.com/eclipse/jgit) is not available anymore.                | 1877 to 1880  |

Affected rows produce appropriated message on `stderr` like this:

```
ERROR: Commit, from row 410 in oracle.csv, not found.
```

##### Renamed files

In the `oracle.csv` are also files listed, which were renamed in the corresponding commit.
So there are no content changes, so nothing to evaluate in matter of readability.

Affected rows produce appropriated message on `stdout` like this:

```
Row 391 of oracle.csv skipped, because the file was only renamed.
```


