#!/bin/bash
# A tool to automate IOC updates for MGU, IDC, and RSE.

set -e

echo "FFP IOC Auto Update v2.0"
echo "If your SoC is not updated to 21w44.5-2 or later, exit now..."
echo "Press any key to continue..."
read -n 1 -s
echo "Continuing with flash..."

ssh_signature_file=~/.ssh/id_ed25519_mgu22

while [[ "$#" -gt 0 ]]; do
	case $1 in
		-u|--unit)
			unit=$(echo "$2" | awk '{print toupper($0)}')
			shift
			;;
		-i)
			ssh_signature_file="$2"
			shift
			;;
		*)
			echo "Invalid parameter: $1"
			echo "Usage: -u|--unit <MGU|IDC|RSE>"
			exit 1
			;;
	esac
	shift
done

./get-iocs.sh -u $unit

# List of IOCs to be flashed
mgu_ioc=("11.19.6" "11.24.5" "11.26.2")
idc_ioc=("11.20.13" "11.22.34" "11.26.2")
rse_ioc=("11.19.4" "11.24.4" "11.28.1")

case $unit in
	"MGU")
		for i in "${mgu_ioc[@]}"; do
			echo "Flashing MGU with IOC $i"
			./update-ioc.sh -t "ioc_releases/$i/bmw_mgu_m4_2m.tar" -s "ioc_releases/$i/bmw_mgu_m4_2m.sig" -u MGU -i $ssh_signature_file
		done
		;;
	"IDC")
		for i in "${idc_ioc[@]}"; do
			echo "Flashing IDC with IOC $i"
			./update-ioc.sh -t "ioc_releases/$i/bmw_idc_m7_4m.tar" -s "ioc_releases/$i/bmw_idc_m7_4m.sig" -u IDC -i $ssh_signature_file
		done
		;;
	"RSE")
		for i in "${rse_ioc[@]}"; do
			echo "Flashing RSE with IOC $i"
			./update-ioc.sh -t "ioc_releases/$i/bmw_mgu_m4_2m.tar" -s "ioc_releases/$i/bmw_mgu_m4_2m.sig" -u RSE -i $ssh_signature_file
		done
		;;
	*)
		echo "Invalid unit provided. Valid options are MGU, IDC, or RSE."
		exit 1
		;;
esac

echo "Flashing finished successfully"
