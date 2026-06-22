import os
import re

from .base import BaseBook


class TheCloudOfUnknowing(BaseBook):
    base_dir = os.path.join("external", "the-cloud-of-unknowing")
    chapters_dir = os.path.join(base_dir, "chapters")

    def __init__(self):
        super().__init__("the-cloud-of-unknowing")

    def get_chapters(self, format):
        files = [
            os.path.join(self.base_dir, "blank.md"),
            self.get_copyright_md(format),
            os.path.join(self.base_dir, "preface.md"),
        ]
        files.extend(self._get_chapters())
        files.append(os.path.join(self.base_dir, "epilogue.md"))
        return files

    def _get_chapters(self):
        for file in sorted(os.listdir(self.chapters_dir)):
            if not file.endswith(".md"):
                continue
            filepath = os.path.join(self.chapters_dir, file)
            yield filepath

    def get_epub_markdown_content(self):
        content = self.get_md_content(format="epub")
        content = re.sub(r"^# ", r"## ", content, flags=re.MULTILINE)
        return content
