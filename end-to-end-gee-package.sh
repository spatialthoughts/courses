# rm -R code/end_to_end_gee
# mkdir code/end_to_end_gee
cp -R ~/projects/End-to-End-GEE/01-Earth-Engine-Basics code/end_to_end_gee/
cp -R ~/projects/End-to-End-GEE/02-Earth-Engine-Intermediate code/end_to_end_gee/
cp -R ~/projects/End-to-End-GEE/03-Supervised-Classification code/end_to_end_gee/
cp -R ~/projects/End-to-End-GEE/04-Earth-Engine-Advanced code/end_to_end_gee/
cp -R ~/projects/End-to-End-GEE/Supplement code/end_to_end_gee/
# Python notebooks
# Clear output from cells before packaging
jupyter-nbconvert --ClearOutputPreprocessor.enabled=True --inplace code/end_to_end_gee/*.ipynb
jupyter-nbconvert --to markdown  code/end_to_end_gee/*.ipynb --output-dir .

