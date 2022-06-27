#!/bin/bash

ssh_signature_file=~/.ssh/id_ed25519_mgu22

while [[ "$#" -gt 0 ]]; do
	case $1 in
		-t|--tar)
			tar="$2"
			shift
			;;
		-s|--sig)
			sig="$2"
			shift
			;;
		-u|--unit)
			unit=$(echo "$2" | awk '{print toupper($0)}')
			shift
			;;
		-i)
			ssh_signature_file="$2"
			shift
			;;
		*)
			echo "Unknown parameter passed: $1"
			exit 3
			;;
	esac
	shift
done

if [ -z "$tar" ]; then
	echo "You must provide a value for the tarball file using --tar"
	exit 1
fi

if [ -z "$sig" ]; then
	echo "You must provide a path for the signature file using --sig"
	exit 1
fi

if [ -z "$unit" ]; then
	echo "You must provide a value for --unit such as MGU, IDC, or RSE"
	exit 1
fi

case $unit in
	"MGU"|"IDC")
		target_ip="160.48.199.99"
		;;
	"RSE")
		target_ip="160.48.199.40"
		;;
	*)
		echo "Invalid unit type."
		echo "Valid types are MGU, IDC, or RSE."
		exit 1
esac

echo "Unit type: ${unit}"
echo "IOC tarball: ${tar}"
echo "IOC signature: ${sig}"
echo ""
echo "Using SSH signature file: ${ssh_signature_file}"

if [ ! -f $ssh_signature_file ]; then
	echo ""
	echo "Warning, SSH signature file is missing."
	echo "This script will fail on releases after 22w04 without it."
	echo ""
fi

wait_per_iter_sec=5
max_timeout_sec=60
waited_sec=0

echo "Connecting to unit..."
while [ $waited_sec -lt $max_timeout_sec ]; do
	sleep $wait_per_iter_sec
	ping -c1 -W5 $target_ip 2>&1 > /dev/null
	if [ $? -eq 0 ]; then
		break
	fi
	waited_sec=$(( waited_sec + wait_per_iter_sec ))
done

# Check for timeout
if [ $waited_sec -ge $max_timeout_sec ]; then
	echo "Error: Connection Timed out"
	exit 1
fi

set -e
echo "Copying files..."
scp -i $ssh_signature_file $tar root@$target_ip:/tmp
scp -i $ssh_signature_file $sig root@$target_ip:/tmp

ssh -i $ssh_signature_file root@$target_ip "systemctl stop nodestatemanager"

echo "Currently installed IOC version:"
ssh -i $ssh_signature_file root@$target_ip "ffptool /usr/lib/libffp_ioc.so.0 sw-version 0" | grep "SW version"

echo "Updating IOC..."
ssh -i $ssh_signature_file -t root@$target_ip "ffptool /usr/lib/libffp_ioc.so.0 flash /tmp/$(basename ${tar}) /tmp/$(basename ${sig})"

# Restart Unit
ssh -i $ssh_signature_file root@$target_ip "systemctl start nodestatemanager"
while [[ $(ssh -i $ssh_signature_file root@$target_ip systemctl is-active --quiet nodestatemanager) -ne 0 ]]; do
	sleep 1
done

echo "Rebooting unit..."
ssh -i $ssh_signature_file root@$target_ip "nsm_control --r 7 > /dev/null 2>&1"

