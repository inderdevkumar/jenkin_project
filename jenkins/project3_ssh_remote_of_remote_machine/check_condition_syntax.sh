#!/usr/bin/env bash

#TARGET="mgu"
while true;
do

echo "Enter the user name: "
read TARGET
if [[ "$TARGET"  == "mgu" || "$TARGET" == "idc" ]] ;then
#if [[ "$TARGET"  == "mgu" ]] ;then
        echo -e "\n\n=========== Check for SW Version ===================="
        cat /etc/os-release
	echo -e "\n\n=========== Check for SW Version ===================="
        uptime
	echo -e "\n\n=========== Check for SW Version ===================="
	whoami
else
        echo "Else Loop"
	echo $TARGET
fi
done
