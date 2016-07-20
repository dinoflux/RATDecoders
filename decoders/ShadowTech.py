import os
import sys
import string
from operator import xor


# Main Decode Function Goes Here
'''
data is a read of the file
Must return a python dict of values
'''

new_line = '#-@NewLine@-#'
split_string = 'ESILlzCwXBSrQ1Vb72t6bIXtKRzHJkolNNL94gD8hIi9FwLiiVlrznTz68mkaaJQQSxJfdLyE4jCnl5QJJWuPD4NeO4WFYURvmkth8' # 
enc_key = 'pSILlzCwXBSrQ1Vb72t6bIXtKRzAHJklNNL94gD8hIi9FwLiiVlr' # Actual key is 'KeY11PWD24'

def config(data):
    raw_config = get_config(data)
    return parse_config(raw_config)

        
#Helper Functions Go Here

def get_config(data):
    config_list = []
    config_string = data.split(split_string)
    for x in range(1, len(config_string)):
        output = ""
        hex_pairs = [config_string[x][i:i+2] for i in range(0, len(config_string[x]), 2)]
        for i in range(0,len(config_string[x])/2):
            data_slice = int(hex_pairs[i], 16)#get next hex value
            key_slice = ord(enc_key[i+1])#get next Char For Key
            output += chr(xor(data_slice,key_slice)) # xor Hex and Key Char
        config_list.append(output)
    return config_list

# Returns only printable chars
def string_print(line):
    return ''.join((char for char in line if 32 < ord(char) < 127))

# returns pretty config
def parse_config(config_list):
    config_dict = {}
    config_dict['Domain'] = config_list[0]
    config_dict['Port'] = config_list[1]
    config_dict['CampaignID'] = config_list[2]
    config_dict['Password'] = config_list[3]
    config_dict['InstallFlag'] = config_list[4]
    config_dict['RegistryKey'] = config_list[5]
    config_dict['Melt'] = config_list[6]
    config_dict['Persistance'] = config_list[7]
    config_dict['Mutex'] = config_list[8]
    config_dict['ShowMsgBox'] = config_list[9]
    #config_dict['Flag5'] = config_list[10] # MsgBox Icon
    #config_dict['Flag6'] = config_list[11] # MsgBox Buttons
    config_dict['MsgBoxTitle'] = config_list[12]
    config_dict['MsgBoxText'] = config_list[13]
    return config_dict

def decrypt_XOR(enckey, data):                    
    cipher = XOR.new(enckey) # set the cipher
    return cipher.decrypt(data) # decrpyt the data