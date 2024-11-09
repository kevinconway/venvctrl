"""Test suites for virtual environment features."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import subprocess

from venvctrl import api


def test_create(random, tmpdir):
    """Test if new virtual environments can be created."""
    path = str(tmpdir.join(random))
    venv = api.VirtualEnvironment(path)
    try:
        venv.create()
    except subprocess.CalledProcessError as exc:
        assert False, exc.output
    assert tmpdir.join(random).check()


def test_pip(venv):
    """Test the ability to manage packages with pip."""
    venv.install_package("confpy")
    assert venv.has_package("confpy")
    venv.uninstall_package("confpy")
    assert not venv.has_package("confpy")
    path = os.path.join(venv.path, "..", "requirements.txt")
    with open(path, "w") as req_file:

        req_file.write("confpy{0}".format(os.linesep))

    venv.install_requirements(path)
    assert venv.has_package("confpy")


def test_relocate(venv):
    """Test the ability to relocate a venv."""
    path = "/testpath"
    pypy_shebang = "#!/usr/bin/env pypy"
    f = open(venv.bin.abspath + "/pypy_shebang.py", "w")
    f.write(pypy_shebang)
    f.close()
    venv.relocate(path)
    for activate in venv.bin.activates:

        assert activate.vpath == path

    for script in venv.bin.files:

        if script.shebang:

            assert script.shebang == "#!{0}/bin/python".format(path)


def test_relocate_long_shebang(venv):
    """Test the ability to relocate a venv."""
    path = "/testpath"
    long_shebang = (
        "#!/bin/sh{0}"
        "'''exec' /tmp/rpmbuild/python \"$0\" \"$@\"{0}"
        "' '''{0}".format(os.linesep)
    )
    f = open(venv.bin.abspath + "/long_shebang.py", "w")
    f.write(long_shebang)
    f.close()
    venv.relocate(path)
    for activate in venv.bin.activates:
        assert activate.vpath == path

    for script in venv.bin.files:
        shebang = script.shebang
        if shebang:
            shebang = shebang.split(os.linesep)
            if len(shebang) == 1:
                assert shebang == ["#!{0}/bin/python".format(path)]

            elif len(shebang) == 3:
                assert shebang == [
                    "#!/bin/sh",
                    "'''exec' {0}/bin/python \"$0\" \"$@\"".format(path),
                    "' '''",
                ]

            else:
                assert False, "Invalid shebang length: {0}, {1}".format(
                    len(shebang), script.shebang
                )


def test_relocate_no_original_path(venv):
    """Test that the original path is not found in any non-binary file."""
    path = "/testpath"
    original_path = venv.abspath
    # Drop a .pth in the virtualenv/venv to ensure that we're still testing
    # these files even if they aren't generated anymore in modern builds.
    f = open(venv.bin.abspath + "/something.pth", "w")
    f.write(original_path)
    f.close()
    venv.relocate(path)
    dirs = [venv]
    while dirs:
        current = dirs.pop()
        dirs.extend(current.dirs)
        for file_ in current.files:
            if file_.abspath.endswith("pyvenv.cfg"):
                continue  # Skip the pytest installed files
            with open(file_.abspath, "r") as source:
                try:
                    lines = source.readlines()
                except UnicodeDecodeError:
                    # Skip any non-text files. Binary files are out of
                    # scope for this test.
                    continue
                for line in lines:
                    assert original_path not in line, file_.abspath
