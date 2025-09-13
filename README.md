# Wisdom Water Website

This repository contains the automation scripts and layout for the **Wisdom Water** website. It is used to maintain and publish book assets, including PDF, EPUB, and Markdown versions of texts.

## Features

- Automated build scripts for generating book formats (PDF, EPUB, Markdown)
- Custom Pandoc templates and filters for advanced formatting
- Organized content structure for chapters, metadata, and assets
- Support for cover images and page breaks in output formats
- Easy management of downloadable book files

## Directory Structure

```
.
├── docs/                # Website content and downloads
├── external/            # Source book content and metadata
├── output/              # Generated book files
├── scripts/             # Automation scripts and templates
│   ├── books/           # Python build scripts
│   ├── my-template.tex  # Custom LaTeX template
│   └── pagebreak.lua    # Pandoc Lua filter for page breaks
├── do.cmd               # Automation script front-end
├── mkdocs.yml           # Mkdocs config file
└── README.md
```

## Usage

1. **Install dependencies:**  
   - [Python 3.x](https://www.python.org/)
   - [Pandoc](https://pandoc.org/)

2. **Run environment setup script:**  
   Open a command prompt and run the `setup` command to set up the build environment.
   ```
   do setup
   ```

3. **Compile book sources:**  
   Run the `compile` command to create book assets.
   ```
   do compile <book>
   ```

4. **Publish book release:**  
   Run the `publish` command to publish a book release.
   ```
   do publish <book>
   ```

## Creating a new book

1. **Add the git submodule:**
   ```
   git submodule add <repo-url> external/<repo-name>
   ```

2. **Create new docs folder:**
   Follow the example of an existing folder and create a new `docs/<repo-name>` folder.

3. **Update docs/index:**
   Add a new entry for the book in `docs/index.md`.

4. **Update nav:**
   Add a new entry for the book to `mkdocs.yml`.

5. **Create book script:**
   Follow the example of an existing file and create a new `scripts/book/<repo-name>.py` file.

6. **Update scripts/do.py:**
   Add a new entry to `BOOK` dictionary in `scripts/do.py`.

7. **Create meta.yaml:**
   Copy and edit existing `external/<book>/meta.yaml` file.


8. **Compile the book:**
   ```
   do compile <book>
   ```

9. **Publish the book artifacts:**
   ```
   do publish <book>
   ```

10. **Merge main site changes:**
   Git push all the changes. This will trigger a rebuilding of the Git Pages site.

11. **Serve http://localhost:8000**
   ```
   do -- mkdocs serve
   ```

## Contributing

Feel free to submit issues or pull requests to improve the automation or content structure.

## License

This repository is maintained by Michael Collins for the Wisdom Water project. See the [LICENSE](LICENSE) for details.