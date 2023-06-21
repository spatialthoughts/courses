OUTPUT_DIR=~/Downloads/
PACKAGE_DIR=~/Downloads/python_foundation
SOLUTIONS_DIR=~/Downloads/python_foundation_solutions
WEB_DIR=~/projects/python-foundation-web


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
jupyter-nbconvert --to markdown  code/python_foundation/assignment.ipynb --output-dir python-foundation-output/

cp code/python_foundation/*.ipynb $PACKAGE_DIR/
cp code/python_foundation/solutions/*.ipynb $SOLUTIONS_DIR/


# Update python-foundation-web repository
cp code/python_foundation/*.ipynb $WEB_DIR/
cp code/python_foundation/*.py $WEB_DIR/