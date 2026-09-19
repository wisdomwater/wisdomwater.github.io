import os
import re

from .base import BaseBook


class NumberGoUp(BaseBook):
    toc = True
    base_dir = os.path.join("external", "number-go-up")
    chapters_dir = os.path.join(base_dir, "chapters")

    def __init__(self):
        super().__init__("number-go-up")

    def get_chapters(self, format):
        dedication = "dedication-epub.md" if format in ("epub", "docx", "markdown") else "dedication.md"
        files = [
            self.get_copyright_md(format),
            os.path.join(self.base_dir, dedication),
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
