## Overview

A personal notes organizer maintained by Claude Code.

## Folder structure
   
```
- raw/ -- documents containing unprocessed notes
- processed/ -- documents containing processed notes
- notes/ -- markdown pages for the organized notes pages
- notes/index.md -- table of contents of all the notes pages
- notes/log.md -- append-only record of all operations
```

## Workflow

- Read the unprocessed notes in the `raw/` folder.
- Process each document and all notes inside using the processing instructions below.
- Once processed, move it to the `processed/` folder.
- Add an empty file `New_Notes.md` in the `raw/` file to collect new notes.


## Processing Instructions

When the user adds a new note to `raw/` and asks you to ingest it

* If the note has one or more URLs,  visit them and generate an accurate short description.
* Identify the core concepts/topic of the resource. 
* Identify the main topic and related topics.
* Read `notes/index.md` first to find relevant topic pages.
* If there is no match, a new topic page can be added. See the list of topics below for additional topics of interest.
* Add a new item to the main topic page. Keeping the newer notes at the top.
* Add back-links ([[page-name]]) to connect related topics. If the related topic page does not exist, create the page.
* Update `notes/index.md` with new pages and one-line descriptions.
* Append an entry to `notes/log.md` with the date, source name, and what changed

## Update the Website

This vault is published as a MkDocs site on GitHub Pages (https://spatialthoughts.github.io/personal-notes/, repo https://github.com/spatialthoughts/personal-notes). After ingesting new notes:

* Update the "Latest Finds" section in `notes/index.md` with the 3 most recently added notes, each from a different topic page.
* Commit and push the changes to GitHub (`git add`, `git commit`, `git push`) so the site's GitHub Actions workflow rebuilds and redeploys automatically. `processed/` stays gitignored and is never pushed.

## List of Topics

Here are some of the topics for the notes you may find. The topics can be Technology focused (i.e. Python, Xarray) or Theme focused (Climate Change, Agriculture). When deciding the main topic when a note covers both - use the theme focused topic as the primary topic.

Technology Topics
* Machine Learning
* Embeddings
* Deep Learning
* SQL
* Python
* Data
* Agentic Coding

Thematic Topics
* Climate Change
* Urban Planning
* Agriculture
* Remote Sensing
* Cartography

## Topic Page Format


Every note topic page should follow this structure:


```markdown
# Page Title


**Summary**: One to two sentences describing this page.
**Last updated**: Date of most recent update.

---


Main content goes here.
```

- Use Markdown format for each note.
- Use a bullet point for each note
- For notes with URLs, 
	  - Follow the format [title](url]): <description> <keywords>
	  - If there is text accompanying the URL, Add it verbatim. 
	  - Add a 1-2 line description from the URLs
- For notes with just text, 
	  - Follow the format *Title*: note text <keywords>
	  - Do not summarize notes with just text. Add it verbatim.
- Add 3-6 keywords that best describe the note and will aid in recalling them later.

Link to related topics using [[wiki-links]] throughout the text.



## Rules

- Keep page names Title Case with underscores (e.g. `Machine_Learning.md`).
- Write in clear, plain language.
- Always update the `log.md` after changes.
