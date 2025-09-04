#! /bin/python3
# CRUDE ROUGH DRAFT

import os
from sys import argv

usage = """
    -f input file
    -d srt direction (send/recv)
"""

if "-f" in argv:
    file = argv[argv.index("-f")+1]
else:
    exit(usage)

if "-d" in argv:
    direction = argv[argv.index("-d")+1]
    if direction == "send":
        RECV_MEDIUM="udp"
        SEND_MEDIUM="srt"
    else:
        RECV_MEDIUM="srt"
        SEND_MEDIUM="udp"


def read_csv() -> list:
    with open(file, "r") as f:
        content = f.read()
    return content.split("\n")[1:]


def create_srt_conf(data:list):
    # This function needs some TLC. At the time of writing this for a specific project I just manually swapped 
    # the fields that need to be replaced in the template.replace functions. I'll try to work on making this more of a 
    # multi-use script for static srt confs
    
    for line in data:
        line = line.split(",")

        leaf = line[6]
        chan_name = line[0][line[0].index(" - ")+3:].lower()
        recv_port = line[3]
        mode = line[7]

        with open('srt_conf_example.conf', 'r') as file:
            template = file.read()
            file.close()

        template = template.replace('SEND_PORT=', f'SEND_PORT="{recv_port}"')
        template = template.replace('RECV_MEDIUM=', f'RECV_MEDIUM="{RECV_MEDIUM}"')
        template = template.replace('SEND_MEDIUM=', f'SEND_MEDIUM="{SEND_MEDIUM}"')
        template = template.replace('SEND_ADDR=', f'SEND_ADDR="127.0.0.1"')
        template = template.replace('MODE=', f'MODE="{mode}"')
        
        file_name = f'{direction}-srt-{leaf}-{chan_name}.conf'

        if not os.path.exists(line[1]):
            os.makedirs(line[1])

        template1 = template.replace('RECV_ADDR=', f'RECV_ADDR="{line[4][0:line[4].index(':')]}"')
        template1 = template1.replace('RECV_PORT=', f'RECV_PORT="{line[4][line[4].index(':')+1:]}"')

        with open(line[1]+f'/{file_name}', "w") as output:
            output.write(template1)
        
        if not os.path.exists(line[2]):
            os.makedirs(line[2])

        template2 = template.replace('RECV_ADDR=', f'RECV_ADDR="{line[5][0:line[5].index(':')]}"')
        template2 = template2.replace('RECV_PORT=', f'RECV_PORT="{line[5][line[5].index(':')+1:]}"')

        with open(line[2]+f'/{file_name}', "w") as output:
            output.write(template2)


create_srt_conf(read_csv())
