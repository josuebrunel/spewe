import os
from setuptools import setup, find_packages

__author__ = 'Josue Kouka'
__email__ = 'josuebrunel@gmail.com'
__version__ = '0.1'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="spewe",
    version=__version__,
    description="Stupid Python Web Framework",
    long_description=read("README.rst"),
    author=__author__,
    author_email=__email__,
    url="https://github.com/josuebrunel/spewe",
    download_url="https://github.com/josuebrunel/spewe/archive/{0}.tar.gz".format(__version__),
    keywords=['web', 'framework', 'wsgi'],
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License'
    ],
    platforms=['Any'],
    license='MIT',
)
