#!/usr/bin/env python

# Generate docs/options.html

import json
import glob
import re
import sys

# Set this to the path to a test file to get debug output for just that test
# file. Can be helpful to figure out why a test is not being shown for a
# particular option.
debug_tests = []  # [ 'tests/zoom.html' ]

# Pull options reference JSON out of dygraph.js
js = ''
in_json = False
for line in file('dygraph-options-reference.js'):
  if '<JSON>' in line:
    in_json = True
  elif '</JSON>' in line:
    in_json = False
  elif in_json:
    js += line

# TODO(danvk): better errors here.
assert js
docs = json.loads(js)

# Go through the tests and find uses of each option.
for opt in docs:
  docs[opt]['tests'] = []
  docs[opt]['gallery'] = []

# This is helpful for differentiating uses of options like 'width' and 'height'
# from appearances of identically-named options in CSS.
def find_braces(txt):
  """Really primitive method to find text inside of {..} braces.
  Doesn't work if there's an unmatched brace in a string, e.g. '{'. """
  out = ''
  level = 0
  for char in txt:
    if char == '{':
      level += 1
    if level >= 1:
      out += char
    if char == '}':
      level -= 1
  return out

def search_files(type, files):
  # Find text followed by a colon. These won't all be options, but those that
  # have the same name as a Dygraph option probably will be.
  prop_re = re.compile(r'\b([a-zA-Z0-9]+) *:')
  for test_file in files:
    text = file(test_file).read()
    # Hack for slipping past gallery demos that have title in their attributes
    # so they don't appear as reasons for the demo to have 'title' options.
    if type == "gallery":
      idx = text.find("function(")
      if idx >= 0:
        text = text[idx:]
    braced_html = find_braces(text)
    if debug_tests:
      print braced_html

    ms = re.findall(prop_re, braced_html)
    for opt in ms:
      if debug_tests: print '\n'.join(ms)
      if opt in docs and test_file not in docs[opt][type]:
        docs[opt][type].append(test_file)

search_files("tests", glob.glob("tests/*.html"))
search_files("gallery", glob.glob("gallery/*.js")) #TODO add grep "Gallery.register\("

if debug_tests: sys.exit(0)

# Extract a labels list.
labels = []
for nu, opt in docs.iteritems():
  for label in opt['labels']:
    if label not in labels:
      labels.append(label)

print """<!DOCTYPE HTML>
<html>
<head>
  <title>Dygraphs Options Reference</title>
  <link rel="stylesheet" href="style.css">
  <style type="text/css">
    p.option {
      padding-left: 25px;
    }
    div.parameters {
      padding-left: 15px;
    }
    #nav {
      position: fixed;
    }
    #content {
      max-width: 800px;
    }
  </style>
</head>
<body>
"""

print """
<div id='nav'>
<h2>Dygraphs</h2>
<ul>
  <li><a href="index.html">Home</a>
  <li><a href="data.html">Data Formats</a></li>
  <li><a href="annotations.html">Annotations</a></li>
</ul>
<h2>Options Reference</h2>
<ul>
  <li><a href="#usage">Usage</a>
"""
for label in sorted(labels):
  print '  <li><a href="#%s">%s</a>\n' % (label, label)
print '</ul>\n</div>\n\n'

print """
<div id='content'>
<h2>Options Reference</h2>
<p>Dygraphs tries to do a good job of displaying your data without any further configuration. But inevitably, you're going to want to tinker. Dygraphs provides a rich set of options for configuring its display and behavior.</p>

<a name="usage"></a><h3>Usage</h3>
<p>You specify options in the third parameter to the dygraphs constructor:</p>
<pre>g = new Dygraph(div,
                data,
                {
                  option1: value1,
                  option2: value2,
                  ...
                });
</pre>

<p>After you've created a Dygraph, you can change an option by calling the <code>updateOptions</code> method:</p>
<pre>g.updateOptions({
                  new_option1: value1,
                  new_option2: value2
                });
</pre>
<p>And, without further ado, here's the complete list of options:</p>
"""

def de_tests(f):
  """Takes 'tests/demo.html' -> 'demo'"""
  return f.replace('tests/', '').replace('.html', '')

def de_gallery(f):
  """Takes 'gallery/demo.js' -> 'demo'"""
  return f.replace('gallery/', '').replace('.js', '')

def urlify_gallery(f):
  """Takes 'gallery/demo.js' -> 'demo'"""
  return f.replace('gallery/', 'gallery/#g/').replace('.js', '')


for label in sorted(labels):
  print '<a name="%s"><h3>%s</h3>\n' % (label, label)

  for opt_name in sorted(docs.keys()):
    opt = docs[opt_name]
    if label not in opt['labels']: continue
    tests = opt['tests']
    if not tests:
      examples_html = '<font color=red>NONE</font>'
    else:
      examples_html = ' '.join(
        '<a href="%s">%s</a>' % (f, de_tests(f)) for f in tests)

    gallery = opt['gallery']
    if not gallery:
      gallery_html = '<font color=red>NONE</font>'
    else:
      gallery_html = ' '.join(
        '<a href="%s">%s</a>' % (urlify_gallery(f), de_gallery(f)) for f in gallery)

    if 'parameters' in opt:
      parameters = opt['parameters']
      parameters_html = '\n'.join("<i>%s</i>: %s<br/>" % (p[0], p[1]) for p in parameters)
      parameters_html = "\n  <div class='parameters'>\n%s</div>" % (parameters_html);
    else:
      parameters_html = ''

    if not opt['type']: opt['type'] = '(missing)'
    if not opt['default']: opt['default'] = '(missing)'
    if not opt['description']: opt['description'] = '(missing)'

    print """
  <div class='option'><a name="%(name)s"></a><b>%(name)s</b><br/>
  <p>%(desc)s</p>
  <i>Type: %(type)s</i><br/>%(parameters)s
  <i>Default: %(default)s</i></p>
  Gallery Samples: %(gallery_html)s<br/>
  Other Examples: %(examples_html)s<br/>
  <br/></div>
  """ % { 'name': opt_name,
          'type': opt['type'],
          'parameters': parameters_html,
          'default': opt['default'],
          'desc': opt['description'],
          'examples_html': examples_html,
          'gallery_html': gallery_html}


print """
<a name="point_properties"></a><h3>Point Properties</h3>
Some callbacks take a point argument. Its properties are:<br/>
<ul>
<li>xval/yval: The data coordinates of the point (with dates/times as millis since epoch)</li>
<li>canvasx/canvasy: The canvas coordinates at which the point is drawn.</li>
<li>name: The name of the data series to which the point belongs</li>
</ul>
</div>
</body>
</html>
"""

# This page was super-helpful:
# http://jsbeautifier.org/
