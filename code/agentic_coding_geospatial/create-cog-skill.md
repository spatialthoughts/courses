---
name: create-cog
description: Convert a raster to a Cloud-Optimized GeoTIFF (COG)
---

Use this skill when you need to convert any geospatial raster data to a
Cloud-Optimized GeoTIFF.

## Workflow

1. Activate the conda environment that has GDAL. Never use the base environment.
2. Check the GDAL version, since the conversion command differs by version.
3. Check if the input is already a valid COG. If it is, stop and report
   that. Do not re-convert.
4. Convert, using the compression settings and naming convention below.
5. Validate the output and report the result.

## Required Tools

* `gdal` Conda package. Install using `conda install -c conda-forge gdal`
* `rio-cogeo` Python package for validation. Install using `pip install
  rio-cogeo`

Both must come from a conda environment, not base. Check what is available
before installing:

    conda env list
    conda activate <env>
    gdal --version

If neither is installed, ask the user which environment to install into
before proceeding.

## Validating COGs

    rio cogeo validate <file>

Always validate the input before converting and the output after converting.

## Converting Raster to a COG

Check `gdal --version` first, then use the matching command.

GDAL version >= 3.11 (the `gdal` subcommand interface)

    gdal raster convert -f COG <input file> <output file>

GDAL version < 3.11 (the legacy utility)

    gdal_translate -of COG <input file> <output file>

Note the flag difference. The new `gdal raster convert` takes `-f` (or
`--format`). It does NOT accept `-of`, which is the legacy `gdal_translate`
flag, and fails with "Option 'o' is not a boolean option."

Creation options are passed with `--co KEY=VALUE` on the new interface,
`-co KEY=VALUE` on the legacy one.

If the output file already exists, the command errors out. Add
`--overwrite` only when you intend to replace it.

## Compression

The COG driver already applies LZW compression by default, so the output is
compressed even if you pass nothing. But the default uses no predictor,
which wastes a lot of space on continuous data. Set the compression and
predictor explicitly. Use DEFLATE as the default, since it is readable by
every GeoTIFF client.

    gdal raster convert -f COG --co COMPRESS=DEFLATE --co PREDICTOR=YES <input> <output>

Only exception - If the input data is JPEG compressed - typically used in
aerial/drone imagery), retain the same with COMPRESS=JPEG

## File Naming Convention

Append the text `_cog` to the converted filename. If the input is
`data.tif`, the output should be named `data_cog.tif`

## Remote Files

If the given file is a remote file, do not download it. Use GDAL Virtual
File Systems by prefixing the URL with `/vsicurl/`

    rio cogeo validate /vsicurl/https://example.com/data.tif
    gdal raster convert -f COG /vsicurl/https://example.com/data.tif data_cog.tif

A remote input gives no obvious output location. Write to the current
working directory unless a location is specified by the user.

In Windows Powershell, set the following environment variable `MSYS_NO_PATHCONV=1` 
to avoid errors when using paths starting with `/vsicurl`

