"""Virtual environment relocatable mixin."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import shutil


class RelocateMixin(object):

    """Mixin which adds the ability to relocate a virtual environment."""

    def relocate(self, destination):
        """Configure the virtual environment for another path.

        Args:
            destination (str): The target path of the virtual environment.

        Note:
            This does not actually move the virtual environment. Is only
            rewrites the metadata required to support a move.
        """
        for activate in self.bin.activates:

            activate.vpath = destination

        for binfile in self.bin.files:

            shebang = binfile.shebang
            if shebang:
                shebang = shebang.strip().split(os.linesep)

                if len(shebang) == 1 and (
                    "python" in shebang[0] or "pypy" in shebang[0]
                ):
                    binfile.shebang = "#!{0}".format(
                        os.path.join(destination, "bin", "python")
                    )
                elif len(shebang) == 3 and (
                    "python" in shebang[1] or "pypy" in shebang[1]
                ):
                    shebang[1] = "'''exec' {0} \"$0\" \"$@\"".format(
                        os.path.join(destination, "bin", "python")
                    )
                    binfile.shebang = os.linesep.join(shebang)

        # Even though wheel is the official format, there are still several
        # cases in the wild where eggs are being installed. Eggs come with the
        # possibility of .pth files. Each .pth file contains the path to where
        # a module can be found. To handle them we must recurse the entire
        # venv file tree since they can be either at the root of the
        # site-packages, bundled within an egg directory, or both.
        original_path = self.path
        original_abspath = self.abspath
        dirs = [self]
        while dirs:
            current = dirs.pop()
            dirs.extend(current.dirs)
            for file_ in current.files:
                if file_.abspath.endswith(".pth"):
                    content = ""
                    with open(file_.abspath, "r") as source:
                        # .pth files are almost always very small. Because of
                        # this we read the whole file as a convenience.
                        content = source.read()
                    # It's not certain whether the .pth will have a relative
                    # or absolute path so we replace both in order of most to
                    # least specific.
                    content = content.replace(original_abspath, destination)
                    content = content.replace(original_path, destination)
                    with open(file_.abspath, "w") as source:
                        source.write(content)

    def move(self, destination):
        """Reconfigure and move the virtual environment to another path.

        Args:
            destination (str): The target path of the virtual environment.

        Note:
            Unlike `relocate`, this method *will* move the virtual to the
            given path.
        """
        self.relocate(destination)
        shutil.move(self.path, destination)
        self._path = destination
