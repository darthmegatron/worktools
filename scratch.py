#! /usr/bin/python3

import requests
import json
from urllib.parse import urljoin
import csv
import os
import portal_functions as pf
from sys import argv
import subprocess


class Colors:
    red = "\033[38;5;9m"
    green = "\033[38;5;10m"
    bold = "\033[0;1m"
    none = "\033[0;0m"


base_url = "https://transport.api.ltnglobal.com/v1/"
#script_host = subprocess.run('hostname', stdout=subprocess.PIPE, text=True).stdout.strip()

with open("/home/rcol/api-key.json") as key_file:
    key_file = json.load(key_file)
    api_key = key_file["api_key"]
    username = key_file["username"]
    password = key_file["password"]

request_session = requests.Session()
request_session.mount(base_url, requests.adapters.HTTPAdapter())
request_session.params = {"key": api_key}
login = {"user_id": username, "password": password}
response = request_session.post(urljoin(base_url, "oauth/token"), json=login)
response.raise_for_status()
val = response.json()
request_session.headers["Authorization"] = f"Bearer {val['token']}"
url = urljoin(base_url, "leaves")


def package_request(api_endpoint, filter1, filter2) -> dict:
    """Form get request payload."""
    url = urljoin(base_url, api_endpoint)

    data = {
        "filter": f'{filter1}=\'{filter2}\'',
        "page_size": 999999
    }

    return request_session.get(url, params = data).json()


def create_leaves():
    pass


def parse_leaf(holder) -> list:
    """Isolate key values to create encoder/decoder confs."""
    count = 0
    output = []
    #print(holder)
    for x in holder['leaves']:
        output.append({})
        output[count]["leaf_id"] = x["leaf_id"]
        output[count]["ip_address"] = x["ip_address"]
        output[count]["transport_handoff_ip"] = x["transport_handoff_ip"]
        output[count]["transport_handoff_port"] = x["transport_handoff_port"]
        output[count]["leaf_type"] = x["leaf_type"]
        output[count]["card_index"] = x["card_index"]
        output[count]["tag_ids"] = x["tag_ids"]
        count += 1
    return output


app_leaves = parse_leaf(package_request("leaves", "endpoint_id", "ltnr-bwi-rcollins"))
#for config in app_leaves:
 #   print(config)


### TESTING NEW TINGS
#leaf = pf.Leaf("ltnr-bwi-rcollins-d1", request_session)
#chan = pf.Channel("234.0.4.1", request_session)

def create_decoder_confs():
    if "-f" in argv:
        file = argv[argv.index("-f")+1]
    else:
        print(usage)

    with open(file, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            leaf = pf.Leaf(', '.join(row), request_session)
            leaf.generate_decoderx_file()


def verify_decoder_confs():
    def ssh_return(args):
        try:
            result = subprocess.run(['ssh'] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.stderr}")
            return None

    def get_info(leaf):
        COL_JUMP = ['-J', 'col-control']
        info = leaf.info
        endpoint = info["endpoint_id"]
        handoff = info["transport_handoff_ip"]
        port = info["transport_handoff_port"]
        leaf_id = info['leaf_id']
        decoder_num = leaf_id[leaf_id.rindex("-d")+2:]
        ssh_arg1 = ['-p', '3999', f'{endpoint}-1.livetimenet.net', \
f'cat /home/ltn/ous/confs/decoder{decoder_num}.conf']
        ssh_arg2 = ['-p', '3999', f'{endpoint}-2.livetimenet.net', \
f'cat /home/ltn/ous/confs/decoder{decoder_num}.conf']

        #print(info)

        if script_host != 'col-control':
            ssh_arg1 = COL_JUMP + ssh_arg1
            ssh_arg2 = COL_JUMP + ssh_arg2

        output1 = ssh_return(ssh_arg1)
        output2 = ssh_return(ssh_arg2)

        if output1 and output2 == f'SEND_ADDRESS1={handoff}:{port}':
            print(f'{Colors.green}Decoder {leaf_id} confs match portal records\n{Colors.none}')

    if "-f" in argv:
        file = argv[argv.index("-f")+1]
    
    if file.endswith(".csv"):
        with open(file, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in spamreader:
                leaf = pf.Leaf(', '.join(row), request_session)
                get_info(leaf)
    else:
        leaf = pf.Leaf(file, request_session)
        get_info(leaf)


if "--create-decoder-confs" in argv:
    create_decoder_confs()

if "--verify-decoder-confs" in argv:
    verify_decoder_confs()

if "-f" in argv:
    file = argv[argv.index("-f")+1]


def read_csv() -> list:
    with open(file, "r") as f:
        content = f.read()

    return content.split("\n")[1:]


def write_csv(content) -> list:
    with open(file, "w") as f:
        #f.write('channel_id, overlay_id, overlay2_id, contact_ids_set, channel_type, long_title, description, encrypted, video_type, protocol,\
#cnp_keygen, default_min_buffer, short_title, streaming_link, stream_available, disconnection_delay, max_drain_rate_mbps\n')
        f.write(f'{content['header']}\n')
        for line in content['body']:
            f.write(line+"\n")
        f.close
    print("\nI'M PICKLE RICK!\n")


def channel_lookup(channels:list) -> list:
    data = []
    for line in channels:
        line = line.split(",")
        chan = line[0]
        if chan == "build new" or chan == "":
            pass
        else:
            channel = pf.Channel(chan, request_session)
            print(f'Channel Info: {channel.info.keys()}')
            overlay = channel.info['overlay_id']
            protocol = channel.info['protocol'] or channel.info['protocol_null']
            if "default_min_buffer" in channel.info.keys():
                buffer = channel.info['default_min_buffer']
            else:
                buffer = ""
            channel_type = channel.info['channel_type']
            channel_name = channel.info['long_title']
            description = channel.info['description']
            #encrypted = channel.info['encrypted']
            stream_available = channel.info['stream_available']
            line = ",".join([line[0],overlay, protocol, str(buffer), channel_type, channel_name, description, str(stream_available)]) #str(encrypted), str(stream_available)])
            data.append(line)
    return data


def channel_lookup_test(channels:list) -> list:
    data = []
    for line in channels:
        line = line.split(",")
        chan = line[0]
        #print(f'Channel: {chan}')
        if chan == "build new" or chan == "":
            pass
        else:
            channel = pf.Channel(chan, request_session)
            #print(f'Channel Info: {channel.info.keys()}')
            chan_params = ['channel_id', 'overlay_id', 'overlay2_id', 'contact_ids_set', 'channel_type', 'long_title', 'description', 'encrypted', 'video_type', 'protocol',\
                'cnp_keygen', 'default_min_buffer', 'short_title', 'streaming_link', 'stream_available', 'disconnection_delay', 'max_drain_rate_mbps']

            chan_info = dict.fromkeys(chan_params, None)

            for param in chan_params:
                if param in channel.info.keys():
                    chan_info[param] = str(channel.info[param])
                else:
                    chan_info[param] = "null"

            data.append(",".join(list(chan_info.values())))
    return {'header':', '.join(chan_params), 'body':data}


def endpoint_leaves(endpoint):
    data = []
    endpt = pf.Leaf(endpoint, request_session, "endpoint_id")
    #print(f'Endpoint Info: {endpt.info[0].keys()}')
    #print(f'Endpoint Info: {endpt.info}')

    leaf_params = ['leaf_id', 'endpoint_id', 'hardware_id',\
        'primary_leaf_id', 'leaf_type', 'equipment_type', 'equipment_name',\
        'latency_compat', 'ip_address', 'management_ip', 'managed_by_ltn',\
        'leaf_control_default', 'description', 'transport_handoff_ip',\
        'transport_handoff_ip_2', 'transport_handoff_port', 'transport_handoff_port_2',\
        'max_bitrate', 'resolutions_available_set', 'status', 'leaf_comment', 'role',\
        'card_index', 'instance_id', 'tag_ids_set', 'external_min_port',\
        'external_max_port', 'log_last_mod_username', 'log_last_mod_time',\
        'log_create_username', 'log_create_time', 'log_info', 'ip_address_2',\
        'connector_id', 'signal_flow_stage', 'mode', 'passphrase',\
        'send_address', 'send_port', 'receive_address', 'receive_port',\
        'booking_contract_id', 'input_address', 'input_args',\
        'output_url', 'latency_ms', 'output_bitrate_mbps',\
        'log_internal', 'enable_smoother', 'stats_file',\
        'name', 'renumber_pids', 'filter_pids',\
        'drift_management', 'ltn_mux_input', 'ltn_mux_output']
    
    for x in range(0, len(endpt.info)):
        leaf_info = dict.fromkeys(leaf_params, None)

        for param in leaf_params:
            if param in endpt.info[x].keys():
                leaf_info[param] = str(endpt.info[x][param])
            else:
                leaf_info[param] = "null"

        data.append(",".join(list(leaf_info.values())))
    return data


def endpoint_flowclients(endpoint):
    data = []
    header = ''
    query = pf.Flowclient(endpoint, request_session, "endpoint_id")
    #print(f'Endpoint Info: {query.info['flowclients'][0].keys()}')
    #print(f'Endpoint Info: {query.info['flowclients'][0]}')

    params = ['flowclient_id', 'channel_id', 'endpoint_id', 'leaf_id',\
        'description', 'client_type', 'status', 'redundant', 'appliance_num',\
        'max_drain_rate_mbps', 'burst_bucket_bytes', 'burst_delay_queue_bytes',\
        'log_last_mod_username', 'log_last_mod_time', 'log_create_username',\
        'log_create_time', 'log_info', 'ou_managed', 'isp_circuit_ids_set']
    
    for x in range(0, len(query.info['flowclients'])):
        info = dict.fromkeys(params, None)

        for param in params:
            if param in query.info['flowclients'][x].keys():
                info[param] = str(query.info['flowclients'][x][param])
            else:
                info[param] = "null"

        data.append(",".join(list(info.values())))

    return {'header':', '.join(params), 'body':data}

def testing():
    '''This is a testing function. Complete BS'''
    pass


def create_local_confs():
    with open(file, "r") as f:
        content = f.read().split("\n")[1:]
        

        for entry in content:
            entry = entry.split(",")
            print(entry)
            decoder_x = entry[0][entry[0].index('-d')+2:]
            send_address = f'SEND_ADDRESS1={entry[1]}:{entry[2]}'
            
            with open(f'/home/rcol/confs/decoder{decoder_x}.conf', 'w') as f:
                f.write(send_address)
                f.close



#print(read_csv())
#channel_lookup(read_csv())
#channel_lookup_test(read_csv())
#write_csv(channel_lookup(read_csv()))
#write_csv(channel_lookup_test(read_csv()))
#write_csv(endpoint_flowclients("ltnp-lax-n"))
#create_local_confs()
write_csv(endpoint_flowclients("ltnp-lax-i"))
