import json
import os
from urllib.parse import urljoin

BASE_URL = "https://transport.api.ltnglobal.com/v1/"


class Component:
    def __init__(self, name, session):
        self.name = name
        self.session = session


class Channel(Component):
    def __init__(self, name, session):
        super().__init__(name, session)
        self.url = urljoin(BASE_URL, "channels")
        self.search_filter = {
            "filter": f'channel_id=\'{self.name}\'',
            "page_size": 999999
        }
        self.info = self.session.get(self.url, params=self.search_filter).json()["channels"][0]


class Leaf(Component):
    def __init__(self, name, session, filter_by):
        super().__init__(name, session)
        self.filter_by = filter_by
        self.url = urljoin(BASE_URL, "leaves")
        self.search_filter = {
            "filter": f'{self.filter_by}=\'{self.name}\'',
            "page_size": 999999
        }
        self.info = self.session.get(self.url,\
            params=self.search_filter).json()["leaves"]

    def create_decoder_confs(self):
        dir = f'decoder_confs/{self.info[0]['endpoint_id']}'
        if not os.path.exists(dir):
            os.makedirs(dir)

        for decoder in self.info:
            try:
                if '8' in decoder['tag_ids'] and decoder['leaf_type'] == 'DEST':
                    with open(f'{dir}/decoder{decoder['leaf_id']\
[decoder['leaf_id'].rindex("-d")+2:]}.conf', 'w') as decoder_file:
                        decoder_file.write(f'SEND_ADDRESS1={decoder['transport_handoff_ip']}:\
{decoder['transport_handoff_port']}')
            except:
                print('Failure')
        print('Success')

        #with open(f'{local_path}/decoder{decoder_num}.conf', 'w') as file:
        #    file.write(f'SEND_ADDRESS1={self.info["transport_handoff_ip"]}:\
#{self.info["transport_handoff_port"]}')


class Endpoint(Component):
    def __init__(self, name, session):
        super().__init__(name, session)
        self.url = urljoin(BASE_URL, "endpoints")
        self.search_filter = {
            "filter": f'endpoint_id=\'{self.name}\'',
            "page_size": 999999
        }
        self.info = self.session.get(self.url, params=self.search_filter).json()#["endpoint"][0]
    
    def get_endpoint(self):
        pass


class Overlay(Component):
    def __init__(self, name, session):
        super().__init__(name, session)
        self.url = urljoin(BASE_URL, "overlay_server_pairs")
        self.search_filter = {
            "filter": f'overlay=\'{self.name}\'',
            "page_size": 999999
        }
        self.info = self.session.get(self.url, params=self.search_filter).json()["overlay_server_pairs"]

    
class Flowclient(Component):
    def __init__(self, name, session, filter_by):
        super().__init__(name, session)
        self.filter_by = filter_by
        self.url = urljoin(BASE_URL, "flowclients")
        self.search_filter = {
            "filter": f'{self.filter_by}=\'{self.name}\'',
            "page_size": 999999
        }
        self.info = self.session.get(self.url,\
            params=self.search_filter).json()#["leaves"]
            
