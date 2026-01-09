import os

from .base import BaseBook


class HeldToTheEnd(BaseBook):
    base_dir = os.path.join("external", "held-to-the-end")
    chapters_dir = os.path.join(base_dir, "chapters")

    def __init__(self):
        super().__init__("held-to-the-end")

    def get_chapters(self, format):
        files = [
            os.path.join(self.base_dir, "blank.md"),
            self.get_copyright_md(format),
            os.path.join(self.base_dir, "preface.md"),
        ]
        files.extend(self._get_chapters())
        return files

    def _get_chapters(self):
        for file in sorted(os.listdir(self.chapters_dir)):
            if not file.endswith(".md"):
                continue
            filepath = os.path.join(self.chapters_dir, file)
            yield filepath

    def create_paperback_pdf(self):
        print(f"Creating {self.book_paperback_pdf}")
        os.makedirs(os.path.dirname(self.book_paperback_pdf), exist_ok=True)
        metadata_file = self.create_paperback_metadata(self.metadata)
        exit_code = os.system(
            f"pandoc {self.book_md} -o {self.book_paperback_pdf} --pdf-engine=xelatex --metadata-file={metadata_file} --template={self.mytemplate_tex} --lua-filter={self.pagebreak_lua} --variable=paper-size:a5 --variable=margin-left:0.75in --variable=margin-right:0.75in --variable=margin-top:1in --variable=margin-bottom:1in"
        )
        if exit_code != 0:
            print("Failed to generate paperback pdf")
        if os.path.exists(metadata_file):
            os.remove(metadata_file)
