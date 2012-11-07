#!/usr/bin/python
import sys
import nose
import os

SDK_PATH = os.environ.get("APPENGINE_SDK", "/usr/local/google_appengine/")

def main():
    #logging.basicConfig(level=logging.DEBUG)
    sys.path.insert(0, SDK_PATH)
    sys.path.insert(0, "stashboard")
    sys.path.insert(0, "stashboard/contrib")
    import dev_appserver
    dev_appserver.fix_sys_path()
    nose.main()

if __name__ == '__main__':
    main()
