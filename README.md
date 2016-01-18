# Python-based sensor analysis
###### Supporting Python scripts for analysis of TAUT study data

Scripts originally designed to analyse data for Chapter 3 of PhD thesis: *A Data-Driven Contextual Reminder Delivery Framework*

Full manuscript available here: (//TODO)

## Description
This program was designed to extract features from sensor data recorded on an android smartphone.

The sensor data is then paired with usage data from an external database for data labelling.

The program works in the following manner:

1. Reads a csv file containing reminder data from external database
2. Creates dictionary of users and reminder data
3. Uses dictionary to iterates raw sensor files looking for matching timestamps
4. When match is found sensor file is processed
5. Establishes cutoff indexes based on defined window length
6. Produces descriptive statistics for windowed signal, incl. rms (root mean square), svm (signal vector magnitude)
7. Collates the data and writes to an external csv file for further analysis (Weka, Hadoop, etc.)

## Dependencies
* NumPy ([link](http://www.numpy.org))
* SciPy ([link](http://www.scipy.org))
