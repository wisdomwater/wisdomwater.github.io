import os

from .base import BaseBook


class TheGreaterMercy(BaseBook):
    base_dir = os.path.join("external", "the-greater-mercy")
    chapters_dir = os.path.join(base_dir, "chapters")

    def __init__(self):
        super().__init__("the-greater-mercy")

    def get_chapters(self):
        files = [
            os.path.join(self.base_dir, "foreword.md"),
        ]
        files.extend(self._get_chapters())
        return files

    def get_cover_image(self):
        return os.path.join(self.base_dir, "artwork", "cover.png")
    
    def _get_chapters(self):
        for file in sorted(os.listdir(self.chapters_dir)):
            filepath = os.path.join(self.chapters_dir, file)
            yield filepath
