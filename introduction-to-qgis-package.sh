# Packaging script to download Introduction to QGIS presentations as PDF
# and upload them to the GitHub release
# Tested on MacOS only

OUTPUT_DIR=~/Downloads/

# Update the presentations and upload to releases
SLIDE_IDS=(
    "1Lw0NQlLQXUSW1Mf1rzy9pLb_m2wxSUHQDxF-vjPTBaU"
    "1YJfWrjSDeriYJMsA6bmVi4zZmzLmGOo5dm13Lr5JaiI"
    "1cB6sF_Lo3w2YKhhxSPZdKKaYVT2ID91Jcvf-E0P4MUk"
    "1hiVXo82VnRHrQBroxzrByYod8CeNvsB1iVwy6q62mz8"
    "1ybJvCXRFfB2yQfPS9VE_pjTRDjQbX_PRcutpo16ksYI"
)
SLIDE_NAMES=(
    "Introduction_to_QGIS_Introduction_and_Course_Overview.pdf"
    "Introduction_to_QGIS_Joins.pdf"
    "Introduction_to_QGIS_Data_Normalization.pdf"
    "Introduction_to_QGIS_Introduction_to_OpenStreetMap.pdf"
    "Introduction_to_QGIS_Gridded_Population_Datasets.pdf"
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
