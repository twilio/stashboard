#!/usr/bin/python
import argparse
import logging
import sys
import unittest
import os
import nose

SDK_PATH = "/usr/local/google_appengine/"

def main():
    #logging.basicConfig(level=logging.DEBUG)
    sys.path.insert(0, SDK_PATH)
    sys.path.insert(0, "stashboard")
    import dev_appserver
    dev_appserver.fix_sys_path()
    nose.main()


if __name__ == '__main__':
    main()
