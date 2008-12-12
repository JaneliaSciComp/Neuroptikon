#!/usr/bin/env python
# -*- coding: ascii -*-

import sys
from distutils.core import setup
python_version = sys.version_info[:2]

the_url = 'http://www.lexicon.net/sjmachin/xlrd.htm'

def mkargs(**kwargs):
    return kwargs

args = mkargs(
      name = 'xlrd',
      version = '0.6.0a1',
      author = 'John Machin',
      author_email = 'sjmachin@lexicon.net',
      url = the_url,
      packages = ['xlrd'],
      scripts = ['scripts/runxlrd.py'],
      description = 'Library for developers to extract data from Microsoft Excel (tm) spreadsheet files',
      long_description = \
            "Extract data from new and old Excel spreadsheets on any platform. " \
            "Pure Python (2.1 or later). Strong support for Excel dates. Unicode-aware.",
      platforms = ["Any platform -- don't need Windows"],
      license = 'BSD',
      keywords = ['xls', 'excel', 'spreadsheet', 'workbook'],
      )
      
if python_version >= (2, 3):      
    args23 = mkargs(      
        download_url = the_url,
        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Operating System :: OS Independent',
            'Topic :: Database',
            'Topic :: Office/Business',
            'Topic :: Software Development :: Libraries :: Python Modules',      
            ],
          )
    args.update(args23)

if python_version >= (2, 4):      
    args24 = mkargs(      
        package_data={'xlrd': ['doc/*.htm*', 'doc/*.txt']},
          )
    args.update(args24)


setup(**args)

