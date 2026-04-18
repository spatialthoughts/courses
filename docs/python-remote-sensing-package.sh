# Packaging script to build python-remote-sensing course
# Should be run after changing any *.ipynb files
# Tested on MacOS only
OUTPUT_DIR=~/Downloads/
PACKAGE_DIR=~/Downloads/python_remote_sensing
SOLUTIONS_DIR=~/Downloads/python_remote_sensing_solutions
WEB_DIR=~/projects/python-remote-sensing-web

#mkdir -p $SOLUTIONS_DIR

# Clear previously generated output
rm -rf python-remote-sensing-output

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

# matplotlib figures end up with a title 'png' or 'svg'.
# Also rewrite local *_files links so they are correct when included as child docs.
for md in python-remote-sensing-output/**/*.md python-remote-sensing-output/*.md; do
    [ -f "$md" ] || continue
    rel=$(dirname "${md#python-remote-sensing-output/}")
    if [ "$rel" = "." ]; then
        prefix="python-remote-sensing-output"
    else
        prefix="python-remote-sensing-output/${rel}"
    fi

    sed -i '' 's/\[png\]/\[\]/g' "$md"
    sed -i '' 's/\[svg\]/\[\]/g' "$md"
    # Rewrite only local links such as (01_xarray_basics_files/...) and keep external URLs untouched.
    sed -i '' -E "s#\(([^()/]+_files/)#(${prefix}/\1#g" "$md"
done
#cp -R code/python_remote_sensing/solutions/* $SOLUTIONS_DIR/

# Update python-remote-sensing-web repository
#cp code/python_remote_sensing/*.ipynb $WEB_DIR/
#cp code/python_remote_sensing/*.py $WEB_DIR/
#cp -R code/python_remote_sensing/streamlit $WEB_DIR/