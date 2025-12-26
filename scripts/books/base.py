import os
import sys
from textwrap import dedent
import time

class BaseBook:
    pagebreak_lua = os.path.join("scripts", "pagebreak.lua")
    mytemplate_tex = os.path.join("scripts", "my-template.tex")

    def __init__(self, name,
    ):
        self.name = name
        self.metadata = os.path.join("external", name, "meta.yaml")
        self.book_md = os.path.join("output", name, f"{name}.md")
        self.book_epub_md = os.path.join("output", name, f"{name}-epub.md")
        self.book_paperback_pdf = os.path.join("output", name, f"{name}-paperback.pdf")
        self.book_pdf = os.path.join("output", name, f"{name}.pdf")
        self.book_epub = os.path.join("output", name, f"{name}.epub")
        self.book_docx = os.path.join("output", name, f"{name}.docx")
        self.cover_tex = os.path.join("output", name, "cover.tex")
        self.downloads_dir = os.path.join("docs", name, "downloads")
    
    def get_chapters(self, format=None):
        raise NotImplementedError()
    
    def get_epub_markdown_content(self):
        content = self.get_md_content(format="epub")
        return content

    def get_copyright_md(self, format):
        if format == "epub":
            return os.path.join(self.base_dir, "copyright-epub.md")
        return os.path.join(self.base_dir, "copyright.md")
  
    def get_cover_image(self):
        return os.path.join(self.base_dir, "artwork", "cover.png")

    def create_md(self):
        filename = self.book_md
        print(f"Creating {filename}")
        content = self.get_md_content()
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8", errors="ignore") as f:
            f.write(content)

    def get_md_content(self, format=None):
        files = self.get_chapters(format)
        content = ""
        for file in files:
            with open(file, encoding="utf-8", errors="ignore") as f:
                content += f.read()
                content += "\n::: pagebreak\n:::\n\n"
        content = content.replace("<!-- PAGEBREAK -->", "\n::: pagebreak\n:::\n")
        content = content.strip()
        return content

    def create_epub(self):
        epub_markdown = self.get_epub_markdown_content()
        if epub_markdown:
            with open(self.book_epub_md, "w", encoding="utf-8", errors="ignore") as f:
                f.write(epub_markdown)
            book_md = self.book_epub_md
        else:
            book_md = self.book_md

        # Do not include cover for now
        cover_image = ""  # self.get_cover_image()
        cover_option = f"--epub-cover-image={cover_image} " if cover_image else ""

        print(f"Creating {self.book_epub}")
        os.makedirs(os.path.dirname(self.book_epub), exist_ok=True)
        exit_code = os.system(
            f"pandoc {book_md} -o {self.book_epub} --metadata-file={self.metadata} {cover_option} --lua-filter={self.pagebreak_lua}"
        )
        if exit_code != 0:
            print("Failed to generate epub")
            sys.exit(1)

    def create_docx(self):
        filename = self.book_docx
        print(f"Creating {filename}")

        # Ensure Pandoc does not auto-generate a table of contents for DOCX output
        # Some Pandoc versions add a TOC when styles or templates request it; explicitly set toc=false
        exit_code = os.system(
            f"pandoc {self.book_md} -o {filename} --metadata-file={self.metadata} --metadata=toc:false --lua-filter={self.pagebreak_lua} --to=docx"
        )
        if exit_code != 0:
            print("Failed to generate docx")
            sys.exit(1)

    def create_pdf(self):
        cover_tex_content = self.get_cover_tex_content()
        if cover_tex_content:
            with open(self.cover_tex, "w", encoding="utf-8", errors="ignore") as f:
                f.write(cover_tex_content)
            cover_option = f"--include-before-body={self.cover_tex} "
        else:
            cover_option = ""

        print(f"Creating {self.book_pdf}")
        os.makedirs(os.path.dirname(self.book_pdf), exist_ok=True)
        exit_code = os.system(
            f"pandoc {self.book_md} -o {self.book_pdf} --pdf-engine=xelatex --metadata-file={self.metadata} --template={self.mytemplate_tex} --lua-filter={self.pagebreak_lua} {cover_option}"
        )
        if exit_code != 0:
            print("Failed to generate pdf")

    def create_paperback_pdf(self):
        print(f"Creating {self.book_paperback_pdf}")
        os.makedirs(os.path.dirname(self.book_paperback_pdf), exist_ok=True)
        metadata_file = self.create_paperback_metadata(self.metadata)
        exit_code = os.system(
            f"pandoc {self.book_md} -o {self.book_paperback_pdf} --pdf-engine=xelatex --metadata-file={metadata_file} --metadata=toc:false --template={self.mytemplate_tex} --lua-filter={self.pagebreak_lua} --variable=paper-size:a5 --variable=margin-left:0.75in --variable=margin-right:0.75in --variable=margin-top:1in --variable=margin-bottom:1in"
        )
        if exit_code != 0:
            print("Failed to generate paperback pdf")
        if os.path.exists(metadata_file):
            os.remove(metadata_file)

    def create_paperback_metadata(self, original_metadata):
        paperback_metadata = original_metadata.replace(".yaml", "-paperback.yaml")
        with open(original_metadata, "r", encoding="utf-8", errors="ignore") as f:
            with open(paperback_metadata, "w", encoding="utf-8", errors="ignore") as fout:
                fout.write(f.read().replace("oneside", "twoside"))
        return paperback_metadata

    def get_cover_tex_content(self):
        cover_image = self.get_cover_image().replace("\\", "/")
        if not cover_image:
            return ""
        return dedent(r"""
            \begin{titlepage}
            \thispagestyle{empty}
            \begin{tikzpicture}[remember picture,overlay]
                % Clip to the physical page
                \clip (current page.south west) rectangle (current page.north east);
                % Place image centered; pick the larger of width/height to ensure full coverage
                \node[anchor=center] at (current page.center)
                {\includegraphics[height=\paperheight]{""" + cover_image + r"""}}; % try height first
                % If you still see side gaps (very tall/narrow image), switch to width:
                % {\includegraphics[width=\paperwidth]{""" + cover_image + r"""}};
            \end{tikzpicture}
            \null % ensure the page is shipped out
            \end{titlepage}
            \clearpage
            """
        )

    def copy_downloads(self):
        dest_pdf = os.path.join(self.downloads_dir, os.path.basename(self.book_pdf))
        dest_epub = os.path.join(self.downloads_dir, os.path.basename(self.book_epub))
        dest_md = os.path.join(self.downloads_dir, os.path.basename(self.book_md))
        dest_docx = os.path.join(self.downloads_dir, os.path.basename(self.book_docx))
        dest_cover_image = os.path.join(self.downloads_dir, "cover" + os.path.splitext(self.get_cover_image())[1])

        os.makedirs(self.downloads_dir, exist_ok=True)
        if os.path.exists(self.book_pdf):
            os.system(f'copy /y "{self.book_pdf}" "{dest_pdf}"')
        if os.path.exists(self.book_epub):
            os.system(f'copy /y "{self.book_epub}" "{dest_epub}"')
        if os.path.exists(self.book_md):
            os.system(f'copy /y "{self.book_md}" "{dest_md}"')
        if os.path.exists(self.book_docx):
            os.system(f'copy /y "{self.book_docx}" "{dest_docx}"')
        cover_image = self.get_cover_image()
        if os.path.exists(cover_image):
            os.system(f'copy /y "{cover_image}" "{dest_cover_image}"')

        print(f"Copied downloads to {self.downloads_dir}")

    def publish(self):
        print(f"Publishing {self.name}")
        
        assets = [
            self.book_pdf,
            self.book_epub,
            self.book_md,
            self.book_docx,
            self.get_cover_image(),
        ]

        # Make sure all assets exist
        for asset in assets:
            if not os.path.exists(asset):
                print(f"Missing asset: {asset}")
                sys.exit(1)

        # Make sure GitHub CLI is authenticated
        exit_code = os.system("gh auth status -h github.com >NUL")
        if exit_code != 0:
            print("GitHub CLI not authenticated. Run 'gh auth login'")
            sys.exit(1)
        
        tag = "v" + time.strftime("%Y.%m.%d")
        repo = self.name

        # Check if release already exists
        release_exists = os.system(f'gh release view {tag} -R wisdomwater/{repo} >NUL 2>&1') == 0
        if not release_exists:
            print(f"Creating release {tag}")
            exit_code = os.system(f'gh release create {tag} -R wisdomwater/{repo} -t "{self.name} {tag}" -n "Automated release of {self.name}."')
            if exit_code != 0:
                print("Failed to create release")
                sys.exit(1)
        else:
            print(f"Release {tag} already exists, updating assets")

        # Upload assets to tagged release
        asset_list = " ".join(f'"{asset}"' for asset in assets)
        print(f"Uploading assets to release {tag}")
        exit_code = os.system(f'gh release upload {tag} {asset_list} -R wisdomwater/{repo} --clobber')
        if exit_code != 0:
            print(f"Failed to upload assets")
            sys.exit(1)

        # Check if latest tag already exists
        tag = "latest"
        release_exists = os.system(f'gh release view {tag} -R wisdomwater/{repo} >NUL 2>&1') == 0
        if not release_exists:
            print(f"Creating release {tag}")
            exit_code = os.system(f'gh release create {tag} -R wisdomwater/{repo} -t "{self.name} {tag}" -n "Automated release of {self.name}."')
            if exit_code != 0:
                print("Failed to create release")
                sys.exit(1)
        else:
            print(f"Release {tag} already exists, updating assets")

        # Upload assets to latest release
        print(f"Uploading assets to latest release")
        exit_code = os.system(f'gh release upload latest {asset_list} -R wisdomwater/{repo} --clobber')
        if exit_code != 0:
            print(f"Failed to upload assets to latest release")
            sys.exit(1)

        print("Published successfully")
