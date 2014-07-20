# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json
import os.path
from copy import deepcopy

from twisted.python.filepath import FilePath
from twisted.python.util import sibpath

from smartanthill.exception import ConfigKeyError
from smartanthill.util import load_config, merge_nested_dicts, singleton


def get_baseconf():
    return load_config(sibpath(__file__, "config_base.json"))


@singleton
class ConfigProcessor(object):

    def __init__(self, wsdir, user_options):
        self.wsconfp = FilePath(os.path.join(wsdir, "smartanthill.json"))

        self._data = get_baseconf()
        self._wsdata = {}
        self._process_workspace_conf()
        self._process_user_options(user_options)

    def _process_workspace_conf(self):
        if (not self.wsconfp.exists()
                or not self.wsconfp.isfile()):  # pragma: no cover
            return
        self._wsdata = load_config(self.wsconfp.path)
        self._data = merge_nested_dicts(self._data, deepcopy(self._wsdata))

    def _process_user_options(self, options):
        assert isinstance(options, dict)
        for k, v in options.iteritems():
            _dyndict = v
            for p in reversed(k.split(".")):
                _dyndict = {p: _dyndict}
            self._data = merge_nested_dicts(self._data, _dyndict)

    def _write_wsconf(self):
        with open(self.wsconfp.path, "w") as f:
            json.dump(self._wsdata, f, sort_keys=True, indent=2)

    def get(self, key_path, default=None):
        try:
            value = self._data
            for k in key_path.split("."):
                value = value[k]
            return value
        except KeyError:
            if default is not None:
                return default
            else:
                raise ConfigKeyError(key_path)

    def update(self, key_path, data, write_wsconf=True):
        newdata = data
        for k in reversed(key_path.split(".")):
            newdata = {k: newdata}

        self._data = merge_nested_dicts(self._data, deepcopy(newdata))
        self._wsdata = merge_nested_dicts(self._wsdata, newdata)

        if write_wsconf:
            self._write_wsconf()

    def delete(self, key_path, write_wsconf=True):
        if "." in key_path:
            _parts = key_path.split(".")
            _parent = ".".join(_parts[:-1])
            _delkey = _parts[-1]

            # del from current session
            del self.get(_parent)[_delkey]

            # del from workspace
            _tmpwsd = self._wsdata
            for k in _parent.split("."):
                _tmpwsd = _tmpwsd[k]
            del _tmpwsd[_delkey]
        else:
            del self._data[key_path]
            del self._wsdata[key_path]

        if write_wsconf:
            self._write_wsconf()
