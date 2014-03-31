# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.python.constants import ValueConstant, Values
from twisted.python.reflect import namedAny

import smartanthill.network.cdc as cdc
from smartanthill.device.arg import DeviceIDArg
from smartanthill.network.zvd import ZeroVirtualDevice


class OperationType(Values):

    PING = ValueConstant(
        cdc.CHANNEL_URGENT.PING.value)
    LIST_OPERATIONS = ValueConstant(
        cdc.CHANNEL_BDCREQUEST.LIST_OPERATIONS.value)
    CONFIGURE_PIN_MODE = ValueConstant(
        cdc.CHANNEL_BDCREQUEST.CONFIGURE_PIN_MODE.value)
    READ_DIGITAL_PIN = ValueConstant(
        cdc.CHANNEL_BDCREQUEST.READ_DIGITAL_PIN.value)
    WRITE_DIGITAL_PIN = ValueConstant(
        cdc.CHANNEL_BDCREQUEST.WRITE_DIGITAL_PIN.value)
    CONFIGURE_ANALOG_REFERENCE = ValueConstant(
        cdc.CHANNEL_BDCREQUEST.CONFIGURE_ANALOG_REFERENCE.value)
    READ_ANALOG_PIN = ValueConstant(
        cdc.CHANNEL_BDCREQUEST.READ_ANALOG_PIN.value)
    WRITE_ANALOG_PIN = ValueConstant(
        cdc.CHANNEL_BDCREQUEST.WRITE_ANALOG_PIN.value)


class OperationBase(object):

    TYPE = None
    TTL = 1
    ACK = True
    REQUIRED_PARAMS = None

    def __init__(self, board, data):
        self.board = board
        self.data = data

    def process_data(self, data):  # pylint: disable=W0613,R0201
        return []

    def on_result(self, result):   # pylint: disable=R0201
        return result

    @inlineCallbacks
    def launch(self, devid):
        devidarg = DeviceIDArg()
        devidarg.set_value(devid)

        zvd = ZeroVirtualDevice()
        result = yield zvd.request(self.TYPE.value, devidarg.get_value(),
                                   self.TTL, self.ACK,
                                   self.process_data(self.data))
        returnValue(self.on_result(result))

    def check_params(self, params):
        if not self.REQUIRED_PARAMS:
            return True
        params = [s if "[" not in s else s[:s.find("[")]+"[]" for s in params]
        return set(self.REQUIRED_PARAMS) <= set(params)


def get_operclass(type_):
    assert isinstance(type_, ValueConstant)
    if not hasattr(get_operclass, "cache"):
        get_operclass.cache = {}
    if type_.value not in get_operclass.cache:
        get_operclass.cache[type_.value] = namedAny(
            "smartanthill.device.operation.%s.Operation" % type_.name.lower())
    return get_operclass.cache[type_.value]
