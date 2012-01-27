import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "lxcrunner",
    version = "0.0.4",
    author = "Dmitry Rozhkov",
    author_email = "dmitry.rojkov@gmail.com",
    description = ("Helpers for setting up a virtual test environment."),
    license = "GPL",
    keywords = "virtualization",
    packages=['lxcrunner'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GPL License",
    ],
    entry_points={
        'console_scripts':
            [
                'lxcrunner = lxcrunner.cli:main',
            ],
    },
    test_suite = "tests"
)
