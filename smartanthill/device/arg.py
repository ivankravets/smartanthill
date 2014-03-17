# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from inspect import getmembers, isroutine

from smartanthill.exception import OperArgInvalid


class ArgBase(object):

    def __init__(self):
        self._value = None

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def raise_exception(self, invalid_value):
        members = getmembers(self, lambda a: not isroutine(a))
        attrs = [a for a in members if not a[0].startswith("__") and a[0] !=
                 "_value"]
        raise OperArgInvalid(self.__class__.__name__, attrs, invalid_value)

    def __repr__(self):
        return "%s: value=%s" % (self.__class__.__name__, self._value)


class IntArgBase(ArgBase):

    def __init__(self, min_=None, max_=None, range_=None):
        ArgBase.__init__(self)
        if range_:
            assert len(range_) and (min_ and max_) == None
        else:
            assert range_ == None and (min_ or max_) != None
        self._min = min_
        self._max = max_
        self._range = range_

    def set_value(self, value):

        try:
            _value = int(value)
            if self._range:
                self._range.index(_value)
            elif self._min == None:
                assert _value <= self._max
            elif self._max == None:
                assert _value >= self._min
            else:
                assert self._min <= _value <= self._max

            ArgBase.set_value(self, _value)
        except:
            self.raise_exception(value)


class IntRangeWithAliasArgBase(IntArgBase):

    def __init__(self, range_, alias):
        IntArgBase.__init__(self, range_=range_)
        self._alias = alias

    def set_value(self, value):
        IntArgBase.set_value(self, self._alias[value] if value in self._alias
                             else value)


class DeviceIDArg(IntArgBase):

    def __init__(self):
        IntArgBase.__init__(self, 1, 255)


class PinArg(IntRangeWithAliasArgBase):

    def __init__(self, allowed, alias=None):
        IntRangeWithAliasArgBase.__init__(self, allowed, alias or [])


class PinLevelArg(IntRangeWithAliasArgBase):

    ALIAS = dict(
        LOW=0,
        HIGH=1
    )

    def __init__(self):
        IntRangeWithAliasArgBase.__init__(self, [0, 1], self.ALIAS)


class PinModeArg(IntRangeWithAliasArgBase):

    def __init__(self, allowed, alias=None):
        IntRangeWithAliasArgBase.__init__(self, allowed, alias or [])


class PinAnalogRefArg(IntRangeWithAliasArgBase):

    def __init__(self, allowed, alias=None):
        IntRangeWithAliasArgBase.__init__(self, allowed, alias or [])
