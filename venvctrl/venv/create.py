"""Virtual environment create mixin."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


class CreateMixin(object):

    """Can create new virtual environments.

    This mixin requires the command mixin.
    """

    def create(self, python=None, system_site=False, always_copy=False):
        """Create a new virtual environment.

        Args:
            python (str): The name or path of a python interpreter to use while
                creating the virtual environment.
            system_site (bool): Whether or not use use the system site packages
                within the virtual environment. Default is False.
            always_copy (bool): Whether or not to force copying instead of
                symlinking in the virtual environment. Default is False.
        """
        command = 'virtualenv'
        if python:

            command = '{0} --python={1}'.format(command, python)

        if system_site:

            command = '{0} --system-site-packages'.format(command)

        if always_copy:

            command = '{0} --always-copy'.format(command)

        command = '{0} {1}'.format(command, self.path)
        self._execute(command)
