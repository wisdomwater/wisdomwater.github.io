import os
import re
import subprocess
import sys
from textwrap import dedent
import time

class BaseBook:
    pagebreak_lua = os.path.join("scripts", "pagebreak.lua")
    mytemplate_tex = os.path.join("scripts", "my-template.tex")
    toc = False

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

    def get_extra_pandoc_options(self, format):
        return ""

    def get_copyright_md(self, format):
        if format in ("epub", "docx", "markdown"):
            return os.path.join(self.base_dir, "copyright-epub.md")
        return os.path.join(self.base_dir, "copyright.md")
  
    def get_cover_image(self):
        return os.path.join(self.base_dir, "artwork", "cover.png")

    def create_md(self):
        filename = self.book_md
        print(f"Creating {filename}")
        content = self.get_md_content(format="markdown")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8", errors="ignore") as f:
            f.write(content)

    def get_md_content(self, format=None):
        copyright_file = self.get_copyright_md(format)
        files = [file for file in self.get_chapters(format) if os.path.normpath(file) != os.path.normpath(copyright_file)]
        if format == "epub" and os.path.exists(copyright_file):
            files.insert(0, copyright_file)
        return self._get_md_content_from_files(files)

    def _get_md_content_from_files(self, files):
        content = ""
        for file in files:
            with open(file, encoding="utf-8", errors="ignore") as f:
                file_content = f.read().strip()
            if not file_content:
                continue
            if content:
                content += "\n\n"
            content += file_content
        content = content.replace("<!-- PAGEBREAK -->", "\n::: pagebreak\n:::\n")
        content = content.strip()
        return content

    def _run_pandoc(self, input_path, output_path, extra_args=None, metadata_file=None, template=None, pdf_engine=None):
        cmd = ["pandoc", str(input_path), "-o", str(output_path)]
        if metadata_file:
            cmd.append(f"--metadata-file={metadata_file}")
        if template:
            cmd.append(f"--template={template}")
        if pdf_engine:
            cmd.append(f"--pdf-engine={pdf_engine}")
        if self.pagebreak_lua:
            cmd.append(f"--lua-filter={self.pagebreak_lua}")
        if extra_args:
            cmd.extend(extra_args)
        print(f"Running: {' '.join(cmd)}")
        return subprocess.run(cmd, check=False).returncode

    def create_epub(self):
        epub_markdown = self.get_epub_markdown_content()
        if epub_markdown:
            with open(self.book_epub_md, "w", encoding="utf-8", errors="ignore") as f:
                f.write(epub_markdown)
            book_md = self.book_epub_md
        else:
            book_md = self.book_md

        metadata_file = self.create_metadata(format="epub")

        # Do not include cover for now
        cover_image = ""  # self.get_cover_image()
        cover_option = f"--epub-cover-image={cover_image} " if cover_image else ""
        extra_options = self.get_extra_pandoc_options(format="epub")

        print(f"Creating {self.book_epub}")
        os.makedirs(os.path.dirname(self.book_epub), exist_ok=True)
        extra_args = []
        if cover_option:
            extra_args.append(cover_option.strip())
        if extra_options:
            extra_args.extend(extra_options.split())
        exit_code = self._run_pandoc(book_md, self.book_epub, extra_args=extra_args, metadata_file=metadata_file)
        if exit_code != 0:
            print("Failed to generate epub")
            sys.exit(1)
        if os.path.exists(metadata_file):
            os.remove(metadata_file)

    def create_docx(self):
        filename = self.book_docx
        print(f"Creating {filename}")

        docx_md = os.path.join(os.path.dirname(self.book_md), f"{os.path.splitext(os.path.basename(self.book_md))[0]}-docx.md")
        with open(docx_md, "w", encoding="utf-8", errors="ignore") as f:
            f.write(self.get_md_content(format="docx"))

        metadata_file = self.create_metadata(format="docx")
        extra_options = self.get_extra_pandoc_options(format="docx")

        # Ensure Pandoc does not auto-generate a table of contents for DOCX output.
        # Some Pandoc versions add a TOC when styles or templates request it, and Word
        # will later warn about that TOC field if it is present.
        extra_args = ["--to=docx", "--metadata=toc=false"]
        if extra_options:
            extra_args.extend(extra_options.split())
        exit_code = self._run_pandoc(docx_md, filename, extra_args=extra_args, metadata_file=metadata_file)
        if exit_code != 0:
            print("Failed to generate docx")
            sys.exit(1)
        if os.path.exists(metadata_file):
            os.remove(metadata_file)
        if os.path.exists(docx_md):
            os.remove(docx_md)

    def create_pdf(self):
        pdf_md = os.path.join(os.path.dirname(self.book_md), f"{os.path.splitext(os.path.basename(self.book_md))[0]}-pdf.md")
        with open(pdf_md, "w", encoding="utf-8", errors="ignore") as f:
            f.write(self.get_md_content(format="pdf"))

        metadata_file = self.create_metadata(format="pdf")
        extra_options = self.get_extra_pandoc_options(format="pdf")

        print(f"Creating {self.book_pdf}")
        os.makedirs(os.path.dirname(self.book_pdf), exist_ok=True)
        extra_args = []
        cover_file = None
        if os.path.exists(self.get_cover_image()):
            cover_file = os.path.join(os.path.dirname(self.book_pdf), "cover.tex")
            with open(cover_file, "w", encoding="utf-8", errors="ignore") as f:
                f.write(self.get_cover_tex_content())
            extra_args.append(f"--include-before-body={cover_file}")
        if extra_options:
            extra_args.extend(extra_options.split())
        exit_code = self._run_pandoc(pdf_md, self.book_pdf, extra_args=extra_args, metadata_file=metadata_file, template=self.mytemplate_tex, pdf_engine="xelatex")
        if exit_code != 0:
            print("Failed to generate pdf")
        if os.path.exists(metadata_file):
            os.remove(metadata_file)
        if os.path.exists(pdf_md):
            os.remove(pdf_md)
        if cover_file and os.path.exists(cover_file):
            os.remove(cover_file)

    def create_paperback_pdf(self):
        print(f"Creating {self.book_paperback_pdf}")
        os.makedirs(os.path.dirname(self.book_paperback_pdf), exist_ok=True)

        paperback_md = os.path.join(os.path.dirname(self.book_md), f"{os.path.splitext(os.path.basename(self.book_md))[0]}-paperback.md")
        with open(paperback_md, "w", encoding="utf-8", errors="ignore") as f:
            f.write(self.get_md_content(format="paperback"))

        metadata_file = self.create_metadata(format="paperback")
        extra_options = self.get_extra_pandoc_options(format="paperback")
        extra_args = [
            "--variable=paper-size:a5",
            "--variable=margin-left:0.75in",
            "--variable=margin-right:0.75in",
            "--variable=margin-top:1in",
            "--variable=margin-bottom:1in",
        ]
        if extra_options:
            extra_args.extend(extra_options.split())
        exit_code = self._run_pandoc(paperback_md, self.book_paperback_pdf, extra_args=extra_args, metadata_file=metadata_file, template=self.mytemplate_tex, pdf_engine="xelatex")
        if exit_code != 0:
            print("Failed to generate paperback pdf")
        if os.path.exists(metadata_file):
            os.remove(metadata_file)
        if os.path.exists(paperback_md):
            os.remove(paperback_md)

    def create_metadata(self, format):
        metadata_path = self.metadata
        if format == "paperback":
            metadata_path = self.metadata.replace(".yaml", "-paperback.yaml")
        elif format == "pdf":
            metadata_path = self.metadata.replace(".yaml", "-pdf.yaml")
        elif format == "docx":
            metadata_path = self.metadata.replace(".yaml", "-docx.yaml")
        elif format == "epub":
            metadata_path = self.metadata.replace(".yaml", "-epub.yaml")

        with open(self.metadata, "r", encoding="utf-8", errors="ignore") as f:
            metadata_content = f.read().rstrip()

        if format == "paperback":
            metadata_content = metadata_content.replace("oneside", "twoside")

        metadata_content = re.sub(
            r"(?m)^toc:\s*(true|false)\s*$",
            f"toc: {'true' if self.toc else 'false'}",
            metadata_content,
            count=1,
        )

        copyright_path = self.get_copyright_md(format)
        before_toc = ""
        if os.path.exists(copyright_path):
            with open(copyright_path, "r", encoding="utf-8", errors="ignore") as f:
                before_toc = f.read().strip()

        if before_toc:
            block = "before-toc: |\n"
            for line in before_toc.splitlines():
                block += f"  {line}\n"
            if metadata_content.endswith("---"):
                metadata_content = metadata_content[:-3].rstrip() + "\n\n" + block.rstrip() + "\n---\n"
            else:
                metadata_content = metadata_content.rstrip() + "\n\n" + block.rstrip() + "\n"

        with open(metadata_path, "w", encoding="utf-8", errors="ignore") as fout:
            fout.write(metadata_content)
        return metadata_path

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
