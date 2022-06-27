#!/usr/bin/env bash


#https://icgen5.artifactory.cc.bmwgroup.net/ui/native/ic-gen5-release-internal-local/gen22/11.30.0/Mgu22/cmake-Mgu22-ioc-m4-2m/bin/
echo =============================
echo This script is only to recover Broken MGU22/IDC/PADI samples
echo Required files are already kept locally 
echo =============================
echo Please enter target u want to flash IOC with UART
read target_connected

#required_idc_ioc=("11.30.0" "11.30.35" "11.40.0")
idc_ioc_array=("11.30.0")
required_idc_ioc=(${idc_ioc_array[@]})

mgu_ioc_array=("11.30.0")
required_mgu_ioc=(${mgu_ioc_array[@]})

padi_ioc_array=("11.30.0")
required_padi_ioc=(${padi_ioc_array[@]})

#You need for loop in case u need to multiple UART flashss
if [ "${target_connected^^}" == "IDC" ]; 
then
for release in "${idc_ioc_array[@]}"
        do
                echo $release
                if [ -d "/home/gui_pd_access/inder/utility_script/recover_broken_targets/idc/$release/DevFBL_B2" ]; then
                        rm -rf /home/gui_pd_access/inder/utility_script/recover_broken_targets/idc/$release/DevFBL_B2
                fi

                echo Extracting tar file
                tar -xvf /home/gui_pd_access/inder/utility_script/recover_broken_targets/idc/$release/DevFBL_B2.tar  --directory /home/gui_pd_access/inder/utility_script/recover_broken_targets/idc/$release/
                sleep 5
                echo giving access for flashing
                sudo chmod 777 /home/gui_pd_access/inder/utility_script/recover_broken_targets/idc/$release/DevFBL_B2/Linux/DEV_BL_pcclient_B2
                echo Making power supply off
                export PYTHONPATH=/home/gui_pd_access/inder/test_files/psu/
                cd /home/gui_pd_access/inder/test_files/psu
                sudo /home/gui_pd_access/inder/test_files/psu/psu.sh False
                echo $release UART Flashing is starting
                sleep 5
                sudo /home/gui_pd_access/inder/test_files/psu/psu.sh True & sudo /home/gui_pd_access/inder/utility_script/recover_broken_targets/idc/$release/DevFBL_B2/Linux/DEV_BL_pcclient_B2 -p /dev/ttyIOC -v 4M -wv /home/gui_pd_access/inder/utility_script/recover_broken_targets/idc/$release/bmw_idc_m7_4m_permissive_secure_boot_image.srec
                echo $release UART Flashing is completed
                sleep 5

        done

elif [ "${target_connected^^}" == "MGU" ]; 
then
for release in "${mgu_ioc_array[@]}"
        do
                echo $release
                if [ -d "/home/gui_pd_access/inder/utility_script/recover_broken_targets/mgu22/$release/DevFBL_B2" ]; then
                        rm -rf /home/gui_pd_access/inder/utility_script/recover_broken_targets/mgu22/$release/DevFBL_B2
                fi

                echo EXtracting tar file
                tar -xvf /home/gui_pd_access/inder/utility_script/recover_broken_targets/mgu22/$release/DevFBL_B2.tar --directory /home/gui_pd_access/inder/utility_script/recover_broken_targets/mgu22/$release/
                sleep 5
                echo giving access for flashing
                sudo chmod 777 /home/gui_pd_access/inder/utility_script/recover_broken_targets/mgu22/$release/DevFBL_B2/Linux/DEV_BL_pcclient_B2
                export PYTHONPATH=/home/gui_pd_access/inder/test_files/psu/
                cd /home/gui_pd_access/inder/test_files/psu
                sudo /home/gui_pd_access/inder/test_files/psu/psu.sh False
                echo $release UART Flashing is starting
                sleep 5
                sudo /home/gui_pd_access/inder/test_files/psu/psu.sh True & sudo /home/gui_pd_access/inder/utility_script/recover_broken_targets/mgu22/$release/DevFBL_B2/Linux/DEV_BL_pcclient_B2 -p /dev/ttyIOC -v 2M -wv /home/gui_pd_access/inder/utility_script/recover_broken_targets/mgu22/$release/bmw_mgu_m4_2m_permissive_secure_boot_image.srec
                echo $release UART Flashing is completed
                sleep 5

        done
elif [ "${target_connected^^}" == "PADI" ]; 
then
for release in "${padi_ioc_array[@]}"
        do
                echo $release
                if [ -d "/home/gui_pd_access/inder/utility_script/recover_broken_targets/padi/$release/DevFBL_B2" ]; then
                        rm -rf /home/gui_pd_access/inder/utility_script/recover_broken_targets/padi/$release/DevFBL_B2
                fi

                echo EXtracting tar file
                tar -xvf /home/gui_pd_access/inder/utility_script/recover_broken_targets/padi/$release/DevFBL_B2.tar --directory /home/gui_pd_access/inder/utility_script/recover_broken_targets/padi/$release/
                sleep 5
                echo giving access for flashings
                sudo chmod 777 /home/gui_pd_access/inder/utility_script/recover_broken_targets/padi/$release/DevFBL_B2/Linux/DEV_BL_pcclient_B2
                export PYTHONPATH=/home/gui_pd_access/inder/test_files/psu/
                cd /home/gui_pd_access/inder/test_files/psu
                sudo /home/gui_pd_access/inder/test_files/psu/psu.sh False
                echo $release UART Flashing is starting
                sleep 5
                sudo /home/gui_pd_access/inder/test_files/psu/psu.sh True & sudo /home/gui_pd_access/inder/utility_script/recover_broken_targets/mgu22/$release/DevFBL_B2/Linux/DEV_BL_pcclient_B2 -p /dev/ttyIOC -v 2M -wv /home/gui_pd_access/inder/utility_script/recover_broken_targets/padi/$release/bmw_mgu_m4_2m_permissive_secure_boot_image.srec
                echo $release UART Flashing is completed
                sleep 5

        done
else
        echo Please press mgu/idc/padi
fi
