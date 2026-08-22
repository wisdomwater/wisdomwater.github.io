import os
import re

from .base import BaseBook


class TheWayOfTheWord(BaseBook):
    base_dir = os.path.join("external", "the-way-of-the-word")
    chapters_dir = os.path.join(base_dir, "chapters")

    def __init__(self):
        super().__init__("the-way-of-the-word")

    def get_chapters(self, format):
        files = [
            os.path.join(self.base_dir, "blank.md"),
            self.get_copyright_md(format),
            os.path.join(self.base_dir, "preface.md"),
            os.path.join(self.base_dir, "blank.md")
        ]
        files.extend(self._get_chapters())
        files.append(os.path.join(self.base_dir, "epilogue.md"))
        return files
    
    def _get_chapters(self):
        for file in sorted(os.listdir(os.path.join(self.chapters_dir))):
            if not file.endswith(".md"):
                continue
            filepath = os.path.join(self.chapters_dir, file)
            yield filepath
