#!/usr/bin/env python
import psutil as ps, time

while 1:
        print ps.cpu_percent(interval=1)
        time.sleep(1)


