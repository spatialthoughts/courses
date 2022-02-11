OUTPUT_DIR=~/Downloads/
PACKAGE_DIR=~/Downloads/python_foundation
SOLUTIONS_DIR=~/Downloads/python_foundation_solutions
mkdir -p $PACKAGE_DIR/images/python_foundation
mkdir -p $PACKAGE_DIR/data
mkdir -p $PACKAGE_DIR/output
mkdir -p $SOLUTIONS_DIR
cp -R images/python_foundation/* $PACKAGE_DIR/images/python_foundation/
cp -R code/python_foundation/data/* $PACKAGE_DIR/data
rm -R $PACKAGE_DIR/data/.ipynb_checkpoints $PACKAGE_DIR/data/*/.ipynb_checkpoints
# Clear output from cells before packaging
jupyter-nbconvert --ClearOutputPreprocessor.enabled=True --inplace code/python_foundation/[0-9]*.ipynb
jupyter-nbconvert --to markdown  code/python_foundation/[0-9]*.ipynb --output-dir python-foundation-output/
# To ensure plots are generated, we run the plotting notebook using --execute
jupyter-nbconvert --to markdown  code/python_foundation/supplement1_plotting.ipynb --output-dir python-foundation-output/ --execute
jupyter-nbconvert --to markdown  code/python_foundation/supplement2_working_with_xarray.ipynb --output-dir python-foundation-output/ --execute
# matplotlib figures end up with a title 'png'. Remove it with sed
sed -i '' 's/\[png\]/\[\]/g' python-foundation-output/*.md
# image paths need to be set relative to the folder. Replace it with sed
sed -i '' -E 's/\((.+_files)/\(python-foundation-output\/\1/g' python-foundation-output/*.md
cp code/python_foundation/*.ipynb $PACKAGE_DIR/
cp code/python_foundation/solutions/*.ipynb $SOLUTIONS_DIR/
