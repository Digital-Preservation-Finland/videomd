"""
Install videomd
"""

from setuptools import setup, find_packages
from version import get_version


def main():
    """Install videomd"""
    setup(
        name='videomd',
        packages=find_packages(exclude=['tests', 'tests.*']),
        version=get_version(),
        install_requires=[
            'lxml',
            'xml-helpers@git+https://gitlab.csc.fi/dpres/xml-helpers.git'
            '@develop'
        ]
    )


if __name__ == '__main__':
    main()
