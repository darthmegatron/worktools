#! /bin/bash

## Maintenance related channels
channels="230.0.187.68 230.0.187.18 230.0.187.70 230.0.187.16 230.0.187.69 230.0.187.17"

## Usage
function usage () {
	echo "Usage: encoderSwap.sh [CONF FILE]... [OPTION]..."
	echo "Options:"
#	echo "	-p	Swap RECEIVE_PORT Only (Useful in cases like changing TBD or Charge to Protect)"
	echo "	--auto Swap RECEIVE_ADDRESS and RECEIVE_PORT for all OTTO channels on the appliance. When using"
	echo "			the --auto option you do not need to supply a conf file."
	echo " 			eg. encoderSwap.sh --auto"
	exit
}

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

function findconf () {
	if [ $1 == "13" ]; then
		conf=$(grep "Encoders 1 & 2" ./ingest-*.conf | sed "s/:.*//")
		swap $conf
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

	--auto)
		confs=$(for channel in $channels; do grep SEND_GROUP=$channel ./*.conf | sed "s/:.*//"; done)
		swap $confs
		;;

	-13)
		echo $(findconf 13)
		;;

	-24)
		echo "test 2 & 4"
		;;

	$1)
		swap $1
		;;
esac

## Restart flowclient and return to the scripts_current dir
#cd ~ltn && sudo -u ltn ./scripts_current/fcctl ./scripts_current/$1 restart &&
#sleep 3
#clear && ps aux | grep bash_runner | grep -e "-ra"
#cd ~ltn/scripts_current
