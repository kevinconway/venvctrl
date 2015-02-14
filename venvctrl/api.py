"""Full featured virtual environment API."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from .venv import base
from .venv import command
from .venv import create
from .venv import pip
from .venv import relocate


class VirtualEnvironment(
        base.VirtualEnvironment,
        command.CommandMixin,
        create.CreateMixin,
        pip.PipMixin,
        relocate.RelocateMixin,
):

    """Virtual environment management class."""
