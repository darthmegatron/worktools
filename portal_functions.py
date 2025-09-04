import requests
import json
import os
from urllib.parse import urljoin

BASEURL = "https://transport-test.api.ltnglobal.com/v1/"


class Leaf:
    def __init__(self, name, session):
        self.name = name
        self.session = session
        self.url = urljoin(BASEURL, "leaves")
        self.search_filter = {
            "filter": f'leaf_id=\'{self.name}\'',
            "page_size": 999999
        }
        self.info = self.session.get(self.url, params=self.search_filter).json()["leaves"][0]

    def generate_decoderx_file(self):
        local_path = f'/home/rcol/Desktop/{self.name}'
        decoder_num = self.name[self.name.rindex("d")+1:len(self.name)]

        if not os.path.exists(local_path):
                os.makedirs(local_path)

        with open(f'{local_path}/decoder{decoder_num}.conf', 'w') as file:
            file.write(f'SEND_ADDRESS1={self.info["transport_handoff_ip"]}:\
{self.info["transport_handoff_port"]}')


class Endpoint:
    def __init__(self, name, session):
        self.name = name
        self.session = session
        self.url = urljoin(BASEURL, "endpoint")
        self.search_filter = {
            "filter": f'endpoint_id=\'{self.name}\'',
            "page_size": 999999
        }
        self.info = self.session.get(self.url, params=self.search_filter).json()["endpoint"][0]
    
    def get_endpoint(self):
        pass


class Overlay:
    def __init__(self, name, session):
        self.name = name
        self.session = session
        self.url = urljoin(BASEURL, "overlay_server_pairs")
        self.search_filter = {
            "filter": f'overlay=\'{self.name}\'',
            "page_size": 999999
        }
        self.info = self.session.get(self.url, params=self.search_filter).json()["overlay_server_pairs"]

    
class Flowclient:
    def __init__(self, name, session):
        self.name = name
        self.session = session
        ## Need to verify the api endpoint and search filter for flowclients
        #self.info = self.session.get(self.url, params=self.search_filter).json()["leaves"][0]
        #self.search_filter = {
        #    "filter": f'leaf_id=\'{self.name}\'',
        #    "page_size": 999999
        #}

