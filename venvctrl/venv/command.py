"""Virtual environment command mixin."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import collections
import shlex
import subprocess


CommandResult = collections.namedtuple('CommandResult', ('code', 'out', 'err'))


class CommandMixin(object):

    """Mixin which adds ability to execute commands."""

    @staticmethod
    def _execute(cmd):
        """Run a command in a subshell."""
        cmd = shlex.split(cmd)
        print(cmd)
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = proc.communicate()
        print(out, err)
        if proc.returncode != 0:

            raise subprocess.CalledProcessError(
                returncode=proc.returncode,
                cmd=cmd,
                output=err,
            )

        return CommandResult(
            code=proc.returncode,
            out=out.decode(),
            err=err.decode(),
        )

    def cmd_path(self, cmd):
        """Get the path of a command in the virtual if it exists.

        Args:
            cmd (str): The command to look for.

        Returns:
            str: The full path to the command.

        Raises:
            ValueError: If the command is not present.
        """
        for binscript in self.bin.files:

            if binscript.path.endswith('/{0}'.format(cmd)):

                return binscript.path

        raise ValueError('The command {0} was not found.'.format(cmd))

    def run(self, cmd):
        """Execute a script from the virtual environment /bin directory."""
        return self._execute(self.cmd_path(cmd))

    def python(self, cmd):
        """Execute a python script using the virtual environment python."""
        python_bin = self.cmd_path('python')
        cmd = '{0} {1}'.format(python_bin, cmd)
        return self._execute(cmd)

    def pip(self, cmd):
        """Execute some pip function using the virtual environment pip."""
        pip_bin = self.cmd_path('pip')
        cmd = '{0} {1}'.format(pip_bin, cmd)
        return self._execute(cmd)
