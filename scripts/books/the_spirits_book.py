import os
import re

from .base import BaseBook


class TheSpiritsBook(BaseBook):
    base_dir = os.path.join("external", "the-spirits-book")
    chapters_dir = os.path.join(base_dir, "chapters")

    def __init__(self):
        super().__init__("the-spirits-book")

    def get_chapters(self, format):
        files = [
            os.path.join(self.base_dir, "blank.md"),
            self.get_copyright_md(format),
            os.path.join(self.base_dir, "preface.md"),
            os.path.join(self.base_dir, "prefaces", "1-translators-preface.md"),
            os.path.join(self.base_dir, "prefaces", "2-anna-blackwell-preface.md"),
            os.path.join(self.base_dir, "prefaces", "3-revised-edition-preface.md"),
        ]
        files.extend(self._get_chapters())
        return files
    
    def _get_chapters(self):
        for subdir in sorted(os.listdir(self.chapters_dir)):
            if not os.path.isdir(os.path.join(self.chapters_dir, subdir)):
                continue
            for file in sorted(os.listdir(os.path.join(self.chapters_dir, subdir))):
                if not file.endswith(".md"):
                    continue
                filepath = os.path.join(self.chapters_dir, subdir, file)
                yield filepath
