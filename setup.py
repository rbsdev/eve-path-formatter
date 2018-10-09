from os import path

from setuptools import setup, find_packages

__version__ = "0.0.0"
__repo__ = "https://github.com/rbsdev/eve-path-formatter.git"

install_requires = [
    "Eve>=0.8,<0.9",
]


def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()


setup(
    name="eve-path-formatter",
    version=__version__,
    install_requires=install_requires,
    packages=find_packages(exclude=["tests", "tests.*"]),
    py_modules=["eve_path_formatter"],
    url=__repo__,
    download_url="{}/tarball/{}".format(__repo__, __version__),
    include_package_data=True,
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    exclude_package_data={'': ['README.md']},
)
