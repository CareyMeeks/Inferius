#!/usr/bin/env python3

import argparse
import os
import shutil
from resources import ipsw, patch
import sys
import subprocess
import requests
import platform

if platform.system() == 'Darwin':
    pass
else:
    exit("This script can only be ran on macOS. Please run this on a macOS computer.")

parser = argparse.ArgumentParser(description='Inferius - Create and restore custom IPSWs to your 64bit iOS device!', usage="./inferius.py -d 'device' -i 'iOS Version' -f 'IPSW' [-v]")
parser.add_argument('-d', '--device', help='Your device identifier (e.g. iPhone10,2)', nargs=1)
parser.add_argument('-i', '--version', help='The version of your stock IPSW', nargs=1)
parser.add_argument('-f', '--ipsw', help='Stock IPSW to create into a custom IPSW', nargs=1)
parser.add_argument('-v', '--verbose', help='Print verbose output for debugging', action='store_true')
args = parser.parse_args()

if args.ipsw:
    if args.device:
        pass
    else:
        sys.exit('Error: You must specify a device identifier with -d!\nExiting...')
    if args.version:
        version_str = args.version[0]
        if version_str.startswith('10.'):
            sys.exit('Error: iOS 10.x IPSWs are not currently supported!\nExiting...')
    else:
        sys.exit('Error: You must specify an iOS version with -i!\nExiting...')
    if args.verbose:
        print('[VERBOSE] Checking for required dependencies...')
    ldid_check = subprocess.Popen('/usr/bin/which ldid2', stdout=subprocess.PIPE, shell=True) # Dependency checking
    ldid_check.wait()
    output = str(ldid_check.stdout.read())
    if len(output) == 3:
        sys.exit('ldid not installed! Please install ldid from Homebrew, then run this script again.')
    if os.path.exists(f'work'): # In case work directory is still here from a previous run, remove it
        shutil.rmtree(f'work')
    print(f'Finding Firmware bundle for:\nDevice: {args.device[0]}\niOS: {args.version[0]}')
    if args.verbose:
        firmware_bundle = ipsw.find_bundle(args.device[0], args.version[0], 'yes')
    else:
        firmware_bundle = ipsw.find_bundle(args.device[0], args.version[0])
    if args.verbose:
        print(f'extracting IPSW: {args.ipsw[0]}')
        ipsw_dir = ipsw.extract_ipsw(args.ipsw[0], 'yes')
    else:
        ipsw_dir = ipsw.extract_ipsw(args.ipsw[0])
    print('IPSW extracted! Applying patches to bootchain...')
    if args.verbose:
        patch.patch_bootchain(firmware_bundle, ipsw_dir, 'yes')
    else:
        patch.patch_bootchain(firmware_bundle, ipsw_dir)
    print('Grabbing latest LLB and iBoot to put into custom IPSW...')
    ipsw.grab_latest_llb_iboot(args.device[0], ipsw_dir, firmware_bundle)
    print('Packing everything into custom IPSW...')
    ipsw_name = ipsw.make_ipsw(ipsw_dir, firmware_bundle)
    print(f'Done!\nCustom IPSW at: {ipsw_name}')
    print('Cleaning up...')
    shutil.rmtree('work')
else:
    exit(parser.print_help(sys.stderr))
