import os

input_dir = 'naip'

command = 'gdal_translate -of GTiff -co COMPRESS=JPEG {input} {output}'
for file in os.listdir(input_dir):
  if file.endswith('.jp2'):
    input = os.path.join(input_dir, file)
    filename = os.path.splitext(os.path.basename(file))[0]
    output =  os.path.join(input_dir, filename + '.tif')
    os.system(command.format(input=input, output=output))

