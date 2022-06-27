# IOC FFP Automation

For up-to-date IOC flashing information, visit: https://asc.bmwgroup.net/wiki/display/MGU22/IOC+soft-bricking+issue

## Updating for IOC security requirements

1. Make sure your unit is running SOC 21w44.5-2 or greater.
2. Run `./auto-update.sh -u <MGU|IDC|RSE>`

### SSH Security Note

On SOC software 22w04 or newer, you will need to have the required SSH key downloaded in order to connect to your unit.
This script will look in `~/.ssh/` for the file by default.
If you want to use a custom path, you can use the `-i` flag followed by the path to your SSH key file.

## Updating with custom IOC versions

### Automated version

If you want to update your IOC with multiple versions, for example you want to write the security features but you want to end on a different version, you can follow the steps below.

1. Edit the list of IOCs that need to be flashed in `auto-update.sh` for your specific unit
2. If new IOCs need to be downloaded, edit the list for your unit in `get-iocs.sh`
3. Run `./auto-update.sh -u <MGU|IDC|RSE>`
4. Optional: use `-i` if your SSH key is not in the default `~/.ssh/` location.

### Manual version

If you want to update your IOC with a single new version, you can run:
```
update-ioc.sh -u <MGU|IDC|RSE>
	-t path/to/tarball
	-s path/to/signature
	-i path/to/ssh/key
```


# Planned additions

1. Allow flashing custom IOC versions by passing the number to `update-ioc.sh`

# My Command auto-update.sh
./auto-update.sh -u RSE -i /home/gui_pd_access/inder/test_files/id_ed25519_mgu22

#My Command update.sh
./update-ioc.sh -u RSE -t /home/gui_pd_access/inder/gui_pd_access_nuc_worker/recover_broken_padi_with_uart/gen22_mb_dev_flash/bmw_rse22_padi-pu2207-images_userdebug-22w23.7-1-nodex_A_22w23.3-1-11/mgu22/ioc/b2/bmw_mgu_m4_2m_11.50.0_0_firmware.tar -s /home/gui_pd_access/inder/gui_pd_access_nuc_worker/recover_broken_padi_with_uart/gen22_mb_dev_flash/bmw_rse22_padi-pu2207-images_userdebug-22w23.7-1-nodex_A_22w23.3-1-11/mgu22/ioc/b2/bmw_mgu_m4_2m_11.50.0_0_firmware.sig -i /home/gui_pd_access/inder/test_files/id_ed25519_mgu22
