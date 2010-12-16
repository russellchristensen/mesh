#!/usr/bin/env python
import psutil as ps, time

while 1:
        total = ps.TOTAL_PHYMEM/1024
        avail = ps.avail_phymem()/1024
        used = ps.used_phymem()/1024
        print "|Total: %s| |Available: %s| |Used: %s|" % (total, avail, used) 
        time.sleep(1)


