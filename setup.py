"""Package setup"""

import codecs
import re
from os.path import join as join_path, dirname
from setuptools import setup, find_packages


def setup_package():
    """Package setup"""
    setup(
        name='injectool',
        version=_get_version(),
        description='Dependency injection tool',
        long_description=_get_long_description(),
        long_description_content_type='text/markdown',
        url='https://github.com/eumis/injectool',
        author='eumis(Eugen Misievich)',
        author_email='misievich@gmail.com',
        license='MIT',
        classifiers=[
            #   2 - Pre-Alpha
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.6'
        ],
        python_requires='>=3.6',
        keywords='di dependency injection ioc inversion of control inject',
        packages=find_packages(exclude=['*.tests']))


_HERE = dirname(__file__)


def _get_version() -> str:
    with open(join_path(_HERE, "injectool", "__init__.py")) as file:
        pattern = re.compile(r"__version__ = '(.*)'")
        match = pattern.search(file.read())
        return match.group(1)


def _get_long_description():
    readme_path = join_path(_HERE, "README.md")
    with codecs.open(readme_path, encoding="utf-8") as readme:
        return "\n" + readme.read()


if __name__ == '__main__':
    setup_package()
