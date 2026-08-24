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

- Read the unprocessed notes in the `raw/` folder. Look at all files inside the `raw/` folder.
- Process each document and all notes inside using the processing instructions below. 
- Once processed, move it to the `processed/` folder.
- Add an empty file `New_Notes.md` in the `raw/` file to collect new notes.


## Processing Instructions

When the user adds a new note to `raw/` and asks you to ingest it

* Read the New_Notes.md and process all notes from it.
	* If the note has one or more URLs,  visit them and generate an accurate short description.
	* For notes with text upto 100 characters, add it verbatim. For longer notes, summarize it up to 100 characters.
* Read any other files added to the `raw/` folder and process each file as a separate note.
* Identify the core concepts/topic of the resource. 
* Identify the main topic and related topics.
* Read `notes/index.md` first to find relevant topic pages.
* If there is no match, a new topic page can be added. See the list of topics below for additional topics of interest.
* Add a new item to the main topic page. Keeping the newer notes at the top.
* Add back-links ([[page-name]]) to connect related topics. If the related topic page does not exist, create the page.
* Update `notes/index.md` with new pages and one-line descriptions.
* Append an entry to `notes/log.md` with the date, source name, and what changed

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

## Note Formatting Instructions

- Use Markdown format for each note.
- Use a bullet point for each note.
- For notes with URLs: 
      - Follow the format [title](url]): <description> <keywords>
      - Add a 1-2 line description from the URLs
- For notes with just text:
      - Follow the format *Title*: <description> <keywords>
      - For notes with text upto 100 characters, add it verbatim. For longer notes, summarize it up to 100 characters.
- Add 3-6 keywords that best describe the note and will aid in recalling them later.
- Link to related topics using [[wiki-links]] throughout the text.

## Rules

- Keep page names Title Case with underscores (e.g. `Machine_Learning.md`).
- Write in clear, plain language.
- Always update the `log.md` after changes.