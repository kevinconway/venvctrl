"""Setuptools configuration for venvctrl."""

from setuptools import setup
from setuptools import find_packages


with open('README.rst', 'r') as readmefile:

    README = readmefile.read()

setup(
    name='venvctrl',
    version='0.1.0',
    url='https://github.com/kevinconway/venvctrl',
    description='API for virtual environments.',
    author="Kevin Conway",
    author_email="kevinjacobconway@gmail.com",
    long_description=README,
    license='MIT',
    packages=find_packages(exclude=['tests', 'build', 'dist', 'docs']),
    entry_points={
        'console_scripts': [
            'venvctrl-relocate = venvctrl.cli.relocate:main',
        ],
    },
    include_package_data=True,
)
