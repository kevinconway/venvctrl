"""Virtual environment pip mixin."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


class PipMixin(object):

    """Perform pip operations within a virtual environment.

    This mixin depends on the command mixin.
    """

    def has_package(self, name):
        """Determine if the given package is installed.

        Args:
            name (str): The package name to find.

        Returns:
            bool: True if installed else false.
        """
        return name in self.pip('list').out

    def install_package(self, name, index=None, force=False, update=False):
        """Install a given package.

        Args:
            name (str): The package name to install. This can be any valid
                pip package specification.
            index (str): The URL for a pypi index to use.
            force (bool): For the reinstall of packages during updates.
            update (bool): Update the package if it is out of date.
        """
        cmd = 'install'
        if force:

            cmd = '{0} {1}'.format(cmd, '--force-reinstall')

        if update:

            cmd = '{0} {1}'.format(cmd, '--update')

        if index:

            cmd = '{0} {1}'.format(cmd, '--index-url {0}'.format(index))

        self.pip('{0} {1}'.format(cmd, name))

    def uninstall_package(self, name):
        """Uninstall a given package.

        Args:
            name (str): The name of the package to uninstall.
        """
        self.pip('{0} --yes {1}'.format('uninstall', name))
