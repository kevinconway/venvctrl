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
                        'python' in shebang[0] or 'pypy' in shebang[0]
                ):
                    binfile.shebang = '#!{0}'.format(
                        os.path.join(destination, 'bin', 'python')
                    )
                elif len(shebang) == 3 and (
                        'python' in shebang[1] or 'pypy' in shebang[1]
                ):
                    shebang[1] = '\'\'\'exec\' {0} "$0" "$@"'.format(
                        os.path.join(destination, 'bin', 'python')
                    )
                    binfile.shebang = os.linesep.join(shebang)

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
