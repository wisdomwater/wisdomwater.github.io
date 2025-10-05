import os
import re

from .base import BaseBook


class PistisSophia(BaseBook):
    base_dir = os.path.join("external", "pistis-sophia")
    chapters_dir = os.path.join(base_dir, "chapters")

    def __init__(self):
        super().__init__("pistis-sophia")

    def get_chapters(self, format):
        files = [
            os.path.join(self.base_dir, "blank.md"),
            self.get_copyright_md(format),
            os.path.join(self.base_dir, "preface.md"),
        ]
        files.extend(self._get_chapters())
        return files

    def get_cover_image(self):
        return os.path.join(self.base_dir, "artwork", "cover.png")
    
    def get_copyright_md(self, format):
        if format == "epub":
            return os.path.join(self.base_dir, "copyright-epub.md")
        return os.path.join(self.base_dir, "copyright.md")

    def _get_chapters(self):
        for subdir in sorted(os.listdir(self.chapters_dir)):
            if not os.path.isdir(os.path.join(self.chapters_dir, subdir)):
                continue
            for file in sorted(os.listdir(os.path.join(self.chapters_dir, subdir))):
                if not file.endswith(".md"):
                    continue
                filepath = os.path.join(self.chapters_dir, subdir, file)
                yield filepath

    def get_epub_markdown_content(self):
        content = self.get_md_content(format="epub")
        content = re.sub(r"^## ", r"# ", content, flags=re.MULTILINE)
        return content
