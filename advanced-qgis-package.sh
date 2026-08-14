# Packaging script to download Advanced QGIS presentations as PDF
# and upload them to the GitHub release
# Tested on MacOS only

OUTPUT_DIR=~/Downloads/

# Update the presentations and upload to releases
SLIDE_IDS=(
    "13R-RbR5LJmBr5F-VAN0OXh7fRxRC8olFIl2yrOFgG-w"
    "1Vej8xgY710C-dsxneVXO_6UkXNkcIrYukzgJqxI2j3k"
    "1K1lR1JfonxGbmj8rCIVln_WkbWv6-tOYTYHAEJKAiw4"
    "1F-gH729oWv4zcCecXd9BYoNdqHr7KaahgMPm_4XCgBY"
    "1T02HeNaCHdWD7TuDdy1IrcYycVshd4kDik1WR_11-58"
)
SLIDE_NAMES=(
    "Advanced_QGIS_Introduction_and_Course_Overview.pdf"
    "Advanced_QGIS_Processing_Framework.pdf"
    "Advanced_QGIS_Spatial_Indexing.pdf"
    "Advanced_QGIS_Summary_Aggregate_Expressions.pdf"
    "Advanced_QGIS_Useful_Plugins.pdf"
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
