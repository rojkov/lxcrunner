import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "lxcrunner",
    version = "1.1.0",
    author = "Dmitry Rozhkov",
    author_email = "dmitry.rojkov@gmail.com",
    description = ("Helpers to run scripts inside dynamicly created LXC containers."),
    license = "BSD",
    keywords = "virtualization",
    packages=['lxcrunner'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    entry_points={
        'console_scripts':
            [
                'lxcrunner = lxcrunner.cli:main',
            ],
    },
    test_suite = "tests"
)
