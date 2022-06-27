#!/bin/bash
# upload.sh

set +v
DEV_BL_pcclient_B2 -p /dev/ttyS0 -v 2M -wv traveo2_m7_0+m0.srec
$?
