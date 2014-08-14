__author__ = 'rodtoll'

import threading;
import ping;
import time;
import logging;

class PingTracker(threading.Thread):
    def __init__(self, sleep_period,ping_timeout, retries, retry_pause, logger, report_func, devices):
        super(PingTracker,self).__init__()
        self.devices = devices
        self.sleep_period = sleep_period
        self.ping_timeout = ping_timeout
        self.logger = logger
        self.daemon = True
        self.report_func = report_func
        self.retries = retries
        self.retry_pause = retry_pause

    def run(self):
        while True:
            self.logger.error("Starting ping pass....")
            for device in self.devices:
                for x in range(0,self.retries-1):
                    delay = ping.do_one(device,self.ping_timeout)
                    self.logger.error(str(delay))
                    if delay != None:
                        self.report_func(device, delay)
                        # we are only retrying if not found
                        break
                    time.sleep(self.retry_pause)
            time.sleep(self.sleep_period)
