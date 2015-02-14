"""Relocate a virtual environment."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse

from ..venv import api


def relocate(source, destination, move=False):
    """Adjust the virtual environment settings and optional move it.

    Args:
        source (str): Path to the existing virtual environment.
        destination (str): Desired path of the virtual environment.
        move (bool): Whether or not to actually move the files. Default False.
    """
    venv = api.VirtualEnvironment(source)
    if not move:

        venv.relocate(destination)
        return None

    venv.move(destination)


def main():
    """Relocate a virtual environment."""
    parser = argparse.ArgumentParser(
        description='Relocate a virtual environment.'
    )
    parser.add_argument(
        '--source',
        help='The existing virtual environment.',
        required=True,
    )
    parser.add_argument(
        '--destination',
        help='The location for which to configure the virtual environment.',
        required=True,
    )
    parser.add_argument(
        '--move',
        help='Move the virtual environment to the destination.',
        default=False,
        action='store_true',
    )

    args = parser.parse_args()
    relocate(args.source, args.destination, args.move)


if __name__ == '__main__':

    main()
