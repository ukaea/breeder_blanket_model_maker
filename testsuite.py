
# these test cover the functionality of breeder blanket model maker

# to run type

# python -m pytest tests/testsuite.py
# python3 -m pytest tests/testsuite.py
# 
# coverage run tests/testsuite.py
# py.test --cov=neutronics_material_maker testsuite.py 

#  pytest --cov=./breeder_blanket_model_maker/tests/testsuite.py 

# requires pytest (pip install pytest)

import unittest

from module_tests import HCLL_tests
from module_tests import DCLL_tests
from module_tests import HCPB_tests
from module_tests import WCLL_tests

def main():
    unittest.TextTestRunner(verbosity=3).run(unittest.TestSuite())


if __name__ == '__main__':
    unittest.main()