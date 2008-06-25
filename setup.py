from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='plone.supermodel',
      version=version,
      description="Integration layer making it possible to load schema definitions from XML",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone XML schema',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://plone.org',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'grokcore.component',
          # -*- Extra requirements: -*-

          # 'zope.component',
          # 'zope.schema',
          # 'elementtree',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
