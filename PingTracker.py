__author__ = 'rodtoll'

import threading;
import ping;
import time;
import logging;

class PingTrackerManager:
    def __init__(self, sleep_period,ping_timeout, retries, retry_pause, logger, report_func, devices):
        self.trackers = []
        self.devices = devices
        self.sleep_period = sleep_period
        self.ping_timeout = ping_timeout
        self.logger = logger
        self.daemon = True
        self.report_func = report_func
        self.retries = retries
        self.retry_pause = retry_pause
        tracker_index = 0
        for device in devices:
            new_tracker = PingTracker(tracker_index, sleep_period, ping_timeout, retries, retry_pause, logger, report_func, device)
            self.trackers.append(new_tracker)
            new_tracker.start()
            tracker_index += 1

class PingTracker(threading.Thread):
    def __init__(self, tracker_index, sleep_period,ping_timeout, retries, retry_pause, logger, report_func, device):
        super(PingTracker,self).__init__()
        self.device = device
        self.sleep_period = sleep_period
        self.ping_timeout = ping_timeout
        self.logger = logger
        self.daemon = True
        self.report_func = report_func
        self.retries = retries
        self.retry_pause = retry_pause
        self.tracker_index = tracker_index

    def run(self):
        while True:
            self.logger.error("PING ["+str(self.tracker_index)+"] - Starting ping pass....")
            for x in range(0,self.retries-1):
                delay = ping.do_one(self.device,self.ping_timeout)
                if delay is not None:
                    self.logger.error("Device: " + self.device + " - " + str(delay))
                    self.report_func(self.device, delay)
                    # we are only retrying if not found
                    break
                else:
                    self.logger.error("Device: " + self.device + " - No Response")
                time.sleep(self.retry_pause)
            time.sleep(self.sleep_period)
