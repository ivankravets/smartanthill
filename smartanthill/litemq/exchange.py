# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.


from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.python.failure import Failure
from twisted.python.reflect import namedAny

from smartanthill.exceptions import LiteMQACKFailed, NotImplemnetedYet
from smartanthill.log import Logger


class ExchangeTypesFactory(object):

    @staticmethod
    def newExchange(name, type_):
        obj_path = "smartanthill.litemq.exchange.Exchange%s" % type_.title()
        obj = namedAny(obj_path)(name)
        assert isinstance(obj, ExchangeBase)
        return obj


class Queue(object):

    MESSAGE_RESEND_DELAY = 1  # in seconds
    MESSAGE_MAX_RESEND = 10  # the number of maximum resending

    def __init__(self, name, routing_key):
        self.log = Logger("litemq.queue")
        self.name = name
        self.routing_key = routing_key

        self._callbacks = []

    def attach_callback(self, callback, ack=False):
        assert callable(callback)
        self._callbacks.append((callback, ack))

    def put(self, message, properties):
        assert self._callbacks

        # check "resent" nums
        if ("_resentnums" in properties and
                properties["_resentnums"] > self.MESSAGE_MAX_RESEND):
            return

        d = Deferred()
        for c in self._callbacks:
            d.addCallback(lambda r, c, m, p: c(m, p), c[0], message, properties)
            if c[1]:
                d.addCallback(lambda r: True if isinstance(r, bool) and r else
                              Failure(LiteMQACKFailed()))
        d.addErrback(self._d_errback_callback, message, properties)
        reactor.callWhenRunning(d.callback, True)

    def _d_errback_callback(self, failure, message, properties):
        self.log.warn(failure, message, properties)
        if not "_resentnums" in properties:
            properties["_resentnums"] = 0
        properties["_resentnums"] += 1
        reactor.callLater(self.MESSAGE_RESEND_DELAY * properties["_resentnums"],
                          self.put, message, properties)


class ExchangeBase(object):

    def __init__(self, name):
        self.name = name
        self._queues = {}

    def bind_queue(self, name, routing_key, callback, ack):
        if not name in self._queues:
            self._queues[name] = Queue(name, routing_key)
        self._queues[name].attach_callback(callback, ack)

    def unbind_queue(self, name):
        if name in self._queues:
            del self._queues[name]

    def publish(self, routing_key, message, properties):
        pass


class ExchangeDirect(ExchangeBase):

    def publish(self, routing_key, message, properties):
        for q in self._queues.itervalues():
            if q.routing_key == routing_key:
                q.put(message, properties)


class ExchangeFanout(ExchangeBase):

    def publish(self, routing_key, message, properties):
        for q in self._queues.itervalues():
            q.put(message, properties)


class ExchangeTopic(ExchangeBase):

    def publish(self, routing_key, message, properties):
        raise NotImplemnetedYet
        for q in self._queues.itervalues():
            if self.match(routing_key, q.routing_key):
                q.put(message, properties)

    def match(self, routing_key, routing_pattern):
        # TODO
        pass