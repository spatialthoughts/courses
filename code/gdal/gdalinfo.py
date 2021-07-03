import os
import json
import subprocess

input_dir = 'srtm'

command = 'gdalinfo -stats -json {input}'
for file in os.listdir(input_dir):
  if file.endswith('.hgt'):
    input = os.path.join(input_dir, file)
    filename = os.path.splitext(os.path.basename(file))[0]
    output = subprocess.check_output(command.format(input=input), shell=True)
    info_dict = json.loads(output)
    bands = info_dict['bands']
    for band in bands:
      band_id = band['band']
      min = band['minimum']
      max = band['maximum']
      print('{},{},{},{}'.format(filename, band_id, min, max))
     

