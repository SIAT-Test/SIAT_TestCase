import os
import unittest

if __name__ == '__main__':
    suite = unittest.TestSuite()
    testCase = unittest.defaultTestLoader.discover(
        start_dir=os.getcwd()+"\database\dataManager",
        pattern='*.py')
    suite.addTest(testCase)
    unittest.TextTestRunner().run(suite)

