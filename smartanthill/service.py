# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from sys import argv as sys_argv

from twisted.application.service import MultiService
from twisted.python import usage
from twisted.python.filepath import FilePath
from twisted.python.reflect import namedModule

from smartanthill import __banner__, __version__
from smartanthill.configprocessor import ConfigProcessor, get_baseconf
from smartanthill.log import Logger


class SAMultiService(MultiService):

    def __init__(self, name, options=None):
        MultiService.__init__(self)
        self.setName(name)
        self.options = options
        self.log = Logger(self.name)

        self._started = False
        self._onstarted = []

    def startService(self):
        MultiService.startService(self)

        infomsg = "Service has been started"
        self.log.info(infomsg + " with options '%s'" % self.options)

        self._started = True
        for callback in self._onstarted:
            callback()

    def stopService(self):
        MultiService.stopService(self)
        self.log.info("Service has been stopped.")

    def on_started(self, callback):
        if self._started:
            callback()
        else:
            self._onstarted.append(callback)


class SmartAnthillService(SAMultiService):

    INSTANCE = None

    def __init__(self, name, options):
        SmartAnthillService.INSTANCE = self
        self.workspacedir = options['workspacedir']
        self.config = ConfigProcessor(self.workspacedir, options)
        SAMultiService.__init__(self, name, options)

    @staticmethod
    def instance():
        return SmartAnthillService.INSTANCE

    def startService(self):
        dashboard = ("http://localhost:%d/" %
                     self.config.get("services.dashboard.options.port"))
        self.log.info(__banner__.replace(
            "#wsdir#", self.workspacedir).replace("#dashboard#", dashboard))

        self.log.debug("Initial configuration: %s." % self.config)
        self._preload_subservices()
        SAMultiService.startService(self)

    def _preload_subservices(self):
        services = sorted(self.config.get("services").items(), key=lambda s:
                          s[1]['priority'])
        for name, _ in services:
            self.startSubService(name)

    def startSubService(self, name):
        sopt = self.config.get("services.%s" % name)
        if "enabled" not in sopt or not sopt['enabled']:
            return
        path = "smartanthill.%s.service" % name
        service = namedModule(path).makeService(name, sopt['options'])
        service.setServiceParent(self)

    def stopSubService(self, name):
        self.removeService(self.getServiceNamed(name))

    def restartSubService(self, name):
        self.stopSubService(name)
        self.startSubService(name)


class Options(usage.Options):
    optParameters = [["workspacedir", "w", ".",
                      "The path to workspace directory"]]

    compData = usage.Completions(
        optActions={"workspacedir": usage.CompleteDirs()})

    longdesc = "SmartAnthill is an intelligent micro-oriented "\
        "networking system (version %s)" % __version__

    allowed_defconf_opts = ("logger.level",)

    def __init__(self):
        self._gather_baseparams(get_baseconf())
        usage.Options.__init__(self)

    def _gather_baseparams(self, baseconf, path=None):
        for k, v in baseconf.items():
            argname = path + "." + k if path else k
            # print argname, v, type(v)
            if isinstance(v, dict):
                self._gather_baseparams(v, argname)
            else:
                if argname not in self.allowed_defconf_opts:
                    continue
                self.optParameters.append([argname, None, v, None, type(v)])

    def postOptions(self):
        wsdir_path = FilePath(self['workspacedir'])
        if not wsdir_path.exists() or not wsdir_path.isdir():
            raise usage.UsageError("The path to the workspace directory"
                                   " is invalid")
        elif wsdir_path.getPermissions().user.shorthand() != 'rwx':
            raise usage.UsageError("You don't have 'read/write/execute'"
                                   " permissions to workspace directory")
        self['workspacedir'] = wsdir_path.path


def makeService(options):
    user_options = dict((p[0], options[p[0]]) for p in options.optParameters)
    cmdopts = frozenset([v.split("=")[0][2:] for v in sys_argv
                         if v[:2] == "--" and "=" in v])
    for k in cmdopts.intersection(frozenset(user_options.keys())):
        user_options[k] = options[k]

    return SmartAnthillService("sas", user_options)
