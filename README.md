## Pairwise PCA Inspection Tool
This project is a part of [SDNist project](https://github.com/usnistgov/SDNist)

This tool allows interactive exploration and highlighting of records in the Pairwise PCA Plot 
metric (see the SDNist Synthetic Data Evaluation library for more on this metric). 
The tool should be installed in the same overall directory as the [crc data bundle](https://github.com/usnistgov/privacy_collaborative_research_cycle/blob/research-acceleration-bundle/crc_data_bundle.zip)
and can be used to investigate scatterplots from all of the deidentified data samples in the bundle.


Version: 1.1.0
Date: Feb 10, 2025
 

### Instructions to run the tool
NOTE: The ***pca>*** string in the commands below indicates that the user is in the **pca** directory.
1. Create a new directory **pca** inside **"crc_data_and_metric_bundle"** directory.
2. Download the **pairwise_pcatool-1.1.0-py3-none-any.whl** file from the [releases](https://github.com/usnistgov/pair-wise_PCA/releases/tag/v1.1.0/)
3. Open terminal or powershell and navigate to the **pca** directory.
4. Now using opened terminal or powershell create a new python virtual environment.
    ```
    pca> python -m venv venv
    ```
5. Now activate the environment:  
    **MAC OS/Linux:**
    ```
    pca> . venv/bin/activate
    ```
    The python virtual environment should now be activated. You should see environment name (**venv** in this case) appended to the terminal prompt as below:  
    ```
    (venv) pca>
    ```
   
    **Windows:**
    ```
    c:\\pca> . venv/Scripts/activate
    ```
    The python virtual environment should now be activated. You should see environment name (**venv** in this case) appended to the command/powershell prompt as below:  
    ```
    (venv) c:\\pca>
    ```
   
6. Now install **pairwise_pcatool-1.1.0-py3-none-any.whl** using pip:
    ```
    (venv)pca> pip install pairwise_pcatool-1.1.0-py3-none-any.whl
    ```

7. Now run the pca tool using command *pcatool*:
    ```
   (venv)pca> pcatool
    ```
   

Credits 
----------

- [Christine Task](mailto:christine.task@knexusresearch.com) - Project technical lead - christine.task@knexusresearch.com
- [Karan Bhagat](https://github.com/kbtriangulum) - Contributor
- [Gary Howarth](https://www.nist.gov/people/gary-howarth) - Project PI - gary.howarth@nist.gov
