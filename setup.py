from setuptools import setup, find_packages
import sys, os

setup(name='Allanon',
      # scripts=['src/allanon',],
      version=open(os.path.join("src", "allanon", "version.txt")).read(),
      description="A crawler for visit a predictable set of URLs, "
                  "and download resources from them",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=["Development Status :: 3 - Alpha",
                   "License :: OSI Approved :: GNU General Public License (GPL)",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Utilities",
                   "Topic :: System :: Shells",
                   "Topic :: Internet :: WWW/HTTP",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2.7",
                   ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='crawler robot spider downloader parser',
      author='keul',
      author_email='luca@keul.it',
      url='https://github.com/keul/Allanon',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup',]),
      #py_modules=['allanon',],
      package_dir = {'': 'src'},
      include_package_data=True,
      #package_data={'': ['example_profile.cfg', ]},
      #data_files=[('profiles', ['src/example_profile.cfg'])],
      tests_require=['nose', 'httpretty',],
      setup_requires=['nose>=1.0'],
      test_suite="nose.collector",
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pyquery',
          'requests>=1.0.0',
      ],
      entry_points={'console_scripts': ['allanon = allanon.main:main', ]}
      )

