OUTPUT_DIR=~/Downloads/
PACKAGE_DIR=~/Downloads/python_foundation
SOLUTIONS_DIR=~/Downloads/python_foundation_solutions
cp -R code/python_foundation/data $PACKAGE_DIR/data
mkdir -p $PACKAGE_DIR/images/python_foundation
mkdir -p $PACKAGE_DIR/data
mkdir -p $SOLUTIONS_DIR
cp -R images/python_foundation/* $PACKAGE_DIR/images/python_foundation/
rm -R $PACKAGE_DIR/data/.ipynb_checkpoints $PACKAGE_DIR/data/*/.ipynb_checkpoints
#rm $PACKAGE_DIR/10_*.ipynb
#jupyter-nbconvert --to notebook --inplace --execute --ExecutePreprocessor.timeout=120 $PACKAGE_DIR/*.ipynb
#rm -R $PACKAGE_DIR/output
jupyter-nbconvert --ClearOutputPreprocessor.enabled=True --inplace code/python_foundation/[0-9]*.ipynb
jupyter-nbconvert --to markdown  code/python_foundation/[0-9]*.ipynb --output-dir .
cp code/python_foundation/[0-9]*.ipynb $PACKAGE_DIR/
cp code/python_foundation/solutions/*.ipynb $SOLUTIONS_DIR/
