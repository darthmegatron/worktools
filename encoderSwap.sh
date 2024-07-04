#! /bin/bash
#
# Quickly change encoders and restart flowclients during OTTO/D2 maintenance

## Maintenance related channels
channels="230.0.187.68 230.0.187.18 230.0.187.70 230.0.187.16 230.0.187.69 230.0.187.17"

message="Encoders swapped and flowclient restarted for"

############################################################################
# Print command usage to the terminal
# Outputs:
#	Writes command usage to stdout
############################################################################
function usage () {
	echo "Usage: encoderSwap.sh [CONF FILE]... [OPTION]..."
	echo "Options:"
	echo "	--auto Swap RECEIVE_ADDRESS and RECEIVE_PORT for all OTTO channels on the appliance. When using"
	echo "			the --auto option you do not need to supply a conf file."
	echo " 			eg. encoderSwap.sh --auto"
	exit
}

############################################################################
# Comment lines that begin with RECEIVE_A* and RECEIVE_P* (RECEIVE_ADDRESS # and RECEIVE_PORT) and uncomment the ones with #RECEIVE_A and #RECEIVE_P, # changing the source encoder order.
# Globals:
#	None
# Arguments:
#	*.conf
############################################################################
function swap () {
	for conf in $@; do
		list=$(grep -e "RECEIVE_[AP]" $conf)
		for line in $list; do
			if [ ${line::1} = "#" ]; then
				sed -i "s/$line/${line:1}/g" $conf
			else
				sed -i "s/\b$line\b/#$line/g" $conf
			fi; done; done
}

function find_conf () {
	if [ $1 == "13" ]; then
		conf=$(grep "Encoders 1 & 2" ./ingest-*.conf | sed "s/:.*//" | sed "s/.\///")
		echo $conf
	elif [ $1 == "24" ]; then
		conf=$(grep "Encoders 3 & 4" ./ingest-*.conf | sed "s/:.*//" | sed "s/.\///")
		echo $conf
	fi
	swap $conf
}

############################################################################
# Restart confs provided as args
# Globals:
#	None
# Arguments:
#	*.conf || list
############################################################################
function restart_fc () {
#	cd ~ltn
	for conf in $@; do
		echo "sudo -u ltn ./scripts_current/fcctl ./scripts_current/$conf restart";
	done
	echo -e "\n$message $@"
}

## Check command
if [ $# -lt 1 ]; then
	usage
fi

case $@ in
	-h | --help)
	 usage
	 ;;

	--auto)
		confs=$(for channel in $channels; do grep SEND_GROUP=$channel ./*.conf | sed "s/:.*//" | sed "s/.\///"; done)
		swap $confs
		restart_fc $confs
		;;

	-13)
		restart_fc $(find_conf 13)
		;;

	-24)
		restart_fc $(find_conf 24)
		;;

	$1)
		swap $1
		echo -e "\n$message $1"
		;;
esac 
