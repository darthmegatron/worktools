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
            "audio_deembedder":"ltn_audio_deembedder/", "ltn_srt_connector":"srt_connector/", "ltn_thumbnailer":"ltn_thumbnailer/"}

        for service in self.services:
            self.services[service] = self.base_dir+self.services[service]
                        

    def check_software_version (self):
        """Returns current software versions available on col-control."""
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

        
        def check_enabled_services():
            """Return enabled services running on the appliance."""
            os.chdir("/home/ltn/services")
            enabled_services = glob("service-*")
            sub = {"flow_clients":"flowclient", "srt_connector":"ltn_srt_connector", "ltn_audio_deembedder":"audio_deembedder", "ltn_encoder":"encoder"}
            for itemx in enabled_services:
                itemy = itemx.split("service-")[1].replace("-","_")
                if itemy in sub:
                    itemy = sub[itemy]
                enabled_services[enabled_services.index(itemx)] = itemy
            return enabled_services

        
        def check_changelog(service):
            """Isolate version number from software packages with a Changelog file."""
            if os.system("ls %s &> /dev/null" % self.services[service]) == 0:
                app_swv[service] = open(self.services[service]+"CHANGELOG.md", mode="r").read().split("##")[:10][1][2:].split("]")[0]
        

        col_swv = format_version_file(os.popen(self.col_connect+"/usr/local/sbin/deploy_software.sh -V").read())

        app_swv = {}
        
        for service in check_enabled_services():
            if service == "lted_decoder":
                app_swv[service] = open(self.services[service]+"VERSION", mode="r").read().split(" ")[0]

            elif service == "audio_deembedder":
                app_swv[service] = open(self.services[service]+"VERSION", mode="r").read().split("\n")[0]

            elif service == "schedule_agent":
                app_swv[service] = open(self.services[service]+"schedule_agent.py", mode="r").read().split("\n")[2].split("= ")[1][1:-1]
            
            elif service == "ltn_srt_connector":
                pass

            else:
                check_changelog(service)


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
