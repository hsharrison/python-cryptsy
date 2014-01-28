#!/usr/bin/env python

from distutils.core import setup


setup(name='python-cryptsy',
      version='0.1.0',
      packages=['cryptsy'],
      modules=[
          'cryptsy.public',
          'cryptsy.private',
          'cryptsy.bterapi',
      ],
      description='Python bindings for cryptsy.com API.',
      author='Henry S. Harrison',
      author_email='henry.schafer.harrison@gmail.com',
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: MIT License',
          'Development Status :: 3 - Alpha',
          'Topic :: Office/Business :: Financial',
      ])