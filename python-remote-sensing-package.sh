# Packaging script to build python-dataviz course
# Should be run after changing any *.ipynb files
# Tested on MacOS only
OUTPUT_DIR=~/Downloads/
PACKAGE_DIR=~/Downloads/python_remote_sensing
SOLUTIONS_DIR=~/Downloads/python_remote_sensing_solutions
WEB_DIR=~/projects/python-dataviz-web

#mkdir -p $SOLUTIONS_DIR

# Main Notebooks
jupyter-nbconvert --to markdown  code/python_remote_sensing/*.ipynb --output-dir python-remote-sensing-output/


# matplotlib figures end up with a title 'png'. Remove it with sed
sed -i '' 's/\[png\]/\[\]/g' python-remote-sensing-output/*.md
# image paths need to be set relative to the folder. Replace it with sed
sed -i '' -E 's/\((.+_files)/\(python-remote-sensing-output\/\1/g' python-remote-sensing-output/*.md
#cp -R code/python_remote_sensing/solutions/* $SOLUTIONS_DIR/

# Update python-dataviz-web repository
#cp code/python_remote_sensing/*.ipynb $WEB_DIR/
#cp code/python_remote_sensing/*.py $WEB_DIR/
#cp -R code/python_remote_sensing/streamlit $WEB_DIR/