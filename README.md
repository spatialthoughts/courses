# Spatial Thoughts OpenCourseWare

This repository powers the content at [courses.spatialthoughts.com](https://courses.spatialthoughts.com/)

The html pages are built using R Studio as a [R Markdown Website](https://rmarkdown.rstudio.com/lesson-13.html).

The content has the following course pages

* Spatial Data Visualization and Analytics
* Advanced QGIS
* Python Foundation for Spatial Analysis
* Customizing QGIS with Python
* Mastering GDAL Tools
* End-to-End Google Earth Engine
* Automating GIS Workflows with QGIS

## Updating the content

Most courses are written using pure MarkDown in the corresponding `.Rmd` file. You can update the content directly. A few courses embed other `.md` files generated from Jupyter Notebooks - which need to be generated before building the site.

### Python Foundation for Spatial Analysis

1. Update the `.ipynb` files in the `code/python_foundation/` directory.
2. Run `python-foundation-package.sh` to generate `.md` files for each notebook

### End-to-End Google Earth Engine

The code for the course comes from a Google Earth Engine repository `users/ujavalgandhi/End-to-End-GEE`. 

1. Clone the `users/ujavalgandhi/End-to-End-GEE` repository to `~/projects` directory.
2. Update the `.ipynb` files in the `code/end_to_end_gee/` directory.
3. Run `end-to-end-gee-package.sh` to generate `.md` files from the updated code and notebooks.

### Formatting Guide

We prefer the following style while writing the tutorials.

| Type                                        | rmd Formatting  |
| ------------------------------------------- | --------------- |
| Title                                       |``` # ```|
| Heading 1                                   | ```##``` |
| Heading 2                                   | ```###``` |
| Window titles, Tabs, Dialogs and buttons    | ```*label*``` |
| Menu items                                  | ``` ** menu &arr; submenu1 &rarr; submenu2 ** ``` |
| Processing algorithms                       | ``` ** Processing Toolbox &arr; Vector Overlay &rarr; Clip** ``` |
| Layer and file names                        | ``` **layer_name** ``` |
| Text input by the user / keyboard shortcuts | ``` **value** ```| 
| Hyper Link's                                | ``` [Spatial Thoughts](https:spatialthoughts.com) ```|
