Typical usage to flash an application file: 

With console open in:
    Windows folder -- (example for COM5):
    	.\DEV_BL_pcclient_B2.exe  -p COM5  -v 2M  -wv srec_file.s19

    Linux folder -- (example for ttyS0):
        ./DEV_BL_pcclient_B2  -p /dev/ttyS0  -v 2M  -wv srec_file.s19
	(make sure you have permissions for the port or use sudo before)



Usage description:

usage: DEV_BL_pcclient_B2.exe [-h] -p PORT (-w WRITE | -wv WRITEVERIFY | -r)
                              [-v {8M,2M}] [-B NBYTES] [-addr ADDRESS] [-s]

MGU22 Development Flash BootLoader Script ------ Version: 0.4.2

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Port used for UART communication (e.g. COM5,
                        /dev/ttyS0)
  -w WRITE, --write WRITE
                        Use to write SREC image (e.g. -w IOC.srec)
  -wv WRITEVERIFY, --writeVerify WRITEVERIFY
                        Use to write SREC image and then verify success of
                        flashing operation. (e.g. -wv IOC.srec)
  -r, --read            Use to READ Code Flash
  -v {8M,2M}, --version {8M,2M}
                        Tgt memory version. [8M || 2M]. Required if -w or -wv
                        is choosen
  -B NBYTES, --nbytes NBYTES
                        Number of bytes to be read from memory. 1Byte
                        hexadecimal value (e.g. 0x10 to read 16 bytes).
                        Argument only required if -r is given
  -addr ADDRESS, --address ADDRESS
                        Starting address of the memory to be read. 4Byte
                        hexadecimal value (e.g. 0x10088000). Argument only
                        required if -r is given
  -s, --silent          Use for silent mode
