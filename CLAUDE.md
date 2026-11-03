# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Source for the Spatial Thoughts OpenCourseWare site (courses.spatialthoughts.com): an R Markdown website (`_site.yml`) served from `docs/` via GitHub Pages.

- Root `*.Rmd`: one page per course/install guide.
- `code/<course_name>/`: notebooks, scripts and data for each course.
- `images/<course>/`: tutorial images.

## Generated files - do not hand-edit

- `docs/`: site build output (also contains copies of `code/` and `images/`). Edit the sources, then rebuild.
- `<course>-output/` (e.g. `python-remote-sensing-output/`): Markdown generated from notebooks by `jupyter nbconvert` and pulled into the Rmd as child docs. Edit the `.ipynb` in `code/<course>/` instead; the package script deletes and regenerates this folder.

## Build

- Build the site: `Rscript -e 'rmarkdown::render_site()'`. Render one page: `Rscript -e "rmarkdown::render_site('page.Rmd')"`.
- `<course>-package.sh` scripts regenerate `<course>-output/` but also zip into `~/Downloads`, copy into sibling repos under `~/projects`, and (with `--update-release`) upload to GitHub releases. Always ask before running one.
- Lint Python/notebooks: `conda run -n ruff ruff check code/<course>`. PyQGIS course folders (`pyqgis`, `qgis_actions`, `qgis_plugin_workshop`, `advanced_qgis`) are excluded in `ruff.toml` (they rely on QGIS console globals like `iface`).
- `python-remote-sensing-package.sh` requires zsh (`**` globbing); other scripts are bash. Scripts use macOS `sed -i ''`.

## Notebooks

- Numeric-prefix names (`01_xarray_basics.ipynb`); each module has `assignmentN.ipynb`.
- Keep the standard Setup cell pattern: detect Colab via `COLAB_RELEASE_TAG`, `%%capture` + `!pip install` only on Colab, `data_folder = 'data'`, `output_folder = 'output'` (both gitignored).
- Outputs: R Markdown does not render DataFrames or rich HTML outputs well, so keep useful image outputs and clear the rest. Don't blanket-clear or blanket-keep outputs.
- Each course has its own conda env; ask which one to use. The root `environment.yml` is stale.

## Writing style (Rmd course pages)

- Formatting (see the style guide in `README.md`):
  - UI labels (windows, tabs, dialogs, buttons) and keyboard keys: `*label*`
  - Menus and Processing algorithms: `**Menu &rarr; Submenu**` (use `&rarr;`)
  - Values the learner enters or selects: `**value**`
  - Layer and file names: backticks
  - External links: `[text](url){target="_blank"}`
  - Callouts: `> Note:`, `> Tip:`, `> Warning:`
- Voice: simple, action-oriented, learner-centric ("We will now learn...", "Next, open this notebook.").
- Hands-on steps are a numbered list. Each step = the action, what the learner will see, and a short explanation of why. Document warnings and confirmation dialogs and what to click.
- GUI walkthroughs (QGIS, install guides, web consoles): one screenshot after every step. The text must precisely reproduce what the screenshot shows (every field, option and button set).
- Never add a step without a screenshot. Merge it into the neighbouring step that has one. If it truly needs its own step, flag it for manual review in your reply instead of adding it.
- Link official docs when introducing a a specific concept, option or function. Point to the exact section or function reference. Examples:
  - "The default mode of classification is Quantile... There are other modes of classification as well. You can learn more about Data Classification Modes in the [QGIS Documentation](https://docs.qgis.org/testing/en/docs/user_manual/working_with_vector/vector_properties.html?#graduated-renderer){target="_blank"}."
  - "Let's filter noise and small patches from the result using the [xrspatial.sieve.sieve()](https://xarray-spatial.readthedocs.io/en/stable/reference/_autosummary/xrspatial.sieve.sieve.html){target="_blank"} function."
- Agentic coding steps: agent output varies between runs. Describe what Claude Code does in general terms ("Claude Code will propose a workflow"). When describing a specific result from the screenshots, use past tense ("In this instance it decided to..."). Don't walk through the contents of plans or summaries.
- Frame refinement prompts as a reusable technique: "If you want to change X, do Y. For example, ..." followed by the prompt.
- Include only what the learner needs to act or understand. Leave out incidental details and commentary. (unused layers, output file locations, styling).
