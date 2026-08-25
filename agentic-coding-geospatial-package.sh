# Packaging script to download Agentic Coding for Geospatial presentations as PDF
# and upload them to the GitHub release
# Tested on MacOS only

OUTPUT_DIR=~/Downloads/

# Update the presentations and upload to releases
SLIDE_IDS=(
    "1gQV_YIBTE_o8ziY0Oza-BX8BOmvATfPq6vHaC4_cNKI"
    "1iRaSLeWlBHvqVOyt5BSy2gkpDyhYlCQi-7P1XgN1p7M"
    "18zyVBK70rY-mv0tiZwKQqRO6pY1A4762HAYrJCVKCjk"
    "1qF0D-697kSUbosBGBZkNYfQ7sn4pxcvGI53OpWs9dGE"
    "1w2N_7FtX4v9nHJoX-se3rLw-KcbfKepEhr9b6Lk7wPI"
    "15vWZLJmcAAc_66IkVfVuh31NmpzwxhV7s33coDDM-B4"
)
SLIDE_NAMES=(
    "Agentic_Coding_for_Geospatial_Introduction.pdf"
    "Agentic_Coding_for_Geospatial_Introduction_to_Agentic_Coding.pdf"
    "Agentic_Coding_for_Geospatial_Using_Skills.pdf"
    "Agentic_Coding_for_Geospatial_Network_Analysis_and_Route_Optimization.pdf"
    "Agentic_Coding_for_Geospatial_Personal_Knowledge_Base.pdf"
    "Agentic_Coding_for_Geospatial_GeoAI_Basics.pdf"
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
