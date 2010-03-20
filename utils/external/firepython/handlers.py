# -*- mode: python; coding: utf-8 -*-

from logging import Handler

__all__ = ['ThreadBufferedHandler']


threading_supported = False
try:
    import threading
    if threading:
        threading_supported = True
except ImportError:
    pass


class ThreadBufferedHandler(Handler):
    """ A logging handler that buffers records by thread. """

    def __init__(self):
        Handler.__init__(self)
        self.records = {} # dictionary (Thread -> list of records)
        self._enabled = {} # dictionary (Thread -> enabled/disabled)
        self.republished = {} # dictionary (Thread -> list of tuples (header_name, header_value) )

    def start(self, thread=None):
        if not thread and threading_supported:
            thread = threading.currentThread()
        self._enabled[thread] = True

    def finish(self, thread=None):
        if not thread and threading_supported:
            thread = threading.currentThread()
        self._enabled.pop(thread, None)

    def is_enabled(self, thread=None):
        if not thread and threading_supported:
            thread = threading.currentThread()
        return self._enabled.get(thread, False)

    def emit(self, record):
        """ Append the record to the buffer for the current thread. """
        if self.is_enabled():
            self.get_records().append(record)

    def get_records(self, thread=None):
        """
        Gets the log messages of the specified thread, or the current thread if
        no thread is specified.
        """
        if not thread and threading_supported:
            thread = threading.currentThread()
        if thread not in self.records:
            self.records[thread] = []
        return self.records[thread]

    def clear_records(self, thread=None):
        """
        Clears the log messages of the specified thread, or the current thread
        if no thread is specified.
        """
        if not thread and threading_supported:
            thread = threading.currentThread()
        if thread in self.records:
            del self.records[thread]

    def republish(self, headers):
        """ Appends republished firepython headers for the current thread. """
        if self.is_enabled():
            self.get_republished().extend(headers)

    def get_republished(self, thread=None):
        if not thread and threading_supported:
            thread = threading.currentThread()
        if thread not in self.republished:
            self.republished[thread] = []
        return self.republished[thread]

    def clear_republished(self, thread=None):
        if not thread and threading_supported:
            thread = threading.currentThread()
        if thread in self.republished:
            del self.republished[thread]
