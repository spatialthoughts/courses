#!/bin/bash
# Use --update-release to also upload the data package and presentations to the GitHub releases
UPDATE_RELEASE=false
for arg in "$@"; do
    if [ "$arg" = "--update-release" ]; then
        UPDATE_RELEASE=true
    fi
done

OUTPUT_DIR=~/Downloads/
PACKAGE_DIR=~/Downloads/python_foundation
WEB_DIR=~/projects/python-foundation-web


# Start from a clean package folder so stale files don't end up in the zip
rm -rf $PACKAGE_DIR
mkdir -p $PACKAGE_DIR/images/python_foundation
mkdir -p $PACKAGE_DIR/data
mkdir -p $PACKAGE_DIR/output
cp -R images/python_foundation/* $PACKAGE_DIR/images/python_foundation/
cp -R code/python_foundation/data/* $PACKAGE_DIR/data
rm -R $PACKAGE_DIR/data/.ipynb_checkpoints $PACKAGE_DIR/data/*/.ipynb_checkpoints
# Clear output from cells before packaging
jupyter-nbconvert --ClearOutputPreprocessor.enabled=True --inplace code/python_foundation/[0-9]*.ipynb
jupyter-nbconvert --to markdown  code/python_foundation/[0-9]*.ipynb --output-dir python-foundation-output/
jupyter-nbconvert --to markdown  code/python_foundation/assignment.ipynb --output-dir python-foundation-output/
jupyter-nbconvert --to markdown  code/python_foundation/common_errors.ipynb --output-dir python-foundation-output/
cp code/python_foundation/*.ipynb $PACKAGE_DIR/

# Create the data package zip, replacing any existing one
ZIP_FILE=${OUTPUT_DIR}python_foundation.zip
rm -f $ZIP_FILE
(cd $OUTPUT_DIR && zip -rq python_foundation.zip python_foundation -x '*.DS_Store' '*.ipynb_checkpoints*')


# Update python-foundation-web repository
cp code/python_foundation/*.ipynb $WEB_DIR/
cp code/python_foundation/*.py $WEB_DIR/


if [ "$UPDATE_RELEASE" = true ]; then
    # Upload the data package to the 'data' release
    gh release delete-asset data python_foundation.zip --repo spatialthoughts/courses --yes 2>/dev/null
    gh release upload data $ZIP_FILE --repo spatialthoughts/courses

    # Update the presentations and upload to releases
    SLIDE_IDS=(
        "125LV0qR47S_OGaZZr5Zv-7lbWfdZ5pNo3iFm6IOX7uI"
        "1fFCOHSEPnGamcymzTZGE3Sc9lMJGo4tQ063leEyZMU8"
        "1fyNe15yhbMq_435yaHRZefKzos4Vpyf54mqNfhC_flQ"
        "1nBvuv9-Qa90RmNCOyLxl0kj9sBIs4QQ3O7ytZccu-Y4"
    )
    SLIDE_NAMES=(
        "Python_Foundation_for_Spatial_Analysis_Introduction_and_Course_Overview.pdf"
        "Python_Foundation_for_Spatial_Analysis_Coordinate_Systems.pdf"
        "Python_Foundation_for_Spatial_Analysis_Pandas_GeoPandas.pdf"
        "Python_Foundation_for_Spatial_Analysis_NumPy_XArray.pdf"
    )

    FILES=()
    for i in "${!SLIDE_IDS[@]}"; do
        id="${SLIDE_IDS[$i]}"
        name="${SLIDE_NAMES[$i]}"
        out="${OUTPUT_DIR}${name}"
        wget -O "$out" "https://docs.google.com/presentation/d/${id}/export/pdf"
        FILES+=("$out")
    done

    # --clobber can 404 on a stale asset id, so delete each asset by name first instead.
    for i in "${!SLIDE_NAMES[@]}"; do
        name="${SLIDE_NAMES[$i]}"
        gh release delete-asset presentations "$name" --repo spatialthoughts/courses --yes 2>/dev/null
        gh release upload presentations "${FILES[$i]}" --repo spatialthoughts/courses
    done
fi
