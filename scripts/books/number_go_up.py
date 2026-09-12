import os
import re

from .base import BaseBook


class NumberGoUp(BaseBook):
    base_dir = os.path.join("external", "number-go-up")
    chapters_dir = os.path.join(base_dir, "chapters")

    def __init__(self):
        super().__init__("number-go-up")

    def get_chapters(self, format):
        files = [
            os.path.join(self.base_dir, "blank.md"),
            os.path.join(self.base_dir, "blank.md"),
            self.get_copyright_md(format),
            os.path.join(self.base_dir, "dedication.md"),
            os.path.join(self.base_dir, "intro.md"),
        ]
        files.extend(self._get_chapters())
        files.extend([os.path.join(self.base_dir, "about.md")])
        return files

    def _get_chapters(self):
        for file in sorted(os.listdir(os.path.join(self.chapters_dir))):
            if not file.endswith(".md"):
                continue
            filepath = os.path.join(self.chapters_dir, file)
            yield filepath

    def _get_epub_chapters(self):
        files = [
            os.path.join(self.base_dir, "blank.md"),
            self.get_copyright_md(format),
            os.path.join(self.base_dir, "dedication-epub.md"),
            os.path.join(self.base_dir, "intro.md"),
        ]
        files.extend(self._get_chapters())
        files.extend([os.path.join(self.base_dir, "about.md")])
        return files

    def create_paperback_pdf(self):
        print(f"Creating {self.book_paperback_pdf}")
        os.makedirs(os.path.dirname(self.book_paperback_pdf), exist_ok=True)
        metadata_file = self.create_paperback_metadata(self.metadata)
        extra_options = self.get_extra_pandoc_options(format="paperback")
        exit_code = os.system(
            f"pandoc {self.book_md} -o {self.book_paperback_pdf} --pdf-engine=xelatex --metadata-file={metadata_file} --metadata=toc:true --template={self.mytemplate_tex} --lua-filter={self.pagebreak_lua} --variable=paper-size:a5 --variable=margin-left:0.75in --variable=margin-right:0.75in --variable=margin-top:1in --variable=margin-bottom:1in {extra_options}"
        )
        if exit_code != 0:
            print("Failed to generate paperback pdf")
        if os.path.exists(metadata_file):
            os.remove(metadata_file)

    def get_epub_markdown_content(self):
        content = self._get_md_content_from_files(self._get_epub_chapters())
        return content
    