import os

from .base import BaseBook


class BardoThodol(BaseBook):
    base_dir = os.path.join("external", "bardo-thodol")
    chapters_dir = os.path.join(base_dir, "chapters")

    def __init__(self):
        super().__init__("bardo-thodol")

    def get_chapters(self, format):
        files = [
            os.path.join(self.base_dir, "blank.md"),
            self.get_copyright_md(format),
            os.path.join(self.base_dir, "introduction.md"),
        ]
        files.extend(self._get_chapters())
        files.append(os.path.join(self.base_dir, "epilogue.md"))
        return files

    def get_cover_image(self):
        return os.path.join(self.base_dir, "artwork", "cover.png")
    
    def get_copyright_md(self, format):
        if format == "epub":
            return os.path.join(self.base_dir, "copyright-epub.md")
        return os.path.join(self.base_dir, "copyright.md")

    def _get_chapters(self):
        for file in sorted(os.listdir(self.chapters_dir)):
            if not file.endswith(".md"):
                continue
            filepath = os.path.join(self.chapters_dir, file)
            yield filepath
