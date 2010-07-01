import subprocess 
import os

def convert(name, filename):
    
    markdown = subprocess.Popen(["/Users/kyleconroy/.cabal/bin/pandoc", filename],stdout=subprocess.PIPE).communicate()[0]
    f = open("/Users/kyleconroy/twilio/ismywebservicedown/views/default/%s.html" % name, 'w')
    print >>f, "{% extends \"documentation.html\" %}"
    print >>f, "{% block document %}"
    print >>f, markdown
    print >>f, "{% endblock %}"
    f.close()

if __name__ == '__main__':
    files = ["examples", "restapi", "overview"]
    for f in files:
        convert(f, os.path.abspath("%s.markdown" % f))
