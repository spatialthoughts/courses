# Reading Files

Python provides built-in functions for reading and writing files.  

To read a file, we must know the path of the file on the disk. Python has a module called `os` that has helper functions that helps dealing with the the operating system. Advantage of using the `os` module is that the code you write will work without change on any suppored operating systems.


```python
import os
```

To open a file, we need to know the path to the file. We will now open and read the file `worldcities.csv` located in your data package. In your data package the data folder is in the `data/` directory. We can construct the relative path to the file using the `os.path.join()` method.


```python
data_pkg_path = 'data'
filename = 'worldcities.csv'
path = os.path.join(data_pkg_path, filename)
print(path)
```

To open the file, use the built-in `open()` function. We specify the *mode* as `r` which means read-only. If we wanted to change the file contents or write a new file, we would open it with `w` mode.

Our input file also contains Unicode characters, so we specify `UTF-8` as the encoding.

It is a good practice to always close the file when you are done with it. To close the file, we must call the `close()` method on the file object after processing it.


```python
f = open(path, 'r', encoding='utf-8')
# Do something
f.close()
```

The easiest way to read the content of the file is to loop through it line by line. If we just wanted to read the first few lines of the file, we create a variable `count` and increase it by 1 for each iteration of the loop. When the `count` value reaches the desired number of lines, we use the `break` statement to exit the loop.


```python
f = open(path, 'r', encoding='utf-8')

count = 0
for line in f:
    print(line)
    count += 1
    if count == 5:
        break
f.close()
```

## Exercise

Count the number of lines in the file and print the total count. You can adapt the for-loop above to count the total number lines in the file.


```python
import os
data_pkg_path = 'data'
filename = 'worldcities.csv'
path = os.path.join(data_pkg_path, filename)

# Add code to open the file and print the total number of lines
# Hint: You do not need to print the line, just increment the count 
#       and print the value of the variable once the loop is finished.
```
