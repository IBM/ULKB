import re
from setuptools import setup, find_packages

with open('Makefile.conf') as fp:
    text = fp.read()
    PACKAGE, = re.findall(r'PACKAGE\s*=\s*(.*)', text)
    DESCRIPTION = re.findall(r'DESCRIPTION\s*=\s*(.*)', text)
    URL = re.findall(r'URL\s*=\s*(.*)', text)
    LICENSE = re.findall(r'LICENSE\s*=\s*(.*)', text)

with open(f'{PACKAGE}/__init__.py') as fp:
    text = fp.read()
    VERSION, = re.findall(r"__version__\s*=\s*'(.*)'", text)

setup(
    name=PACKAGE,
    version=VERSION,
    description=DESCRIPTION,
    url=URL,
    platforms='any',
    python_requires='>=3.9',
    packages=find_packages(exclude=('tests', 'tests.*')),
    #package_data={PACKAGE: ['py.typed']},
    include_package_data=True,
    install_requires=[
        'lark',
        'more_itertools',
        'rdflib',
        'setuptools',
        'z3-solver',
    ],
    extras_require={
        'docs': [
            'myst_parser',
            'pydata_sphinx_theme',
        ],
        'tests': [
            'flake8',
            'isort',
            'mypy',
            'pytest',
            'pytest-cov',
            'pytest-mypy',
            'tox',
        ],
    },
)
