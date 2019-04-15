from setuptools import setup

setup(name='bb84',
      version='0.1',
      description='a basic implementation of the BB84 QKD protocol',
      author='Eric Zheng',
      author_email='ericzheng@cmu.edu',
      license='GPL',
      packages=['bb84'],
      install_requires=['numpy'],
      test_suite='bb84.tests',
      tests_require=['numpy'],
      zip_safe=False)

