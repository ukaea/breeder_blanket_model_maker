
# install with this command
# sudo python setup.py install --force
# test with this command
# sudo python setup.py test
# export PYTHONPATH=/media/jshim/Data/neutronics_material_maker/
# pytest

from setuptools import setup

#with open('requirements.txt') as test_reqs_txt:
#    requirements = [line for line in test_reqs_txt]


setup(name='breeder_blanket_model_maker',
      version='0.002',
      summary='Package for making 3D parametric breeder blanket models',
      description='Input blanket envelopes and retrive detailed blanket geometry',
      url='https://github.com/ukaea/breeder_blanket_model_maker',
      author='Jonathan Shimwell',
      author_email='jonathan.shimwell@ukaea.uk',
      license='Apache 2.0',
      packages=['breeder_blanket_model_maker','examples'],
      test_suite='testsuite', # works in python 2
      #test_suite='tests.testsuite', # does not work within a folder in python 2
      zip_safe=True,
      package_data={'':['requirements.txt', 'README.md','README.md.html', 'LICENSE','sample_envelope_1.step','sample_envelope_2.step']},
      #install_requires=requirements,
      #setup_requires=['pytest-runner'],
      tests_require=['pytest']
      )

