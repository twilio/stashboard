# The MIT License
# 
# Copyright (c) 2008 William T. Katz
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

import string
import re
import logging

from external.BeautifulSoup import BeautifulSoup
from utils import sanitizer

language_jsfiles = {
    'python': 'Python',
    'ruby': 'Ruby',
    'js': 'JScript',
    'html': 'Xml',
    'php': 'Php',
    'css': 'Css',
    'cpp': 'Cpp'
}

def process_html(html):
    """Processes HTML for embedded code using SyntaxHighlighter
    
    Determines languages used by checking class attribute of pre tags
    with name="code".

    Args:
      html: HTML to be processed for embedded code

    Returns:
      The modified html and a list of strings giving the embedded
      code languages.
    """
    code_tag = re.compile('\s*<pre name="code" class="([^"]+)">', 
                          re.MULTILINE)
    languages = set([])
    soup = BeautifulSoup(html)
    clean_html = ''
    for section in soup.contents:
        txt = str(section)
        matchobj = re.match(code_tag, txt)
        if matchobj:
            languages.add(matchobj.group(1))
            clean_html += re.sub(r'<br />', "\n", txt)
        else:
            clean_html += txt
            
    # Map the language class names to the spelling for javascript files
    list_language_files = [language_jsfiles[lang] for lang in list(languages)]
    return clean_html.decode('utf-8'), list_language_files

