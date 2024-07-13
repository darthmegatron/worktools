#! /bin/bash
#
# Quickly change encoders and restart flowclients during OTTO/D2 maintenance

message="Encoders swapped and flowclient restarted for"
RED="\033[1;31m"
GREEN="\033[1;32m"
NOCOLOR="\033[0m"
BOLD="\033[1m"

############################################################################
# Print command usage to the terminal
# Outputs:
#	Writes command usage to stdout
############################################################################
function usage () {
	echo -e "usage: encoderSwap.sh [CONF FILE] [OPTION]\n"
	echo -e ${BOLD}"Description\n"${NOCOLOR}
	echo -e "This script is used to quickly swap between encoders 1 & 2, and 3 & 4, as they are commonly referred to during ABC OTTO maintenance.\nIf a conf file is provided to the script it will change the encoders for that file ONLY and the optional arguments are not used.\nLikewise, if the optional arguments are used, eg. -13, a conf file is not to be provided.\n\nThe options are as follows:\n	-13	Switch to encoders 1 and 3\n	-24	Switch to encoders 2 and 4"
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

#############################################################################
#Check which encoders are currently active in the flowclient confs
# Output:
#	array
############################################################################
function check_active_encoder () {
	active=($(grep -wB 1 "^RECEIVE_ADDRESS" $@ | grep Encoder | sed "s/.*#//"));
	echo ${active[0]} and ${active[1]} are active >&2
	echo ${active[@]}
}

function find_conf () {
	confs=$(grep "Encoder[13]" ./ingest-*.conf | sed "s/:.*//" | sed "s/.\///")
	active=($(check_active_encoder ${confs[@]}))

	if [ $1 == "13" ]; then
		if ! [[ ${active[@]} == "Encoder1 Encoder3" || ${active[@]} == "Encoder3 Encoder1" ]]; then
			echo -e ${GREEN}"Switching to encoders 1 and 3\n"${NOCOLOR} >&2
			swap $confs
		else
			echo -e ${RED}"No changes made\n"${NOCOLOR}
		fi
	elif [ $1 == "24" ]; then
		if ! [[ ${active[@]} == "Encoder2 Encoder4" || ${active[@]} == "Encoder4 Encoder2" ]]; then
			echo -e ${GREEN}"Switching to encoders 2 and 4\n"${NOCOLOR} >&2
			swap $confs
		else
			echo -e ${RED}"No changes made\n"${NOCOLOR}
		fi
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
	cd ~ltn
	if [ $# -gt 0 ]; then
		for conf in $@; do
			sudo -u ltn ./scripts_current/fcctl ./scripts_current/$conf restart;
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

	-13)
		find_conf 13
		;;

	-24)
		find_conf 24
		;;

	$1)
		swap $1
		;;

	*)
		usage
		;;
esac
