import os
from multiprocessing import Pool
from timeit import default_timer as timer

input_dir = 'naip'

command = 'gdal_translate -of GTiff -co COMPRESS=JPEG {input} {output}'

def process(file):
    input = os.path.join(input_dir, file)
    filename = os.path.splitext(os.path.basename(file))[0]
    output =  os.path.join(input_dir, filename + '.tif')
    os.system(command.format(input=input, output=output))
    
files = [file for file in os.listdir(input_dir) if file.endswith('.jp2')]

if __name__ == '__main__':
  start = timer()
  p = Pool(4)
  p.map(process, files)
  end = timer()
  print(end - start)
  
  start = timer()
  for file in files:
    process(file)
  end = timer()
  print(end - start)

