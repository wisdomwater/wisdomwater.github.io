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

