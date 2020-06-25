OUTPUT_DIR=~/Downloads/
PACKAGE_DIR=~/Downloads/python_foundation
SOLUTIONS_DIR=~/Downloads/python_foundation_solutions
cp -R code/python_foundation/data $PACKAGE_DIR/
mkdir -p $PACKAGE_DIR/images/python_foundation
cp -R images/python_foundation/package/* $PACKAGE_DIR/images/python_foundation/
rm -R $PACKAGE_DIR/data/.ipynb_checkpoints $PACKAGE_DIR/data/*/.ipynb_checkpoints
cp code/python_foundation/[0-9]*.ipynb $PACKAGE_DIR
rm $PACKAGE_DIR/10_*.ipynb
#jupyter-nbconvert --to notebook --inplace --execute --ExecutePreprocessor.timeout=120 $PACKAGE_DIR/*.ipynb
#rm -R $PACKAGE_DIR/output
cp code/python_foundation/[0-9]*.ipynb $PACKAGE_DIR
jupyter-nbconvert --ClearOutputPreprocessor.enabled=True --inplace $PACKAGE_DIR/*.ipynb
cp code/python_foundation/solutions/*.ipynb $SOLUTIONS_DIR
