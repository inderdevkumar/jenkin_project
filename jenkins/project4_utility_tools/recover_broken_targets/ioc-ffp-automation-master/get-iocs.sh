#!/bin/bash

# Additional IOC versions can be added to the following arrays
required_mgu_ioc=("11.19.6" "11.24.5" "11.26.2")
required_idc_ioc=("11.20.13" "11.22.34" "11.26.2")
required_rse_ioc=("11.19.4" "11.24.4" "11.28.1")

while [[ "$#" -gt 0 ]]; do
	case $1 in
		-u|--unit)
			unit=$(echo "$2" | awk '{print toupper($0)}')
			shift
			;;
		*)
			echo "Unknown parameter: $1"
			exit 1
			;;
	esac
	shift
done

case $unit in
	"MGU") required_ioc=(${required_mgu_ioc[@]}) ;;
	"IDC") required_ioc=(${required_idc_ioc[@]}) ;;
	"RSE") required_ioc=(${required_rse_ioc[@]}) ;;
	*) echo "Invalid unit provided. Valid options are MGU, IDC, or RSE"; exit 1 ;;
esac

if [ "$unit" == "MGU" ] || [ "$unit" == "RSE" ]; then
	for release in "${required_ioc[@]}"
	do
		mkdir -p ioc_releases/$release

		if [[ ! -f "ioc_releases/${release}/bmw_mgu_m4_2m.sig" ]]; then
			wget -c "https://icgen5.artifactory.cc.bmwgroup.net/artifactory/ic-gen5-release-internal-local/gen22/$release/Mgu22/cmake-Mgu22-ioc-m4-2m/bin/bmw_mgu_m4_2m.sig" -P ioc_releases/$release
		fi
		if [[ ! -f "ioc_releases/${release}/bmw_mgu_m4_2m.tar" ]]; then
			wget -c "https://icgen5.artifactory.cc.bmwgroup.net/artifactory/ic-gen5-release-internal-local/gen22/$release/Mgu22/cmake-Mgu22-ioc-m4-2m/bin/bmw_mgu_m4_2m.tar" -P ioc_releases/$release
		fi
	done

elif [ "$unit" == "IDC" ]; then
	for release in "${required_ioc[@]}"
	do
		mkdir -p ioc_releases/$release

		if [[ ! -f "ioc_releases/${release}/bmw_idc_m7_4m.sig" ]]; then
			wget -c "https://icgen5.artifactory.cc.bmwgroup.net/artifactory/ic-gen5-release-internal-local/gen22/$release/Idc/cmake-Idc-ioc-m7-4m/bin/bmw_idc_m7_4m.sig" -P ioc_releases/$release
		fi

		if [[ ! -f "ioc_releases/${release}/bmw_idc_m7_4m.tar" ]]; then
			wget -c "https://icgen5.artifactory.cc.bmwgroup.net/artifactory/ic-gen5-release-internal-local/gen22/$release/Idc/cmake-Idc-ioc-m7-4m/bin/bmw_idc_m7_4m.tar" -P ioc_releases/$release
		fi
	done

fi

