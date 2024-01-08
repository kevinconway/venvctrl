"""Test fixtures and configuration."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import uuid

import pytest

from venvctrl import api


def pytest_generate_tests(metafunc):
    if "use_stdlib_venv" in metafunc.fixturenames:
        metafunc.parametrize("use_stdlib_venv", (True, False))


@pytest.fixture(scope="function")
def random():
    """Get a random UUID."""
    return str(uuid.uuid4())


@pytest.fixture(scope="function")
def venv(random, tmpdir, use_stdlib_venv):
    """Get an initialized venv."""
    path = str(tmpdir.join(random))
    v = api.VirtualEnvironment(path)
    if not use_stdlib_venv:
        v.create()
    else:
        v._execute("python -m venv {0}".format(path))
    return v
