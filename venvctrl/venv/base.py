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
        tmp_file = tempfile.TemporaryFile("w+")
        if not line.endswith(os.linesep):

            line += os.linesep
        try:

            with open(self.path, "r") as file_handle:

                for count, new_line in enumerate(file_handle):

                    if count == line_number:

                        new_line = line

                    tmp_file.write(new_line)

            tmp_file.seek(0)
            with open(self.path, "w") as file_handle:

                for new_line in tmp_file:

                    file_handle.write(new_line)
        finally:

            tmp_file.close()

    def replace(self, old, new):
        """Replace old with new in every occurrence.

        Args:
            old (str): The original text.
            new (str): The new text.
        """
        tmp_file = tempfile.TemporaryFile("w+")
        try:

            with open(self.path, "r") as file_handle:

                for line in file_handle:

                    line = line.replace(old, new)
                    tmp_file.write(line)

            tmp_file.seek(0)
            with open(self.path, "w") as file_handle:

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
        with open(self.path, "rb") as file_handle:
            hashtag = file_handle.read(2)
            if hashtag == b"#!":
                # Check if we're using the new style shebang
                new_style_shebang = (
                    file_handle.readline() == b"/bin/sh\n"
                    and file_handle.read(8) == b"'''exec'"
                )

                file_handle.seek(0)
                return os.linesep.join(
                    [
                        next(file_handle).decode("utf8").strip()
                        for _ in range(3 if new_style_shebang else 1)
                    ]
                )

        return None

    @shebang.setter
    def shebang(self, new_shebang):
        """Write a new shebang to the file.

        Raises:
            ValueError: If the file has no shebang to modify.
            ValueError: If the new shebang is invalid.
        """

        if not self.shebang:

            raise ValueError("Cannot modify a shebang if it does not exist.")

        if new_shebang is None:

            raise ValueError("New shebang cannot be None.")

        old_shebang = self.shebang.strip().split(os.linesep)
        new_shebang = new_shebang.strip().split(os.linesep)

        if len(old_shebang) != len(new_shebang):

            raise ValueError(
                "Old and new shebangs must " "be same number of lines"
            )

        if not new_shebang[0].startswith("#!"):

            raise ValueError("Invalid shebang.")

        for line_num, line in enumerate(new_shebang):
            self.writeline(line, line_num)


class ActivateFile(BinFile):

    """A common base for all activate scripts.

    Implementations should replace the read_pattern for cases where the path can
    be extracted with a regex. More complex use cases should override the
    _find_vpath method to perform a search and return the appropriate path.
    """

    read_pattern = re.compile(r"""^VIRTUAL_ENV=["'](.*)["']$""")

    def _find_vpath(self):
        """
        Find the VIRTUAL_ENV path entry.

        Returns:
            tuple: A tuple containing the matched line, the old vpath, and the line number where the virtual
            path was found. If the virtual path is not found, returns a tuple of three None values.
        """
        with open(self.path, "r") as file_handle:

            for count, line in enumerate(file_handle):

                match = self.read_pattern.match(line)
                if match:

                    return match.group(0), match.group(1), count

        return None, None, None

    @property
    def vpath(self):
        """Get the path to the virtual environment."""
        return self._find_vpath()[1]

    @vpath.setter
    def vpath(self, new_vpath):
        """Change the path to the virtual environment."""
        old_line, old_vpath, line_number = self._find_vpath()
        new_line = old_line.replace(old_vpath, new_vpath)
        self.writeline(new_line, line_number)


class ActivateFileBash(ActivateFile):

    """The virtual environment /bin/activate script.

    This version accounts for differences between the virtualenv and venv
    activation scripts for bash.
    """

    read_pattern = re.compile(r"""^VIRTUAL_ENV=["']?(.*)["']?$""")
    read_pattern_stdlib_venv = re.compile(r"""^ *export VIRTUAL_ENV=["']?(.*)["']?$""")

    def _find_vpath(self):
        """
        Find the VIRTUAL_ENV path entry.

        Returns:
            tuple: A tuple containing the matched line, the old vpath, and the line number where the virtual
            path was found. If the virtual path is not found, returns a tuple of three None values.
        """
        with open(self.path, "r") as file_handle:

            for count, line in enumerate(file_handle):

                match = self.read_pattern.match(line)
                if match:

                    return match.group(0), match.group(1), count
                match = self.read_pattern_stdlib_venv.match(line)
                if match:

                    return match.group(0), match.group(1), count

        return None, None, None

    @property
    def vpath(self):
        """Get the path to the virtual environment."""
        return self._find_vpath()[1]

    @vpath.setter
    def vpath(self, new_vpath):
        """Change the path to the virtual environment.

        The bash activate file from the standard library venv duplicates the
        full path in multiple places instead of only one place like in
        virtualenv. To account, this code now does a line by line replacement
        of the old path to ensure that it is replaced everywhere.
        """
        _, old_vpath, _ = self._find_vpath()
        self.replace(old_vpath, new_vpath)


class ActivateFishFile(ActivateFile):

    """The virtual environment /bin/activate.fish script."""

    read_pattern = re.compile(r"""^set -gx VIRTUAL_ENV ["']?(.*)["']?$""")


class ActivateCshFile(ActivateFile):

    """The virtual environment /bin/activate.csh script."""

    read_pattern = re.compile(r"""^setenv VIRTUAL_ENV ["']?(.*)["']?$""")


class ActivateXshFile(ActivateFile):

    """The virtual environment /bin/activate.xsh script."""

    read_pattern = re.compile(r"""^\$VIRTUAL_ENV = r["']?(.*)["']?$""")


class ActivateNuFile(ActivateFile):

    """The virtual environment /bin/activate.nu script.

    Note that the NU shell activation script is different from previously
    supported shells because it contains two references to the virtualenv path
    rather than one. This is because it requires a specialized deactivate
    script which is aliased to the deactivate command.

    activate.nu:3 generated with virtualenv 20.13.3
    let virtual-env = "/tmp/test_venv"

    activate.nu:34 generated with virtualenv 20.21.0
    ....let virtual_env = '/tmp/test_venv'
    """

    read_pattern = re.compile(r"""^\s*let virtual[-_]env = r?\#?["']?(.*)["']?\#?$""")


class ActivateNuFileDeactivateAlias(ActivateFile):

    """The virtual environment /bin/activate.nu script's deactivate alias.

    This is the second part of the NU shell activation script modification
    This is implemented as a second activate script as a convenience. The
    ActivateFile base class only ever expected that a single line in the
    activate script would contain the virtualenv path. NU shell is the first
    script to break that expectation. Rather than re-write the ActivateFile
    class, this class models the second line containing the path as a second
    file in order to use the inherited regex matching logic.
    """

    read_pattern = re.compile(
        r"""^alias deactivate = source ["'](.*)/bin/deactivate.nu["']$"""
    )

    @property
    def exists(self):
        """
        Get if the path exists.

        Overwite VenvPath property. The /bin/activate.nu scipt generated
        by virtualenv>=20.14.0 does contain a virtual path anymore.
        So, relocation is only required for older versions.

        Returns:
            bool: True if the /bin/activate.nu exists and it contains a virtual path
                  for deactivate.
        """

        return os.path.exists(self.path) and self.vpath is not None


class BinDir(VenvDir):

    """Specialized VenvDir for the /bin directory."""

    @property
    def activates(self):
        """Get an iter of activate files in the virtual environment."""
        return (
            activation
            for activation in (
                self.activate_sh,
                self.activate_csh,
                self.activate_fish,
                self.activate_xsh,
                self.activate_nu,
                self.activate_nu_deactivate,
            )
            if activation.exists
        )

    @property
    def activate_sh(self):
        """Get the /bin/activate script."""
        return ActivateFileBash(os.path.join(self.path, "activate"))

    @property
    def activate_csh(self):
        """Get the /bin/activate.csh script."""
        return ActivateCshFile(os.path.join(self.path, "activate.csh"))

    @property
    def activate_fish(self):
        """Get the /bin/activate.fish script."""
        return ActivateFishFile(os.path.join(self.path, "activate.fish"))

    @property
    def activate_xsh(self):
        """Get the /bin/activate.xsh script."""
        return ActivateXshFile(os.path.join(self.path, "activate.xsh"))

    @property
    def activate_nu(self):
        """Get the /bin/activate.nu script."""
        return ActivateNuFile(os.path.join(self.path, "activate.nu"))

    @property
    def activate_nu_deactivate(self):
        """Get the /bin/activate.nu script.

        This returns the same underlying file as the activate_nu property but
        is configured to target all vpath operations to the secondary
        virtualenv path reference that exists to set up the deactivate
        command. Generally, any use of the activate_nu property to modify the
        vpath must be repeated with this property as well. See the
        ActivateNuFileDeactivateAlias class documentation for more information.
        """
        return ActivateNuFileDeactivateAlias(
            os.path.join(self.path, "activate.nu")
        )

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
        return BinDir(os.path.join(self.path, "bin"))

    @property
    def include(self):
        """Get the /include directory."""
        return VenvDir(os.path.join(self.path, "include"))

    @property
    def lib(self):
        """Get the /lib directory."""
        return VenvDir(os.path.join(self.path, "lib"))

    @property
    def local(self):
        """Get the /local directory."""
        return VenvDir(os.path.join(self.path, "local"))
