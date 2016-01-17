Supporting Python scripts for analysis of TAUT study data
=============
Scripts originally designed to analyse data for Chapter 3 (A Data-Driven Contextual Reminder Delivery Framework) of PhD thesis.
Full thesis manuscript available here: (//TODO)

This program was designed to extract features from sensor data recorded on an android smartphone.
The sensor data is then paired with usage data from an external database, and each entry is labeled as ('Acknowledged' or 'Missed')

The program works in the following manner:
0. Reads a csv file containing reminder data from external database
0. Creates dictionary of users and reminder data
0. Uses dictionary to iterates raw sensor files looking for matching timestamps
0. When match is found sensor file is processed
0. Establishes cutoff indexes based on defined window length
0. Produces descriptive statistics for windowed signal, incl. rms (root mean square), svm (signal vector magnitude)
0. Collates the data and writes to an external csv file for further analysis (Weka, Hadoop, etc.)

Dependencies
-------
* NumPy, SciPy
