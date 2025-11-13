# XML to JSON Parser

A Python script that parses XML research papers (Elsevier/NLP XML format) and converts them to structured JSON files.

## Requirements

- Python 3.x
- Built-in libraries: `os`, `json`, `xml.etree.ElementTree`, `re`

## Usage

1. Place your XML files in the `xml_files/` folder
2. Run the script:
   ```bash
   python3 parser.py
   ```
3. Find your JSON outputs in the `json_output/` folder

## Configuration

Edit the constants at the top of `parser.py`:
- `INPUT_FOLDER`: Folder containing XML files (default: `./xml_files`)
- `OUTPUT_FOLDER`: Folder for JSON outputs (default: `./json_output`)
- `MIN_WORD_COUNT`: Minimum word count to keep a paper (default: `50`)

## Output Format

Each JSON file contains:
- `title`: Paper title
- `abstract`: Abstract text
- `body`: Full body text
- `citations`: List of citation references
- `references`: List of full reference texts
- `datasets`: List of DOI identifiers
- `authors`: List of author names
- `publication date`: Publication date
- `keywords`: List of keywords
- `institution`: Institution/affiliation

