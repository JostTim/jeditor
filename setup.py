# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 21:34:34 2023

@author: tjostmou
"""

from setuptools import setup, find_packages
from pathlib import Path 

def get_version(rel_path):
    here = Path(__file__).parent.absolute()
    with open(here.joinpath(rel_path), 'r') as fp:
        for line in fp.read().splitlines():
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError('Unable to find version string.')

setup(
    name= 'JEditor',
    version= get_version(Path('JEditor', '__init__.py')),
    packages=find_packages(),
    include_package_data=True,
    url= 'https://gitlab.pasteur.fr/haisslab/analysis-packages/Inflow',
    license= 'MIT',
    author= 'Timothé Jost-MOUSSEAU',
    author_email= 'timothe.jost-mousseau@pasteur.com',
    description= "JEditor is a Json nested parameters editor",
    #data_files=[("assets",['JEditor\\assets\\app_icon.ico','JEditor\\assets\\app_icon.svg','JEditor\\assets\\refresh_button.svg'])],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    install_requires=[
        "ONE-api @ git+https://gitlab.pasteur.fr/haisslab/data-management/ONE.git#egg=ONE-api"
        "PyQt5>=5.15",
        "pyqtspinner>=2.0",
        "qt_material>=2.14",
        "qtwidgets>=1.0",
        "requests>=2.28",
        "setuptools>=65.5",
    ],
    entry_points={
        'console_scripts': ['JEditor=JEditor:JEditor'],
    },
    scripts={},
)

