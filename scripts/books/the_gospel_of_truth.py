import os

from .base import BaseBook


class TheGospelOfTruth(BaseBook):
    header_page_break = 1
    base_dir = os.path.join("external", "the-gospel-of-truth")
    chapters_dir = os.path.join(base_dir, "chapters")
    toc = False

    def __init__(self):
        super().__init__("the-gospel-of-truth")

    def get_chapters(self, format):
        files = [
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
