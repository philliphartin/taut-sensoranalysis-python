# Python-based sensor analysis
###### Supporting Python scripts for analysis of TAUT study data

Scripts originally designed to analyse data for Chapter 3 of PhD thesis: *A Data-Driven Contextual Reminder Delivery Framework*

Full manuscript available here: (//TODO)

## Description
This program was designed to extract features from sensor data recorded on an android smartphone.

The sensor data is then paired with usage data from an external database for data labelling.

The program operates in the following manner:

1. List of desired window lengths are input
2. Reads a csv file containing reminder data from external database
3. Creates dictionary of users and reminder data
4. Uses dictionary to iterates raw sensor files looking for matching timestamps
5. When match is found sensor file is processed
6. Establishes cutoff indexes based on defined window length
7. Strips data into axis components for window length, and generates a component signal vector magnitude signal (SVM)
8. Applies a median filter to resulting signals (IF continuous, i.e. Accelerometer, Magnetometer)
9. Applies offset calibration to SVM signal based upon median value.
9. Produces features based on descriptive statistics for all windowed signals (mean, max, min, var, std, rms, etc.)
10. Writes the features to a sorted and labelled external csv file for further analysis from third party tools (Weka, Hadoop, etc.)
11. Re-Imports CSV file and then formats to a Weka .arff file, ready for direct import.

## Dependencies
* NumPy ([link](http://www.numpy.org))
* SciPy ([link](http://www.scipy.org))

### Disclaimer
Code produced during last week of PhD enrollment, and first time using python. Apologies for hackish approaches here and there. Will tidy up later!