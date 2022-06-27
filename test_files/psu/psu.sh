
#!/bin/bash
usage() {
    cat <<EOM
    Usage:
    export PYTHONPATH=[DIR_PATH] && [DIR_PATH]/power_supply_control.sh True

EOM
    exit 0
}

[ -z $1 ] && { usage; }
python3 -c "from manson_hcs import MansonHCS as psu; psu(\"/dev/ttyUSB_PowerSupply\").enabled=$1;"


