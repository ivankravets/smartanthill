# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import os.path

from twisted.python.filepath import FilePath
from twisted.python.util import sibpath

from smartanthill.exception import ConfigKeyError
from smartanthill.util import load_config, merge_nested_dicts, singleton


def get_baseconf():
    return load_config(sibpath(__file__, "config_base.json"))


@singleton
class ConfigProcessor(dict):

    def __init__(self, wsdir, user_options):
        self._data = get_baseconf()
        self.process_workspace_conf(wsdir)
        self.process_user_options(user_options)

        dict.__init__(self, self._data)

    def process_workspace_conf(self, wsdir):
        wsconf_path = FilePath(os.path.join(wsdir, "smartanthill.json"))
        if (not wsconf_path.exists()
                or not wsconf_path.isfile()):  # pragma: no cover
            return
        self._data = merge_nested_dicts(self._data,
                                        load_config(wsconf_path.path))

    def process_user_options(self, options):
        assert isinstance(options, dict)
        for k, v in options.iteritems():
            _dyndict = v
            for p in reversed(k.split(".")):
                _dyndict = {p: _dyndict}
            self._data = merge_nested_dicts(self._data, _dyndict)

    def get(self, key_path, default=None):
        try:
            value = self
            for k in key_path.split("."):
                value = value[k]
            return value
        except KeyError:
            if default is not None:
                return default
            else:
                raise ConfigKeyError(key_path)