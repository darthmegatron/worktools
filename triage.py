#! /usr/bin/python

___author___ = "Robert Collins"
___version___ = "0.1"

import os
from distutils.version import StrictVersion

class Colors:
    red = "\033[38;5;9m"
    green = "\033[38;5;10m"
    bold = "\033[0;1m"
    none = "\033[0;0m"


class Triage:
    def __init__(self):
        self.base_dir = "/home/ltn/" # Prod
        self.col_connect = "ssh -p 3993 col-control.livetimenet.net "
        self.lted_decoder_dir = "%slted_decoder/" % (self.base_dir)
        self.encoder_dir = "%sltn_encoder/" % (self.base_dir)
        self.audio_deembedder_dir = "%sltn_audio_deembedder/" % (self.base_dir)
        self.schedule_agent_dir = "%sous/schedule_agent/" % (self.base_dir)
        

    def check_software_version (self):
        print("Checking installed software versions...\n")

        def format_version_file(file):
            versions = file.split("\n\n")
            production_versions = versions[0].split("\n")
            production_versions.pop(0)
            x = {}
            for i in production_versions:
                split = i.split(": ")
                x[split[0]] = split[1]
            return x
        

        col_swv = format_version_file(os.popen(self.col_connect+"/usr/local/sbin/deploy_software.sh -V").read())

        app_swv = {}

        if os.system("ls %s &> /dev/null" % self.lted_decoder_dir) == 0:
                app_swv["lted_decoder"] = open(self.lted_decoder_dir+"VERSION", mode="r").read().split(" ")[0]

        if os.system("ls %s &> /dev/null" % self.encoder_dir) == 0:
                app_swv["encoder"] = open(self.encoder_dir+"CHANGELOG.md", mode="r").read().split("##")[:10][1][2:].split("]")[0]

        if os.system("ls %s &> /dev/null" % self.audio_deembedder_dir) == 0:
             app_swv["audio_deembedder"] = open(self.audio_deembedder_dir+"VERSION", mode="r").read().split("\n")[0]

        if os.system("ls %s &> /dev/null" % self.schedule_agent_dir) == 0:
             app_swv["schedule_agent"] = open(self.schedule_agent_dir+"schedule_agent.py", mode="r").read().split("\n")[2].split("= ")[1][1:-1]

        def compare_v():
            """Compare on appliance software versions with the most recent available on col-control"""

            print("")
            for swv in app_swv:
                if StrictVersion(app_swv[swv]) == StrictVersion(col_swv[swv]):
                    print("%s%s%s -%s is up to date. Installed: %s Available: %s%s\n"%(Colors.bold, swv, Colors.none, Colors.green, app_swv[swv], col_swv[swv], Colors.none))

                elif StrictVersion(app_swv[swv]) > StrictVersion(col_swv[swv]):
                    print("%s%s%s -%s version is out of date. Installed: %s Available: %s%s"%(Colors.bold, swv, Colors.none, Colors.red, app_swv[swv], col_swv[swv], Colors.none))

                    print("Installed version is not a production release\n")

                else:
                    print("%s%s%s -%s version is out of date. Installed: %s Available: %s%s"%(Colors.bold, swv, Colors.none, Colors.red, app_swv[swv], col_swv[swv], Colors.none))

                    print("Please check if a newer software version is available for this appliance.\n")
                    
        compare_v()

if __name__ == "__main__":
    trg = Triage()
    trg.check_software_version()
