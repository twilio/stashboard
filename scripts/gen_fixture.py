# Copyright (c) 2010 Twilio Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Requires Python 2.7

import argparse
import os
import json

# List of supported icon sets
# These sets live in stashboard/static/images/icons
ICON_SETS = ["fugue", "iconic"]

parser = argparse.ArgumentParser(description="")
parser.add_argument("directory", type=str,
                    help="Stashboard image directory")
args = parser.parse_args()

# Icons path
icons = os.path.join(args.directory, "icons")

image_set = set()
images = []

for p in os.listdir(icons):
    if p in ICON_SETS:
        for i in os.listdir(os.path.join(icons, p)):
            if i[0] != '.': #ignore hidden files
                filename, ext = os.path.splitext(i)
                if filename in image_set:
                    name = filename + "_alt"
                else:
                    name = filename

                image_set.add(name)
                image = {
                    "name": name,
                    "set": p,
                    "url": os.path.join("icons", p, i),
                    }
                images.append(image)

print json.dumps(images, indent=4)









