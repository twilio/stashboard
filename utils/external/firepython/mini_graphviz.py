import sys
import optparse
import tempfile
import subprocess

__all__ = [
    'main',
]

DEFAULT_DOT = 'dot'
DEFAULT_VIEWER = 'eog'
USAGE = "%prog [options]"
OPTIONS = (
    (('-D', '--dot-exe'),
        dict(dest='dot', action='store', default=DEFAULT_DOT,
             help='dot executable to use for making png, '
                  'default=%r' % DEFAULT_DOT)),
    (('-V', '--viewer'),
        dict(dest='viewer', action='store', default=DEFAULT_VIEWER,
             help='viewer with which to open resulting png, '
                  'default=%r' % DEFAULT_VIEWER)),
)


def main(sysargs=sys.argv[:]):
    parser = get_option_parser()
    opts, targets = parser.parse_args(sysargs[1:])

    for target in targets:
        graphviz = MiniGraphviz(dot=opts.dot, viewer=opts.viewer)
        graphviz.view_as_png(target)

    return 0


def get_option_parser():
    parser = optparse.OptionParser(usage=USAGE)
    for args, kwargs in OPTIONS:
        parser.add_option(*args, **kwargs)
    return parser


class MiniGraphviz(object):

    def __init__(self, dot=DEFAULT_DOT, viewer=DEFAULT_VIEWER):
        self.dot = dot
        self.viewer = viewer

    def view_as_png(self, dot_input_file):
        png_maker = Dot2PngMaker(dot_input_file, dot=self.dot)
        png_path = png_maker.get_png()
        self._open_png_with_viewer(png_path)
        return png_path

    def _open_png_with_viewer(self, png_path):
        if self.viewer:
            cmd = [self.viewer, png_path]
            subprocess.call(cmd)


class Dot2PngMaker(object):
    _tempfile = ''

    def __init__(self, dot_input_file, dot=DEFAULT_DOT):
        self.dot_input_file = dot_input_file
        self.dot = dot

    def get_png(self):
        self._get_tempfile()
        self._get_png_from_dot()
        return self._tempfile

    def _get_tempfile(self):
        self._tempfile = tempfile.mkstemp('.png', __name__)[1]

    def _get_png_from_dot(self):
        cmd = [self.dot, '-T', 'png', '-o', self._tempfile,
               self.dot_input_file]
        subprocess.call(cmd)


if __name__ == '__main__':
    sys.exit(main())

# vim:filetype=python
