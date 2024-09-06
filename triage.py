#! /usr/bin/python

___author___ = "Robert Collins"
___version___ = "0.1"

import os
from distutils.version import StrictVersion
from glob import glob

class Colors:
    red = "\033[38;5;9m"
    green = "\033[38;5;10m"
    bold = "\033[0;1m"
    none = "\033[0;0m"


class Triage:
    def __init__(self):
        self.col_connect = "ssh -p 3993 col-control.livetimenet.net "
        self.base_dir = "/home/ltn/" # Prod
        self.services = {"lted_decoder":"lted_decoder/", "spread":"spread/", "flowclient":"scripts_current/", "schedule_agent":"ous/schedule_agent/", "encoder":"ltn_encoder/",\
            "audio_deembedder":"ltn_audio_deembedder/"}

        for service in self.services:
            self.services[service] = self.base_dir+self.services[service]
                        

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

        
        def check_changelog(service):
            if os.system("ls %s &> /dev/null" % self.services[service]) == 0:
                app_swv[service] = open(self.services[service]+"CHANGELOG.md", mode="r").read().split("##")[:10][1][2:].split("]")[0]


        def check_enabled_services():
            os.chdir("/home/ltn/services")
            enabled_services = glob("service-*")
            for itemx in enabled_services:
                itemy = itemx.split("service-")[1].replace("-","_")
                if itemy == "flow_clients":
                    itemy = "flowclient"
                enabled_services[enabled_services.index(itemx)] = itemy
            for service in check_enabled_services():
            match service:
                case "lted_decoder":
                    app_swv["lted_decoder"] = open(self.services["lted_decoder"]+"VERSION", mode="r").read().split(" ")[0]

                case "audio_deembedder":
                    app_swv["audio_deembedder"] = open(self.services["audio_deembedder"]+"VERSION", mode="r").read().split("\n")[0]

                case: "schedule_agent":
                    app_swv["schedule_agent"] = open(self.services["schedule_agent"]+"schedule_agent.py", mode="r").read().split("\n")[2].split("= ")[1][1:-1]

                case: _:
                    check_changelog(_)
      

        col_swv = format_version_file(os.popen(self.col_connect+"/usr/local/sbin/deploy_software.sh -V").read())

        app_swv = {}
        
        check_enabled_services()


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
