import subprocess
import threading
import time
import logging

class RHTDataCollector(threading.Thread):
    def __init__(self, base_address, logger, report_func, sleep_period):
        super(RHTDataCollector,self).__init__(group=None)
        self.logger = logger
        self.base_address = base_address
        self.report_func = report_func
        self.sleep_period = sleep_period
        self.daemon = True

    def run(self):
        while True:
            result = subprocess.check_output("./rht03")
            result = result.rstrip('\n')
            results = result.split(',')
            self.logger.error("RHT Read: Temp: "+str(results[0])+" Humidity: "+str(results[1]))
            self.report_func(self.base_address+"-temp", float(results[0]))
            self.report_func(self.base_address+"-humidity", float(results[1]))
            time.sleep(self.sleep_period)
        
