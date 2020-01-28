import simpy
import numpy as np
from collections import deque, OrderedDict


class Part(object):

    def __init__(self, time, data, id, src="a", dst="z", flow_id=0):
        self.time = time
        self.id = id
        self.src = src
        self.dst = dst
        self.flow_id = flow_id
        self.data = data

    def __repr__(self):
        return "id: {}, src: {}, time: {}".format(self.id, self.src, self.time)


class Source(object):

    def __init__(self, env, id, data, initial_delay=0, finish=float("inf"), flow_id=0):
        self.id = id
        self.env = env
        self.data = data
        self.initial_delay = initial_delay
        self.finish = finish
        self.parts_sent = 0
        self.action = env.process(self.run())
        self.flow_id = flow_id
        self.out = None
        self.start_time = 0.0
        self.start_time_list = []

    def run(self):
        yield self.env.timeout(self.initial_delay)
        while self.env.now < self.finish:
            try:
                temp = next(self.data)
                yield self.env.timeout(temp["Assembly"][0])
                self.start_time_list.append(self.env.now)
                # self.start_time += temp["Assembly"][0]

                self.parts_sent += 1
                p = Part(self.env.now, temp, self.parts_sent, src=self.id,
                                  flow_id=self.flow_id)

                if self.out.inventory + self.out.busy >= self.out.qlimit:
                    stop = self.env.event()
                    self.out.wait1.append(stop)
                    yield stop

                self.out.put(p)
            except StopIteration:
                break


class Sink(object):

    def __init__(self, env, name, rec_arrivals=True, absolute_arrivals=False, rec_waits=True, debug=True, selector=None):
        self.name = name
        self.store = simpy.Store(env)
        self.env = env
        self.rec_waits = rec_waits
        self.rec_arrivals = rec_arrivals
        self.absolute_arrivals = absolute_arrivals
        self.waits = []
        self.arrivals = []
        self.debug = debug
        self.parts_rec = 0
        self.selector = selector
        self.last_arrival = 0.0

    def put(self, part):
        if not self.selector or self.selector(part):
            now = self.env.now
            if self.rec_waits:
                self.waits.append(self.env.now - part.time)
            if self.rec_arrivals:
                if self.absolute_arrivals:
                    self.arrivals.append(now)
                else:
                    self.arrivals.append(now)
                self.last_arrival = now
            self.parts_rec += 1

            if self.debug:
                print(part)


class Process(object):

    def __init__(self, env, name, subprocess_num, qlimit=None, limit_bytes=True, debug=False):
        self.name = name
        self.store = simpy.Store(env)
        self.env = env
        self.subprocess_num = subprocess_num
        self.wait1 = deque([])
        self.wait2 = self.env.event()
        self.parts_rec = 0
        self.parts_drop = 0
        self.qlimit = qlimit
        self.out = None
        self.limit_bytes = limit_bytes
        self.debug = debug
        self.inventory = 0
        self.busy = 0
        self.working_time = 0
        self.action = env.process(self.run())
        self.start_time = []
        self.finish_time = 0.0

    def run(self):
        while True:
            if self.busy < self.subprocess_num:
                msg = (yield self.store.get())
                self.inventory -= 1
                self.busy += 1
                self.env.process(self.subrun(msg))
            else:
                yield self.wait2

    def subrun(self, msg):
        proc_time = msg.data[self.name][1]
        start_time = self.env.now
        self.start_time.append(start_time)
        yield self.env.timeout(proc_time)
        print(self.name, self.env.now)
        self.working_time += self.env.now - start_time

        if self.out.__class__.__name__ == 'Process':
            lag = msg.data[self.out.name][0]
            if lag > 0:
                yield self.env.timeout(lag)

            if self.out.inventory + self.out.busy >= self.out.qlimit:
                stop = self.env.event()
                self.out.wait1.append(stop)
                yield stop
        self.out.put(msg)
        self.parts_rec += 1

        self.busy -= 1
        self.wait2.succeed()
        self.wait2 = self.env.event()
        self.finish_time = self.env.now

        if self.debug:
            print(msg)

        if self.inventory + self.busy < self.qlimit and len(self.wait1) > 0:
            temp = self.wait1.popleft()
            temp.succeed()

    def put(self, part):
        self.inventory += 1
        self.parts_rec += 1
        if self.qlimit is None:
            return self.store.put(part)
        elif len(self.store.items) >= self.qlimit:
            self.parts_drop += 1
        else:
            return self.store.put(part)


class Monitor(object):

    def __init__(self, env, port, dist):
        self.port = port
        self.env = env
        self.dist = dist
        self.M = []
        self.time = []
        self.WIP = []
        self.action = env.process(self.run())
        self.TH = []
        self.TH_time = []

    def run(self):
        while True:
            yield self.env.timeout(self.dist())

            if self.port.__class__.__name__ == 'Sink':
                if len(self.port.arrivals) > 0:
                    temp_list = []
                    for i in range(1, len(self.port.arrivals)):
                        temp_list.append(self.port.arrivals[i] - self.port.arrivals[i - 1])
                    th = 1 / (np.mean(temp_list))

                    self.TH.append(th)
                    self.TH_time.append(self.env.now)
            else:
                m = self.port.busy
                wip = self.port.inventory
                self.WIP.append(wip)
                self.M.append(m)

            self.time.append(self.env.now)