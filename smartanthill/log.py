# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import sys
import traceback

from twisted.python import log
from twisted.python.constants import FlagConstant, Flags

from smartanthill.configprocessor import ConfigProcessor


class Level(Flags):

    FATAL = FlagConstant()
    ERROR = FlagConstant()
    WARN = FlagConstant()
    INFO = FlagConstant()
    DEBUG = FlagConstant()


class Logger(object):

    def __init__(self, system="-"):
        self.system = system
        self._level = Level.INFO

        try:
            self.set_level(Level.lookupByName(
                ConfigProcessor().get("logger.level")))
        except ValueError:  # pragma: no cover
            pass

    def set_level(self, level):
        assert isinstance(level, FlagConstant)
        self._level = level

    def fatal(self, *msg, **kwargs):
        kwargs['_salevel'] = Level.FATAL
        self._emit(*msg, **kwargs)
        sys.exit()

    def error(self, *msg, **kwargs):
        kwargs['_salevel'] = Level.ERROR
        self._emit(*msg, **kwargs)

    def warn(self, *msg, **kwargs):
        kwargs['_salevel'] = Level.WARN
        self._emit(*msg, **kwargs)

    def info(self, *msg, **kwargs):
        kwargs['_salevel'] = Level.INFO
        self._emit(*msg, **kwargs)

    def debug(self, *msg, **kwargs):
        kwargs['_salevel'] = Level.DEBUG
        self._emit(*msg, **kwargs)

    def _emit(self, *msg, **kwargs):
        _system = self.system
        if kwargs['_salevel'].value > self._level.value:
            return
        elif kwargs['_salevel'] != Level.INFO:
            _system = "%s#%s" % (_system, kwargs['_salevel'].name.lower())

        params = dict(system=_system)
        params.update(kwargs)
        if kwargs['_salevel'] == Level.FATAL:
            log.err(*msg, **params)
            if ("_satraceback" not in kwargs or
                    kwargs['_satraceback']):  # pragma: no cover
                traceback.print_stack()
        elif kwargs['_salevel'] == Level.ERROR:
            log.err(*msg, **params)
        else:
            log.msg(*msg, **params)


class Console(object):

    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self._messages = []
        log.addObserver(self.on_emit)

    def get_messages(self):
        return self._messages

    def on_emit(self, data):
        level = data['_salevel'].name if "_salevel" in data else None
        self._messages.append(
            (data['message'], data['system'].split("#")[0], level)
        )
