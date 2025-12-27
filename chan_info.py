#! /bin/python3

import os
from sys import argv

usage = "Usage: I'll fill this in later"

if "-f" in argv:
    file = argv[argv.index("-f")+1]
else:
    print(usage)


def read_csv() -> list:
    with open(file, "r") as f:
        content = f.read()

    return content.split("\n")[1:-1]


def write_file(*args):
    output = ""
    srv_count = 1

    for server in args[0]:
        output += f'SERVER{srv_count}={server}-MX\n'
        srv_count += 1
    output += "BUF_TIME=1000"
    return output


def create_endpoint_oudat(data:list):
    for line in data:
        line = line.split(",")

        if not os.path.exists(line[0]):
            os.makedirs(line[0])

        with open(line[0]+"/endpoint.oudat", "w") as output:
            output.write(write_file(line[1:]))


print(read_csv())
