#!/usr/bin/python
import argparse
import logging
import sys
import unittest
import os

def main(sdk_path, test_path):
    logging.basicConfig(filename="testing.log", level=logging.DEBUG)
    sys.path.insert(0, os.path.abspath("."))
    sys.path.insert(0, sdk_path)
    import dev_appserver
    dev_appserver.fix_sys_path()
    suite = unittest.loader.TestLoader().discover(test_path)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    desc = "Run unit tests for App Engine apps."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-s", "--sdk_path", type=str,
                        default="/usr/local/google_appengine/",
                        help="Path to the SDK installation")
    parser.add_argument("-t", "--test_path", type=str,
                        default="tests",
                        help="Path to package containing test modules")
    args = parser.parse_args()

    main(args.sdk_path, args.test_path)
