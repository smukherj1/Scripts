# Scripts
Random scripts I use on a day to day basis for a variety of tasks. Following are the names of the scripts
and a brienf description of what they do

## 1. count_distinct.py
Given a filename as the first and only command line argument, this script goes through each line and counts
the number of times a line occurs in the file. For example a file foo.txt with the following contents:-
```
hi how are you
foo
bar
foo
hi how are you
Hi how are you
```
will output (not neessarily in this order):-
```
hi how are you 2
foo 2
bar 1
Hi how are you 1
```

## 2. cpucorecount.py
Python module to get the number of physical cores in the current system. Most languages provide easy ways to
obtain the logical core count but physical core count is harder to get. Typical usage is as follows
```python
import cpucorecount as c

print 'This system has %d physical cpu cores'%c.getCPUPhysicalCoreCount()
```
Sample Output for an Intel i7 3770k with 4 physical cores and 8 logical cores:-
```
This system has 4 physical cpu cores
```
**Note:** Currently only windows is supported which parses output from the 'WMIC' tool. Linux support will be added by
parsing the '/proc/cpuinfo' file.
