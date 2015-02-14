"""Virtual environment object interface."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import tempfile


class VenvPath(object):

    """A path in the virtual environment."""

    def __init__(self, path):
        """Initialize the VenvPath with a file system path.

        Args:
            path (str): A file system path.
        """
        self._path = path

    @property
    def path(self):
        """Get the original path."""
        return self._path

    @property
    def abspath(self):
        """The the absolute path for the item."""
        return os.path.abspath(self.path)

    @property
    def realpath(self):
        """Get the path with symbolic links resolved."""
        return os.path.realpath(self.path)

    @property
    def is_absolute(self):
        """Get if the path is an absolute path."""
        return os.path.isabs(self.path)

    @property
    def is_file(self):
        """Get if the path is a file object."""
        return os.path.isfile(self.path)

    @property
    def is_dir(self):
        """Get if the path is a directory object."""
        return os.path.isdir(self.path)

    @property
    def is_link(self):
        """Get if the path is a symbolic link."""
        return os.path.islink(self.path)

    @property
    def exists(self):
        """Get if the path exists."""
        return os.path.exists(self.path)


class VenvFile(VenvPath):

    """A file within a virtual environment."""

    def writeline(self, line, line_number):
        """Rewrite a single line in the file.

        Args:
            line (str): The new text to write to the file.
            line_number (int): The line of the file to rewrite. Numbering
                starts at 0.
        """
        tmp_file = tempfile.TemporaryFile('w+')
        if not line.endswith(os.linesep):

            line += os.linesep
        try:

            with open(self.path, 'r') as file_handle:

                for count, new_line in enumerate(file_handle):

                    if count == line_number:

                        new_line = line

                    tmp_file.write(new_line)

            tmp_file.seek(0)
            with open(self.path, 'w') as file_handle:

                for new_line in tmp_file:

                    file_handle.write(new_line)
        finally:

            tmp_file.close()


class VenvDir(VenvPath):

    """A directory within a virtual environment."""

    @property
    def paths(self):
        """Get an iter of VenvPaths within the directory."""
        contents = os.listdir(self.path)
        contents = (os.path.join(self.path, path) for path in contents)
        contents = (VenvPath(path) for path in contents)
        return contents

    @property
    def files(self):
        """Get an iter of VenvFiles within the directory."""
        contents = self.paths
        contents = (VenvFile(path.path) for path in contents if path.is_file)
        return contents

    @property
    def dirs(self):
        """Get an iter of VenvDirs within the directory."""
        contents = self.paths
        contents = (VenvDir(path.path) for path in contents if path.is_dir)
        return contents

    @property
    def items(self):
        """Get an iter of VenvDirs and VenvFiles within the directory."""
        contents = self.paths
        contents = (
            VenvFile(path.path) if path.is_file else VenvDir(path.path)
            for path in contents
        )
        return contents

    def __iter__(self):
        """Iter over items."""
        return iter(self.items)


class BinFile(VenvFile):

    """An executable file from a virtual environment."""

    @property
    def shebang(self):
        """Get the file shebang if is has one."""
        with open(self.path, 'rb') as file_handle:
            hashtag = file_handle.read(2)
            if hashtag == b'#!':

                file_handle.seek(0)
                return file_handle.readline().decode()

        return None

    @shebang.setter
    def shebang(self, new_shebang):
        """Write a new shebang to the file.

        Raises:
            ValueError: If the file has no shebang to modify.
            ValueError: If the new shebang is invalid.
        """
        if not self.shebang:

            raise ValueError('Cannot modify a shebang if it does not exist.')

        if not new_shebang.startswith('#!'):

            raise ValueError('Invalid shebang.')

        self.writeline(new_shebang, 0)


class ActivateFile(BinFile):

    """The virtual environment /bin/activate script."""

    read_pattern = re.compile(r'^VIRTUAL_ENV="(.*)"$')
    write_pattern = 'VIRTUAL_ENV="{0}"'

    def _find_vpath(self):
        """Find the VIRTUAL_ENV path entry."""
        with open(self.path, 'r') as file_handle:

            for count, line in enumerate(file_handle):

                match = self.read_pattern.match(line)
                if match:

                    return match.group(1), count

        return None, None

    @property
    def vpath(self):
        """Get the path to the virtual environment."""
        return self._find_vpath()[0]

    @vpath.setter
    def vpath(self, new_vpath):
        """Change the path to the virtual environment."""
        _, line_number = self._find_vpath()
        new_vpath = self.write_pattern.format(new_vpath)
        self.writeline(new_vpath, line_number)


class ActivateFishFile(ActivateFile):

    """The virtual environment /bin/activate.fish script."""

    read_pattern = re.compile(r'^set -gx VIRTUAL_ENV "(.*)"$')
    write_pattern = 'set -gx VIRTUAL_ENV "{0}"'


class ActivateCshFile(ActivateFile):

    """The virtual environment /bin/activate.csh script."""

    read_pattern = re.compile(r'^setenv VIRTUAL_ENV "(.*)"$')
    write_pattern = 'setenv VIRTUAL_ENV "{0}"'


class BinDir(VenvDir):

    """Specialized VenvDir for the /bin directory."""

    @property
    def activates(self):
        """Get an iter of activate files in the virtual environment."""
        return (self.activate_sh, self.activate_csh, self.activate_fish)

    @property
    def activate_sh(self):
        """Get the /bin/activate script."""
        return ActivateFile(os.path.join(self.path, 'activate'))

    @property
    def activate_csh(self):
        """Get the /bin/activate.csh script."""
        return ActivateCshFile(os.path.join(self.path, 'activate.csh'))

    @property
    def activate_fish(self):
        """Get the /bin/activate.fish script."""
        return ActivateFishFile(os.path.join(self.path, 'activate.fish'))

    @property
    def files(self):
        """Get an iter of VenvFiles within the directory."""
        contents = self.paths
        contents = (BinFile(path.path) for path in contents if path.is_file)
        return contents

    @property
    def dirs(self):
        """Get an iter of VenvDirs within the directory."""
        contents = self.paths
        contents = (BinDir(path.path) for path in contents if path.is_dir)
        return contents

    @property
    def items(self):
        """Get an iter of VenvDirs and VenvFiles within the directory."""
        contents = self.paths
        contents = (
            BinFile(path.path) if path.is_file else BinDir(path.path)
            for path in contents
        )
        return contents


class VirtualEnvironment(VenvDir):

    """A virtual environment on a system."""

    @property
    def bin(self):
        """Get the /bin directory."""
        return BinDir(os.path.join(self.path, 'bin'))

    @property
    def include(self):
        """Get the /include directory."""
        return VenvDir(os.path.join(self.path, 'include'))

    @property
    def lib(self):
        """Get the /lib directory."""
        return VenvDir(os.path.join(self.path, 'lib'))

    @property
    def local(self):
        """Get the /local directory."""
        return VenvDir(os.path.join(self.path, 'local'))
