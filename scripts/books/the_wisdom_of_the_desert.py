import os

from .base import BaseBook


class TheWisdomOfTheDesert(BaseBook):
    header_page_break = 1
    base_dir = os.path.join("external", "the-wisdom-of-the-desert")
    chapters_dir = os.path.join(base_dir, "chapters")
    file_page_break = True

    def __init__(self):
        super().__init__("the-wisdom-of-the-desert")

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
