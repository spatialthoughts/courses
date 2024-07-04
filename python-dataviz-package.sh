# Packaging script to build python-dataviz course
# Should be run after changing any *.ipynb files
# Tested on MacOS only
OUTPUT_DIR=~/Downloads/
PACKAGE_DIR=~/Downloads/python_dataviz
SOLUTIONS_DIR=~/Downloads/python_dataviz_solutions
WEB_DIR=~/projects/python-dataviz-web

mkdir -p $SOLUTIONS_DIR

# Main Notebooks
jupyter-nbconvert --to markdown  code/python_dataviz/*.ipynb --output-dir python-dataviz-output/


# matplotlib figures end up with a title 'png'. Remove it with sed
sed -i '' 's/\[png\]/\[\]/g' python-dataviz-output/*.md
# image paths need to be set relative to the folder. Replace it with sed
sed -i '' -E 's/\((.+_files)/\(python-dataviz-output\/\1/g' python-dataviz-output/*.md
cp -R code/python_dataviz/solutions/* $SOLUTIONS_DIR/
# Remove assignment solution
rm $SOLUTIONS_DIR/assignment.ipynb
# Update python-dataviz-web repository
cp code/python_dataviz/*.ipynb $WEB_DIR/
cp code/python_dataviz/*.py $WEB_DIR/
cp -R code/python_dataviz/streamlit $WEB_DIR/