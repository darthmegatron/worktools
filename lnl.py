#! /usr/bin/python

import os
import subprocess
from sys import argv

decoder = argv[1]
#decoder_test = "wagm-pqi-station-d71"


def ping_hosts(decoder):
    hosts = []
    endpoint = decoder[:decoder.index("-d")]
    rhosts = ["", "-1", "-2", "-1.vpn", "-2.vpn"]
    
    while len(hosts) < 2:
        for x in rhosts:
            host = endpoint+x
            try:
                if subprocess.check_output("ping %s" %host):
                    hosts.append(host)
            except:
                pass
    print(hosts)


ping_hosts(decoder)
