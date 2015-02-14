"""Test suites for virtual environment features."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import uuid

import pytest

from venvctrl import api


@pytest.fixture(scope='function')
def random():
    """Get a random UUID."""
    return str(uuid.uuid4())


@pytest.fixture(scope='function')
def venv(random, tmpdir):
    """Get an initialized venv."""
    v = api.VirtualEnvironment(str(tmpdir.join(random)))
    v.create()
    return v


def test_create(random, tmpdir):
    """Test if new virtual environments can be created."""
    path = str(tmpdir.join(random))
    venv = api.VirtualEnvironment(path)
    venv.create()
    assert tmpdir.join(random).check()


def test_pip(venv):
    """Test the ability to manage packages with pip."""
    venv.install_package('confpy')
    assert venv.has_package('confpy')
    venv.uninstall_package('confpy')
    assert not venv.has_package('confpy')
    path = os.path.join(venv.path, '..', 'requirements.txt')
    with open(path, 'w') as req_file:

        req_file.write('confpy{0}'.format(os.linesep))

    venv.install_requirements(path)
    assert venv.has_package('confpy')


def test_relocate(venv):
    """Test the ability to relocate a venv."""
    path = '/testpath'
    venv.relocate(path)
    for activate in venv.bin.activates:

        assert activate.vpath == path

    for script in venv.bin.files:

        if script.shebang:

            assert script.shebang == '#!{0}/bin/python{1}'.format(
                path,
                os.linesep,
            )
