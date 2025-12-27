import os

from .base import BaseBook


class TheFirstLight(BaseBook):
    base_dir = os.path.join("external", "the-first-light")
    chapters_dir = os.path.join(base_dir, "chapters")

    def __init__(self):
        super().__init__("the-first-light")

    def get_chapters(self, format):
        files = [
            os.path.join(self.base_dir, "blank.md"),
            self.get_copyright_md(format),
            os.path.join(self.base_dir, "preface.md"),
        ]
        files.extend(self._get_chapters())
        files.append(os.path.join(self.base_dir, "appendix.md"))
        return files

    def _get_chapters(self):
        for file in sorted(os.listdir(self.chapters_dir)):
            if not file.endswith(".md"):
                continue
            filepath = os.path.join(self.chapters_dir, file)
            yield filepath
