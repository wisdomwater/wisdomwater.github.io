import os
import sys
from textwrap import dedent

class BaseBook:
    pagebreak_lua = os.path.join("scripts", "pagebreak.lua")
    mytemplate_tex = os.path.join("scripts", "my-template.tex")

    def __init__(self, name,
    ):
        self.name = name
        self.metadata = os.path.join("external", name, "meta.yaml")
        self.book_md = os.path.join("output", name, f"{name}.md")
        self.book_epub_md = os.path.join("output", name, f"{name}-epub.md")
        self.book_pdf = os.path.join("output", name, f"{name}.pdf")
        self.book_epub = os.path.join("output", name, f"{name}.epub")
        self.cover_tex = os.path.join("output", name, "cover.tex")
        self.downloads_dir = os.path.join("docs", name, "downloads")
    
    def get_chapters(self):
        raise NotImplementedError()
    
    def get_epub_markdown_content(self):
        return ""
    
    def get_cover_image(self):
        return ""

    def create_md(self):
        filename = self.book_md
        print(f"Creating {filename}")

        files = self.get_chapters()
        
        content = ""
        for file in files:
            with open(file, encoding="utf-8", errors="ignore") as f:
                content += f.read()
                content += "\n::: pagebreak\n:::\n\n"
        content = content.strip()

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8", errors="ignore") as f:
            f.write(content)

    def create_epub(self):
        epub_markdown = self.get_epub_markdown_content()
        if epub_markdown:
            with open(self.book_epub_md, "w", encoding="utf-8", errors="ignore") as f:
                f.write(epub_markdown)
            book_md = self.book_epub_md
        else:
            book_md = self.book_md

        cover_image = self.get_cover_image()
        cover_option = f"--epub-cover-image={cover_image} " if cover_image else ""

        print(f"Creating {self.book_epub}")
        os.makedirs(os.path.dirname(self.book_epub), exist_ok=True)
        exit_code = os.system(
            f"pandoc {book_md} -o {self.book_epub} --metadata-file={self.metadata} {cover_option} --lua-filter={self.pagebreak_lua}"
        )
        if exit_code != 0:
            print("Failed to generate epub")
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
        dest_cover_image = os.path.join(self.downloads_dir, "cover" + os.path.splitext(self.get_cover_image())[1])

        os.makedirs(self.downloads_dir, exist_ok=True)
        if os.path.exists(self.book_pdf):
            os.system(f'copy /y "{self.book_pdf}" "{dest_pdf}"')
        if os.path.exists(self.book_epub):
            os.system(f'copy /y "{self.book_epub}" "{dest_epub}"')
        if os.path.exists(self.book_md):
            os.system(f'copy /y "{self.book_md}" "{dest_md}"')
        cover_image = self.get_cover_image()
        if os.path.exists(cover_image):
            os.system(f'copy /y "{cover_image}" "{dest_cover_image}"')

        print(f"Copied downloads to {self.downloads_dir}")
