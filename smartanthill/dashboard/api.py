# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json

from twisted.internet.defer import maybeDeferred
from twisted.python.failure import Failure
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET

from smartanthill.configprocessor import ConfigProcessor
from smartanthill.device.operation.base import OperationType
from smartanthill.log import Logger
from smartanthill.util import get_service_named
from smartanthill.webrouter import WebRouter

# pylint: disable=W0613

router = WebRouter(prefix="/api")


@router.add("/", method="OPTIONS")
def cors(request):
    """ Preflighted request """
    request.setHeader("Access-Control-Allow-Origin", "*")
    request.setHeader("Access-Control-Allow-Methods",
                      "GET, POST, PUT, DELETE, OPTIONS")
    request.setHeader("Access-Control-Allow-Headers",
                      "Content-Type, Access-Control-Allow-Headers")
    return None


@router.add("/boards$")
def get_boards(request):
    boards = get_service_named("device").get_boards()
    data = [{"id": id_, "name": board.get_name()} for id_, board in
            boards.iteritems()]
    return sorted(data, key=lambda d: d['id'])


@router.add("/boards/<board_id>")
def get_board_info(request, board_id):
    board = get_service_named("device").get_board(board_id)
    data = {
        "id": board_id,
        "name": board.get_name(),
        "vendor": board.get_vendor(),
        "inforUrl": board.get_info_url(),
        "pins": board.get_pins(),
        "pinsAlias": board.get_pins_alias(),
        "analogPins": board.get_analog_pins(),
        "pwmPins": board.get_pwm_pins(),
        "extintPins": board.get_extint_pins(),
        "pinModeArgParams": board.get_pinmodearg_params()[1],
        "pinAnalogRefArgParams": board.get_pinanalogrefarg_params()[1]
    }
    return data


@router.add("/devices$")
def get_devices(request):
    devices = get_service_named("device").get_devices()
    data = [{
        "id": id_,
        "boardId": device.board.get_id(),
        "name": device.get_name()
    } for id_, device in devices.iteritems()]
    return sorted(data, key=lambda d: d['id'])


@router.add("/devices/<int:devid>")
def get_device_info(request, devid):
    assert 0 < devid <= 255
    device = get_service_named("device").get_device(devid)
    data = {
        "id": devid,
        "boardId": device.board.get_id(),
        "name": device.get_name(),
        "operationIds": [item.value for item in device.operations],
        "network": device.options.get("network", {})
    }
    return data


@router.add("/devices/<int:devid>", method="POST")
def update_device(request, devid):
    assert 0 < devid <= 255
    ConfigProcessor().update("services.device.options.devices.%d" % devid,
                             json.loads(request.content.read()))
    sas = get_service_named("sas")
    sas.stopSubService("network")
    sas.restartSubService("device")
    sas.startSubService("network")
    return get_device_info(request, devid)


@router.add("/devices/<int:devid>", method="DELETE")
def delete_device(request, devid):
    assert 0 < devid <= 255
    ConfigProcessor().delete("services.device.options.devices.%d" % devid)
    sas = get_service_named("sas")
    sas.stopSubService("network")
    sas.restartSubService("device")
    sas.startSubService("network")
    return None


@router.add("/operations")
def get_operations(request):
    return [{"id": item.value, "name": item.name} for item in
            OperationType.iterconstants()]


@router.add("/serialports")
def get_serialports(request):
    import os
    if os.name == "nt":
        from serial.tools.list_ports_windows import comports
    elif os.name == 'posix':
        from serial.tools.list_ports_posix import comports
    else:
        raise ImportError("Sorry: no implementation for your platform ('%s') "
                          "available" % os.name)
    data = [{"port": p, "decription": d, "hwid": h} for p, d, h in comports()]
    return data


class REST(Resource):

    isLeaf = True

    def __init__(self):
        Resource.__init__(self)
        self.log = Logger("dashboard.api")

    def render(self, request):
        d = maybeDeferred(router.match, request)
        d.addBoth(self.delayed_render, request)
        return NOT_DONE_YET

    def delayed_render(self, result, request):
        request.setHeader("Access-Control-Allow-Origin", "*")
        if isinstance(result, Failure):
            self.log.error(result)
            request.setResponseCode(500)
            request.write(str(result.getErrorMessage()))
        elif result:
            request.setHeader("Content-Type", "application/json")
            request.write(json.dumps(result))
        request.finish()
