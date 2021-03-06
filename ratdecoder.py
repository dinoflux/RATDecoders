#!/usr/bin/env python
import os
import sys
import importlib
import hashlib
import yara
import subprocess
import tempfile
from optparse import OptionParser

from decoders import JavaDropper
import json

__description__ = 'RAT Config Extractor'
__author__ = 'Kevin Breen, https://techanarchy.net, https://malwareconfig.com'
__version__ = '1.0'
__date__ = '2016/04'
rule_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'yaraRules', 'yaraRules.yar')

def unpack(raw_data):
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(raw_data)
    f.close()
    try:
        subprocess.call("(upx -d %s > /dev/null)" %f.name, shell=True)
    except Exception as e:
        print >> sys.stderr, 'UPX Error {0}'.format(e)
        return
    new_data = open(f.name, 'rb').read()
    os.unlink(f.name)
    return new_data


# Yara Scanner Returns the Rule Name
def yara_scan(raw_data):
    if raw_data is None:
        return
    yara_rules = yara.compile(rule_file)
    matches = yara_rules.match(data=raw_data)
    if len(matches) > 0:
        return str(matches[0])
    else:
        return


def run(raw_data, src_file_path=None):
    # Get some hashes
    md5 = hashlib.md5(raw_data).hexdigest()
    sha256 = hashlib.sha256(raw_data).hexdigest()

    print >> sys.stderr, "   [-] MD5: {0}".format(md5)
    print >> sys.stderr, "   [-] SHA256: {0}".format(sha256)

    # Yara Scan
    family = yara_scan(raw_data)


    # UPX Check and unpack
    if family == 'UPX':
        print >> sys.stderr, "   [!] Found UPX Packed sample, Attempting to unpack"
        raw_data = unpack(raw_data)
        family = yara_scan(raw_data)

        if family == 'UPX':
            # Failed to unpack
            print >> sys.stderr, "   [!] Failed to unpack UPX"
            return

    # Java Dropper Check
    if family == 'JavaDropper':
        print >> sys.stderr, "   [!] Found Java Dropped, attemping to unpack"
        raw_data = JavaDropper.run(raw_data)
        family = yara_scan(raw_data)

        if family == 'JavaDropper':
            print >> sys.stderr, "   [!] Failed to unpack JavaDropper"
            return

    if not family:
        print >> sys.stderr, "   [!] Unable to match your sample to a decoder"
        return

    # Import decoder
    try:
        module = importlib.import_module('decoders.{0}'.format(family))
        print >> sys.stderr, "[+] Importing Decoder: {0}".format(family)
    except ImportError:
        print >> sys.stderr, '    [!] Unable to import decoder {0}'.format(family)
        return { 'family': family, 'config': {'Error': 'Not supported'} }

    # Get config data
    try:
        # csandoval changes: AlienSpy support.
        # print 'Family:', family
        if family == 'AlienSpy':
            config_data = module.config(src_file_path)
        else:
            config_data = module.config(raw_data)
        # csandoval end changes.
    except Exception as e:
        raise
        print >> sys.stderr, 'Conf Data error with {0}. Due to {1}'.format(family, e)
        return ['Error', 'Error Parsing Config']

    # csandoval changes: Parser data
    # print 'Config Data:', config_data
    if isinstance(config_data, dict):
        for key, value in config_data.iteritems():
            #print value, type(value)
            if isinstance(value, str):
                config_data[key] = value.decode('UTF-8', errors='replace')
    # csandoval end changes.

    result_data = { 'family': family, 'config': config_data }
    return result_data




def print_output(config_dict, output, format='json'):
    if output:
        with open(output, 'a') as out:
            if format == 'json':
                json.dumps(config_dict, out, sort_keys=True, indent=4, separators=(',', ': '))
            else:
                print >> sys.stderr, "    [+] Printing Config to Output"
                for key, value in sorted(config_dict.iteritems()):
                    out.write("       [-] Key: {0}\t Value: {1}".format(key,value))
                out.write('*'*20)
                print >> sys.stderr, "    [+] End of Config"
    else:
        if format == 'json':
            print json.dumps(config_dict, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            print >> sys.stderr, "[+] Printing Config to screen"        
            for key, value in sorted(config_dict.iteritems()):
                print >> sys.stderr, "   [-] Key: {0}\t Value: {1}".format(key,value)
            print >> sys.stderr, "[+] End of Config"




if __name__ == "__main__":
    parser = OptionParser(usage='usage: %prog file / dir\n' + __description__, version='%prog ' + __version__)
    parser.add_option("-r", "--recursive", action='store_true', default=False, help="Recursive Mode")
    parser.add_option("-f", "--family", help="Force a specific family")
    parser.add_option("-l", "--list", action="store_true", default=False, help="List Available Decoders")
    parser.add_option("-o", "--output", help="Output Config elements to file.")
    (options, args) = parser.parse_args()

    # Print list
    if options.list:
        print >> sys.stderr, "[+] Listing Available Decoders"
        for filename in os.listdir('decoders'):
            print >> sys.stderr, "  [-] {0}".format(filename)
        sys.exit()

    # We need at least one arg
    if len(args) < 1:
        print >> sys.stderr, "[!] Not enough Arguments, Need at least file path"
        parser.print_help()
        sys.exit()

    # Check for file or dir
    is_file = os.path.isfile(args[0])
    is_dir = os.path.isdir(args[0])

    if options.recursive:
        if not is_dir:
            print >> sys.stderr, "[!] Recursive requires a directory not a file"
            sys.exit()

        # Read all the things
        for filename in os.listdir(args[0]):
            file_data = open(os.path.join(args[0], filename), 'rb').read()
            print >> sys.stderr, "[+] Reading {0}".format(filename)
            config_data = run(file_data)

    else:
        if not is_file:
            print >> sys.stderr, "[!] You did not provide a valid file."
            sys.exit()

        # Read in the file.
        file_data = open(args[0], 'rb').read()
        print >> sys.stderr, "[+] Reading {0}".format(args[0])
        config_data = run(file_data)
        print_output(config_data, options.output)
