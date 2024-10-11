from distutils.core import setup
from setuptools import find_packages

__version__ = "0.0.0-post.38+9edf86a"

setup(
    name="tai_ttex",
    version=__version__,
    packages=find_packages(),
    install_requires=[],
    license="GPL3",
    long_description="Tool for experiments",
    long_description_content_type="text/x-rst",
)
