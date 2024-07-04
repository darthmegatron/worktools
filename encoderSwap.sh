#! /bin/bash
#
# Quickly change encoders and restart flowclients during OTTO/D2 maintenance

## Maintenance related channels
channels="230.0.187.68 230.0.187.18 230.0.187.70 230.0.187.16 230.0.187.69 230.0.187.17"

message="Encoders swapped and flowclient restarted for"
RED="\033[1;31m"
GREEN="\033[1;32m"
NOCOLOR="\033[0m"

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
	confs=()
	for conf in $@; do
		confs+=($conf)
		list=$(grep -e "RECEIVE_[AP]" $conf)
		for line in $list; do
			if [ ${line::1} = "#" ]; then
				sed -i "s/$line/${line:1}/g" $conf
			else
				sed -i "s/\b$line\b/#$line/g" $conf
			fi;
		done; 
	done
	restart_fc ${confs[@]}
}

function check_active_encoder () {
	active=($(grep -wB 1 "^RECEIVE_ADDRESS" $@ | grep Encoder | sed "s/.*#//"));
	echo ${active[0]} and ${active[1]} are active >&2
	echo ${active[@]}
}

function find_conf () {
	confs=$(grep "Encoder[13]" ./ingest-*.conf | sed "s/:.*//" | sed "s/.\///")
	active=($(check_active_encoder ${confs[@]}))

	if [[ $1 == "13" && ${active[0]} != "Encoder1" && ${active[1]} != "Encoder3" ]]; then
		echo -e ${GREEN}"Switching to encoders 1 and 3\n"${NOCOLOR} >&2
		swap $confs
	elif [[ $1 == "24" && ${active[0]} != "Encoder2" && ${active[1]} != "Encoder4" ]]; then
		echo -e ${GREEN}"Switching to encoders 2 and 4\n"${NOCOLOR} >&2
		swap $confs
	else
		echo -e ${RED}"No changes made\n"${NOCOLOR}
	fi
}

############################################################################
# Restart confs provided as args
# Globals:
#	None
# Arguments:
#	*.conf || list
############################################################################
function restart_fc () {
	if [ $# -gt 0 ]; then
#		cd ~ltn
		for conf in $@; do
			echo "sudo -u ltn ./scripts_current/fcctl ./scripts_current/$conf restart";
		done
		echo -e "\n$message $@"
	fi
}

## Check command
if [ $# -lt 1 ]; then
	usage
fi

case $@ in
	-h | --help)
		usage
	 	;;

	--test)
		find_conf 13
		;;

	--auto)
		confs=$(for channel in $channels; do grep SEND_GROUP=$channel ./*.conf | sed "s/:.*//" | sed "s/.\///"; done)
		swap $confs
		restart_fc $confs
		;;

	-13)
		find_conf 13
		;;

	-24)
		find_conf 24
		;;

	$1)
		swap $1
		echo -e "\n$message $1"
		;;
	
esac
