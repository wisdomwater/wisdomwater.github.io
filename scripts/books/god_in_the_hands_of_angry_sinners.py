import os

from .base import BaseBook


class GodInTheHandsOfAngrySinners(BaseBook):
    mytemplate_tex = os.path.join("scripts", "my-template-god-in-the-hands-of-angry-sinners.tex")

    base_dir = os.path.join("external", "god-in-the-hands-of-angry-sinners")
    chapters_dir = os.path.join(base_dir, "chapters")

    def __init__(self):
        super().__init__("god-in-the-hands-of-angry-sinners")

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

