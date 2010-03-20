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

import logging
import string
import re

from external.BeautifulSoup import BeautifulSoup, Comment

acceptable_tags = ['a', 'abbr', 'acronym', 'address', 'area', 'b', 'big',
  'blockquote', 'br', 'button', 'caption', 'center', 'cite', 'code',    
  'col', 'colgroup', 'dd', 'del', 'dfn', 'dir', 'div', 'dl', 'dt', 'em', 
  'fieldset', 'font', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 
  'i', 'img', 'input', 'ins', 'kbd', 'label', 'legend', 'li', 'map', 
  'menu', 'ol', 'optgroup', 'option', 'p', 'pre', 'q', 's', 'samp', 
  'select', 'small', 'span', 'strike', 'strong', 'sub', 'sup', 'table', 
  'tbody', 'td', 'textarea', 'tfoot', 'th', 'thead', 'tr', 'tt', 'u', 
  'ul', 'var']

acceptable_attributes = ['abbr', 'accept', 'accept-charset', 'accesskey',
  'action', 'align', 'alt', 'axis', 'border', 'cellpadding', 
  'cellspacing', 'char', 'charoff', 'charset', 'checked', 'cite', 'class', 
  'clear', 'cols', 'colspan', 'color', 'compact', 'coords', 'datetime', 
  'dir', 'disabled', 'enctype', 'for', 'frame', 'headers', 'height', 
  'href', 'hreflang', 'hspace', 'id', 'ismap', 'label', 'lang', 
  'longdesc', 'maxlength', 'media', 'method', 'multiple', 'name', 
  'nohref', 'noshade', 'nowrap', 'prompt', 'readonly', 'rel', 'rev', 
  'rows', 'rowspan', 'rules', 'scope', 'selected', 'shape', 'size',
  'span', 'src', 'start', 'summary', 'tabindex', 'target', 'title', 
  'type', 'usemap', 'valign', 'value', 'vspace', 'width']

tags_for_trusted_source = ['object', 'param', 'embed', 'style']
attributes_for_trusted_source = ['style', 'wmode']

danger_elements = ['script', 'applet']
js_possible_attributes = ['href', 'src']

href_matcher = re.compile("^https?://", re.IGNORECASE)
javascript_matcher = re.compile("javascript:", re.IGNORECASE | re.MULTILINE)

class DangerousHTMLError(Exception):
    def __init__(self, value):
        self.value = chop_up(value)  # Even when logging, could be displayed
    def __str__(self):
        return ' ~ '.join(self.value)

def sanitize_html(html='<p>No comment</p>', encoding=None,
                  allow_tags=[], allow_attributes=[],
                  blacklist_tags=[], blacklist_attributes=[],
                  trusted_source=False):
    """Parses HTML and tries to sanitize it using white list.
    
    This method is a mishmash of code from Django snippets
    (http://www.djangosnippets.org/snippets/169) and the
    HTML sanitization of Universal Feed Parser.  It explicitly
    looks for valid hrefs to prevent scripts lurking in there.
    Unfortunately, style, either as a tag or attribute, can
    contain malicious script through executable CSS definitions.
    So sanitized HTML cannot be colored or highlighted using styles.

    Args:
      html: HTML to be sanitized.
      allow_tags: limit all tags to just this list
      allow_attributes: limit all tags to just this list
      allow_styling: should only be TRUE if you trust source

    Returns:
      Sanitized version of html

    Raises:
      DangerousHTMLError if the supplied HTML has dangerous elements.
    """
    if not allow_tags:
        allow_tags = acceptable_tags
    if not allow_attributes:
        allow_attributes = acceptable_attributes
    allow_tags = [tag for tag in allow_tags if tag not in blacklist_tags]
    allow_attributes = [tag for tag in allow_attributes 
                        if tag not in blacklist_tags]
    if trusted_source:
        allow_attributes += attributes_for_trusted_source
        allow_tags += tags_for_trusted_source

    if isinstance(html, unicode) and not encoding:
        logging.debug("Sanitizing unicode input.")
        soup = BeautifulSoup(html,  
                            convertEntities=BeautifulSoup.XHTML_ENTITIES)
    else:
        if not encoding:
            encoding = 'latin-1'
        logging.debug("Sanitizing string input, assuming %s", encoding)
        soup = BeautifulSoup(html.decode(encoding, 'ignore'),
                             convertEntities=BeautifulSoup.XHTML_ENTITIES)
    for comment in soup.findAll(
                    text = lambda text: isinstance(text, Comment)):
        comment.extract()
    for tag in soup.findAll(True):
        if tag.name not in allow_tags:
            tag.hidden = True
            if tag.name in danger_elements:
                raise DangerousHTMLError(html)
        ok_attrs = []
        for attr, val in tag.attrs:
            if attr == 'href' and not href_matcher.match(val) and not trusted_source:
                continue
            if attr in allow_attributes:
                if attr in js_possible_attributes:
                    if javascript_matcher.match(val):
                        raise DangerousHTMLError(html)
                ok_attrs += [(attr, val)]
        tag.attrs = ok_attrs
    return soup.renderContents().decode('utf-8')

def chop_up(text, chop_size=5):
    "Returns a list of smaller chunks of text"
    chars = len(text)
    blocks = chars / chop_size
    if chars % chop_size:
        blocks += 1
    return [text[i*chop_size:min(chars,(i+1)*chop_size)] 
            for i in xrange(0, blocks)]
