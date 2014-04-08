# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from twisted.internet.defer import inlineCallbacks
from twisted.python.constants import ValueConstant

from smartanthill.device.board import BoardFactory
from smartanthill.device.operation.base import OperationType
from smartanthill.exception import DeviceUnknownOperation
from smartanthill.log import Logger
from smartanthill.service import SmartAnthillService


class Device(object):

    def __init__(self, id_, options):
        self.log = Logger("device.%d" % id_)
        self.id_ = id_
        self.options = options
        self.operations = set([OperationType.PING,
                               OperationType.LIST_OPERATIONS])
        self.board = BoardFactory.newBoard(options['board'])
        SmartAnthillService.instance().on_started(self.preload_operations)

    def launch_operation(self, type_, data=None):
        assert isinstance(type_, ValueConstant)
        if type_ in self.operations:
            return self.board.launch_device_operation(self.id_, type_, data)
        raise DeviceUnknownOperation(type_.name, self.id_)

    @inlineCallbacks
    def preload_operations(self):
        result = yield self.launch_operation(OperationType.LIST_OPERATIONS)
        for cdc in result:
            self.operations.add(OperationType.lookupByValue(cdc))
        self.operations = frozenset(self.operations)
        self.log.info("Received allowed operations: %s" %
                      [o.name for o in self.operations])