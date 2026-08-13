# Packaging script to build python-remote-sensing course
# Should be run after changing any *.ipynb files
# Tested on MacOS only
# Use --update-release to also upload the downloaded presentations to the GitHub release
UPDATE_RELEASE=false
for arg in "$@"; do
    if [ "$arg" = "--update-release" ]; then
        UPDATE_RELEASE=true
    fi
done

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

# Update spatialthoughts-ai-skills repository with the latest skill
SKILLS_REPO=~/projects/spatialthoughts-ai-skills
mkdir -p "$SKILLS_REPO/skills/cloud-native-remote-sensing"
cp code/python_remote_sensing/.claude/skills/cloud-native-remote-sensing/SKILL.md \
    "$SKILLS_REPO/skills/cloud-native-remote-sensing/SKILL.md"

if [ "$UPDATE_RELEASE" = true ]; then
    # Update the presentations and upload to releases
    SLIDE_IDS=(
        "1YhT8OdrOm0JkkoTJ-eyQC89V2q6QiFXpA_57QW6caec"
        "1FPQ4ZQVqTXW5hQ2FVZG9knwZNDnR3aUoeJvpUOoRC6Y"
        "1_LlMfxZ54QESEb0iKpclYWLqruzGXVW_d3w9q5epenA"
        "1rC3wh7hqZzWRmb5AP7hlteCJf3KbS5fL7csndGE7bNo"
        "1AHlQq75wm3G5H-KRDhnaAdjtfmVW1Gbm3tBQLCBx2Uk"
    )
    SLIDE_NAMES=(
        "Cloud_Native_Remote_Sensing_with_Python_Introduction_and_Course_Overview.pdf"
        "Cloud_Native_Remote_Sensing_with_Python_Cloud_Native_Geospatial_Basics.pdf"
        "Cloud_Native_Remote_Sensing_with_Python_Remote_Sensing_Fundamentals.pdf"
        "Cloud_Native_Remote_Sensing_with_Python_Computation_and_Data_Processing.pdf"
        "Cloud_Native_Remote_Sensing_with_Python_Machine_Learning_and_AI.pdf"
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

