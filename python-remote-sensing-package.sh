# Packaging script to build python-dataviz course
# Should be run after changing any *.ipynb files
# Tested on MacOS only
OUTPUT_DIR=~/Downloads/
PACKAGE_DIR=~/Downloads/python_remote_sensing
SOLUTIONS_DIR=~/Downloads/python_remote_sensing_solutions
WEB_DIR=~/projects/python-dataviz-web

#mkdir -p $SOLUTIONS_DIR

# Main Notebooks
for nb in code/python_remote_sensing/**/*.ipynb code/python_remote_sensing/*.ipynb; do
    rel=$(dirname "${nb#code/python_remote_sensing/}")
    if [ "$rel" = "." ]; then
        outdir="python-remote-sensing-output"
    else
        outdir="python-remote-sensing-output/${rel}"
    fi
    mkdir -p "$outdir"
    jupyter nbconvert --to markdown "$nb" --output-dir "$outdir"
done

# matplotlib figures end up with a title 'png'. Remove it with sed
# Fix root-level md files
sed -i '' 's/\[png\]/\[\]/g' python-remote-sensing-output/*.md
sed -i '' -E 's/\((.+_files)/\(python-remote-sensing-output\/\1/g' python-remote-sensing-output/*.md

# Fix md files in subdirectories
for md in python-remote-sensing-output/**/*.md; do
    rel=$(dirname "${md#python-remote-sensing-output/}")
    sed -i '' 's/\[png\]/\[\]/g' "$md"
    sed -i '' -E "s/\((.+_files)/\(python-remote-sensing-output\/${rel}\/\1/g" "$md"
done
#cp -R code/python_remote_sensing/solutions/* $SOLUTIONS_DIR/

# Update python-dataviz-web repository
#cp code/python_remote_sensing/*.ipynb $WEB_DIR/
#cp code/python_remote_sensing/*.py $WEB_DIR/
#cp -R code/python_remote_sensing/streamlit $WEB_DIR/