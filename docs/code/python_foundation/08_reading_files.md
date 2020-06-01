# Reading Files

Python provides built-in functions for reading and writing files.  

To read a file, we must know the path of the file on the disk. Python has a module called `os` that has helper functions that helps dealing with the the operating system. Advantage of using the `os` module is that the code you write will work without change on any suppored operating systems.


```python
import os
```

To open a file, we need to know the path to the file. We will now open and read the file `worldcitites.csv` located in your data package. In your data package the data folder is in the `data/` directory. We can construct the relative path to the file using the `os.path.join()` method.


```python
data_pkg_path = 'data'
filename = 'worldcities.csv'
path = os.path.join(data_pkg_path, filename)
print(path)
```

    data/worldcities.csv


To open the file, use the built-in `open()` function. We specify the *mode* as `r` which means read-only. If we wanted to change the file contents or write a new file, we would open it with `w` mode.

The open() function returns a file object. We can call the  `readline()` method for reading the content of the file, one line at a time.

It is a good practice to always close the file when you are done with it. To close the file, we must call the `close()` method on the file object.


```python
f = open(path, 'r')
print(f.readline())
print(f.readline())
f.close()
```

    "city","city_ascii","lat","lng","country","iso2","iso3","admin_name","capital","population","id"
    
    "Tokyo","Tokyo","35.6850","139.7514","Japan","JP","JPN","Tōkyō","primary","35676000","1392685764"
    


Calling `readline()` for each line of the file is tedious. Ideally, we want to loop through all the lines in file. You can iterate through the file object like below.

We can loop through each line of the file and increase the `count` variable by 1 for each iteration of the loop. At the end, the count variable's value will be equal to the number of lines in the file.


```python
f = open(path, 'r')

count = 0
for line in f:
    count += 1
f.close()
print(count)
```

    15494


## Exercise

Print first 5 lines of the file. 

- Hint: Use break statement

----
