# -*- mode: python; coding: utf-8 -*-

import os
import sys
import time
import random
import logging
import traceback

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import jsonpickle

try:
    import gprof2dot
except ImportError:
    gprof2dot = None

import firepython
import firepython.utils
import firepython._const as CONST
from firepython.handlers import ThreadBufferedHandler

__all__ = [
    'FirePythonBase',
    'FirePythonDjango',
    'FirePythonWSGI',
    'paste_filter_factory',
]


# add a new backed jsonpickle for Django
# jsonpickle will attempt to import this if default
# jsonpickle libraries are not present
jsonpickle.load_backend('django.utils.simplejson', 'dumps',
                        'loads', ValueError)

class FirePythonBase(object):

    def __init__(self):
        raise NotImplementedError("Must be subclassed")

    def install_handler(self):
        logger = logging.getLogger(self._logger_name)
        self._handler = ThreadBufferedHandler()
        logger.addHandler(self._handler)

    def uninstall_handler(self):
        if self._handler is None:
            return
        logger = logging.getLogger(self._logger_name)
        logger.removeHandler(self._handler)
        self._handler = None

    def _version_check(self, version_header):
        firelogger_api_version = version_header.strip()
        if firelogger_api_version == '':
            logging.info('FireLogger not detected')
            return False
        if firepython.__api_version__ != firelogger_api_version:
            self._client_message += (
                'Warning: FireLogger (client) has version %s, but '
                'FirePython (server) is %s. ' % (firelogger_api_version,
                                                 firepython.__api_version__)
            )
            logging.warning('FireLogger has version %s, but FirePython '
                            '(server) is version %s', firelogger_api_version,
                            firepython.__api_version__)
        return True

    def _password_check(self, token):
        if self._password is None:
            raise Exception("self._password must be set!")
        if not firepython.utils.get_auth_token(self._password) == token:
            self._client_message += 'FireLogger password does not match. '
            logging.warning('FireLogger password does not match. Logging output won\'t be sent to FireLogger. Double check your settings!')
            return False
        return True

    def _appengine_check(self):
        if 'google.appengine' not in sys.modules:
            return True  # Definitely not running under Google App Engine
        try:
            from google.appengine.api import users
        except ImportError:
            return True  # Apparently not running under Google App Engine
        if os.getenv('SERVER_SOFTWARE', '').startswith('Dev'):
            return True  # Running in SDK dev_appserver
        # Running in production, only allow admin users
        if not users.is_current_user_admin():
            self._client_message += 'Security: Log in as a project administrator to see FirePython logs (App Engine in production mode). '
            logging.warning('Security: Log in as a project administrator to see FirePython logs (App Engine in production mode)')
            return False
        return True

    def _check(self, env):
        self._client_message = ''
        self._profile_enabled = \
            env.get(CONST.FIRELOGGER_PROFILER_ENABLED_HEADER, '') != ''
        self._appstats_enabled = \
            env.get(CONST.FIRELOGGER_APPSTATS_ENABLED_HEADER, '') != ''
        if self._check_agent and not self._version_check(
            env.get(CONST.FIRELOGGER_VERSION_HEADER, '')):
            return False
        if ((self._password and not
              self._password_check(
                env.get(CONST.FIRELOGGER_AUTH_HEADER, '')))):
            return False
        # If _password is set, skip _appengine_check()
        if (not self._password and not self._appengine_check()):
            return False
        return True

    def _sanitize_exc_info(self, exc_info):
        if exc_info == None:
            return ("?", "No exception info available", [])
        exc_type = exc_info[0]
        exc_value = exc_info[1]
        exc_traceback = exc_info[2]
        if exc_traceback is not None:
            exc_traceback = traceback.extract_tb(exc_traceback)
        return (exc_type, exc_value, exc_traceback)

    def _handle_internal_exception(self, e):
        if CONST.RAZOR_MODE: # in razor mode hurt web server
            raise e
        # in non-razor mode report internal error to firepython addon
        exc_info = self._sanitize_exc_info(sys.exc_info())
        return {"message": "Internal FirePython error: %s" % unicode(e),
                "exc_info": exc_info}

    def _encode(self, logs, errors=None, profile=None, extension_data=None):
        data = {"logs": logs}
        if errors:
            data['errors'] = errors
        if profile:
            data['profile'] = profile
        if extension_data:
            data['extension_data'] = extension_data
        try:
            data = jsonpickle.encode(data, unpicklable=False,
                                     max_depth=CONST.JSONPICKLE_DEPTH)
        except Exception, e:
            # this exception may be fired, because of buggy __repr__ or
            # __str__ implementations on various objects
            errors = [self._handle_internal_exception(e)]
            try:
                data = jsonpickle.encode({"errors": errors },
                                         unpicklable=False,
                                         max_depth=CONST.JSONPICKLE_DEPTH)
            except Exception, e:
                # even unable to serialize error message
                data = jsonpickle.encode(
                        {"errors": {
                            "message": "FirePython has a really bad day :-("
                        }
                    },
                    unpicklable=False,
                    max_depth=CONST.JSONPICKLE_DEPTH
                )
        data = data.encode('utf-8')
        data = data.encode('base64')
        return data.splitlines()

    def republish(self, headers):
        firelogger_headers = []
        for key, value in headers.iteritems():
            if CONST.FIRELOGGER_RESPONSE_HEADER.match(key):
                firelogger_headers.append((key, value))

        self._handler.republish(firelogger_headers)

    def _flush_records(self, add_header, profile=None, extension_data=None):
        """
        Flush collected logs into response.

        Argument ``add_header`` should be a function receiving two arguments:
        ``name`` and ``value`` of header.
        """

        records = self._handler.get_records()
        self._handler.clear_records()
        republished = self._handler.get_republished()
        self._handler.clear_republished()

        for name, value in republished:
            add_header(name, value)

        logs = []
        errors = []
        for record in records:
            try:
                logs.append(self._prepare_log_record(record))
            except Exception, e:
                # this exception may be fired, because of buggy __repr__ or
                # __str__ implementations on various objects
                errors.append(self._handle_internal_exception(e))

        chunks = self._encode(logs, errors, profile, extension_data)
        guid = "%08x" % random.randint(0, 0xFFFFFFFF)
        for i, chunk in enumerate(chunks):
            add_header(CONST.FIRELOGGER_HEADER_FORMAT %
                       dict(guid=guid, identity=i), chunk)

    def _prepare_log_record(self, record):
        data = {
            "level": self._log_level(record.levelno),
            "message": self._handler.format(record),
            "template": record.msg,
            "timestamp": long(record.created * 1000 * 1000),
            "time": (time.strftime("%H:%M:%S",
                     time.localtime(record.created)) +
                (".%03d" % ((record.created - long(record.created)) * 1000))
            )
        }
        props = ["args", "pathname", "lineno", "exc_text", "name", "process",
                 "thread", "threadName"]
        for p in props:
            try:
                data[p] = getattr(record, p)
            except AttributeError:
                pass

        try:
            exc_info = getattr(record, 'exc_info')
            if exc_info is not None:
                data['exc_info'] = self._sanitize_exc_info(exc_info)

                frames = []
                t = exc_info[2]
                while t:
                    try:
                        d = {}
                        for k,v in t.tb_frame.f_locals.iteritems():
                            if CONST.DEEP_LOCALS:
                                d[unicode(k)] = v
                            else:
                                d[unicode(k)] = repr(v)
                        frames.append(d)
                    except:
                        frames.append('?')
                    t = t.tb_next
                data['exc_frames'] = frames
        except AttributeError:
            pass
        return data

    def _log_level(self, level):
        if level >= logging.CRITICAL:
            return "critical"
        elif level >= logging.ERROR:
            return "error"
        elif level >= logging.WARNING:
            return "warning"
        elif level >= logging.INFO:
            return "info"
        else:
            return "debug"

    def _start(self):
        self._handler.start()

    def _finish(self):
        self._handler.finish()

    def _profile_wrap(self, func):
        '''If the FIRELOGGER_RESPONSE_HEADER header has been passed with a
        request, given function will be wrapped with a profile.
        '''
        if not self._profile_enabled:
            return func
        try:
            import cProfile as profile
        except ImportError:
            import profile
        self._prof = profile.Profile()
        def prof_wrapper(*args, **kwargs):
            return self._prof.runcall(func, *args, **kwargs)
        return prof_wrapper

    def _prepare_profile(self):
        """Prepares profiling information."""
        if not self._profile_enabled or not hasattr(self, '_prof'):
            return None

        if not gprof2dot:
            logging.warn('failed to import ``gprof2dot``, will not profile')
            return None

        self._prof.create_stats()
        parser = gprof2dot.PstatsParser(self._prof)

        def get_function_name((filename, line, name)):
            module = os.path.splitext(filename)[0]
            module_pieces = module.split(os.path.sep)
            return "%s:%d:%s" % ("/".join(module_pieces[-4:]), line, name)

        parser.get_function_name = get_function_name
        output = StringIO()
        gprof = parser.parse()

        gprof.prune(0.005, 0.001)
                # TODO: ^--- Parameterize node and edge thresholds.
        dot = gprof2dot.DotWriter(output)
        theme = gprof2dot.TEMPERATURE_COLORMAP
        theme.bgcolor = (0.0, 0.0, 0.0)
                        # ^--- Use black text, for less eye-bleeding.
        dot.graph(gprof, theme)

        def get_info(self):
            s = "Profile Graph:"
            s += " %.3fs CPU" % self.total_tt
            s += ": %d function calls" % self.total_calls
            if self.total_calls != self.prim_calls:
                s += " (%d primitive calls)" % self.prim_calls
            return s

        profile = {
          "producer": "gprof2dot",
          "producerVersion": str(gprof2dot.__version__),
          "info": get_info(parser.stats),
          "dot": output.getvalue(),
        }

        return profile


class FirePythonDjango(FirePythonBase):
    """
    Django middleware to enable FirePython logging.

    To use add 'firepython.middleware.FirePythonDjango' to your
    MIDDLEWARE_CLASSES setting.

    Optional settings:

     - ``FIREPYTHON_PASSWORD``: password to protect your logs
     - ``FIREPYTHON_LOGGER_NAME``: specific logger name you want to monitor
     - ``FIREPYTHON_CHECK_AGENT``: set to False for prevent server to check
       presence of firepython in user-agent HTTP header.
    """

    def __init__(self):
        from django.conf import settings
        self._password = getattr(settings, 'FIREPYTHON_PASSWORD', None)
        self._logger_name = getattr(settings, 'FIREPYTHON_LOGGER_NAME', None)
        self._check_agent = getattr(settings, 'FIREPYTHON_CHECK_AGENT', True)
        self.install_handler()

    def __del__(self):
        self.uninstall_handler()

    def process_request(self, request):
        if not self._check(request.META):
            return

        self._start()
        # Make set_extension_data available via the request object.
        self._extension_data = {}
        if self._appstats_enabled:
            request.firepython_appstats_enabled = True
        request.firepython_set_extension_data = self._extension_data.__setitem__

    def process_view(self, request, callback, callback_args, callback_kwargs):
        args = (request, ) + callback_args
        return self._profile_wrap(callback)(*args, **callback_kwargs)

    def process_response(self, request, response):
        check = self._check(request.META)
        if self._client_message:
            response.__setitem__(CONST.FIRELOGGER_MESSAGE_HEADER,
                                 self._client_message)
        if not check:
            return response
            
        profile = self._prepare_profile()
        self._finish()
        self._flush_records(response.__setitem__, profile, self._extension_data)
        return response

    def process_exception(self, request, exception):
        if not self._check(request.META):
            return

        logging.exception(exception)


class FirePythonWSGI(FirePythonBase):
    """
    WSGI middleware to enable FirePython logging.

    Supply an application object and an optional password to enable password
    protection. Also logger name may be specified.
    """
    def __init__(self, app, password=None, logger_name=None, check_agent=True):
        self.app = app
        self._password = password
        self._logger_name = logger_name
        self._check_agent = check_agent
        self.install_handler()

    def __del__(self):
        self.uninstall_handler()

    def __call__(self, environ, start_response):
        check = self._check(environ)
        if not check and not self._client_message:
            return self.app(environ, start_response) # a quick path

        # firepython is enabled or we have a client message we want to communicate in headers
        client_message = self._client_message

        # asking why? see __ref_pymod_counter__
        closure = ["200 OK", [], None]
        extension_data = {}  # Collect extension data here
        sio = StringIO()
        def faked_start_response(_status, _headers, _exc_info=None):
            closure[0] = _status
            closure[1] = _headers
            closure[2] = _exc_info
            if client_message:
                closure[1].append(
                    (CONST.FIRELOGGER_MESSAGE_HEADER, client_message))
            return sio.write

        def add_header(name, value):
            closure[1].append((name, value))

        if self._appstats_enabled:
            environ['firepython.appstats_enabled'] = True
            
        if check: 
            self._start()
            environ['firepython.set_extension_data'] = extension_data.__setitem__
            
        # run app
        try:
            # the nested try-except block within
            # a try-finally block is so that we stay
            # python2.3 compatible
            try:
                app = self.app
                if check:
                    app = self._profile_wrap(app)
                app_iter = app(environ, faked_start_response)
                output = list(app_iter)
            except:
                logging.warning("DeprecationWarning: raising a "
                                "string exception is deprecated")
                logging.exception(sys.exc_info()[0])
                raise
        finally:
            # Output the profile first, so we can see any errors in profiling.
            if check: 
                profile = self._prepare_profile()
                self._finish()
                self._flush_records(add_header, profile, extension_data)

        # start responding
        write = start_response(*closure)
        if sio.tell(): # position is not 0
            sio.seek(0)
            write(sio.read())
        # return output
        return output


def paste_filter_factory(global_conf, password_file='', logger_name='',
                         check_agent='true'):
    from paste.deploy.converters import asbool

    check_agent = asbool(check_agent)
    get_password = lambda: ''
    if password_file:
        def get_password():
            return open(password_file).read().strip()

    def with_firepython_middleware(app):
        return FirePythonWSGI(app, password=get_password(),
                              logger_name=logger_name,
                              check_agent=check_agent)
    return with_firepython_middleware


__ref_pymod_counter__ = \
"http://jjinux.blogspot.com/2006/10/python-modifying-counter-in-closure.html"
