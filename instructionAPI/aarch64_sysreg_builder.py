import os
from os import path
from xml.dom.minidom import parse
import xml.dom.minidom
from collections import OrderedDict

sys_reg_dir = "/p/paradyn/arm/arm-download-1350222/AR100-DA-70000-r0p0-00rel10/AR100-DA-70000-r0p0-00rel10/SysReg_xml/ARMv8-SysReg-00bet12/SysReg_xml-00bet12"
reg_names = list()
reg_encodings = OrderedDict()

reg_names = [f.split('.')[0].split("AArch64-")[1] for f in os.listdir(sys_reg_dir) if (path.isfile(sys_reg_dir + os.sep + f) and f.find("AArch64") != -1)]

for name in reg_names:
    DOMTree = xml.dom.minidom.parse(sys_reg_dir + "/AArch64-" + name + ".xml")
    collection = DOMTree.documentElement

    encodings = collection.getElementsByTagName("encoding_param")
    encoding_dict = OrderedDict()

    for encoding in encodings:
	encoding_fieldname = encoding.getElementsByTagName("encoding_fieldname")[0].childNodes[0].data
	encoding_fieldvalue = encoding.getElementsByTagName("encoding_fieldvalue")[0].childNodes[0].data

	encoding_dict[encoding_fieldname] = encoding_fieldvalue

    encoding_val = list()
    for encoding_fieldname in encoding_dict:
	encoding_fieldvalue =  encoding_dict[encoding_fieldname]
	for c in encoding_fieldvalue:
	    encoding_val.append(c)
    
    try: 
        reg_encodings[name] = hex(int(''.join(str(i) for i in encoding_val), 2))
    except:
	encoding_str = ''.join(encoding_val)
	if len(encoding_str) < 1 or encoding_str.find("n") == -1:
	    print(name)
	    continue

	replace_parts = encoding_str.split("n", 1)[1].split('>')
	replace_list = list()
	
	for part in replace_parts:
	    if len(part) > 0 and part.find('<') != -1:
		bit_positions = part.split('<')[1].split(':')
		
		if len(bit_positions) == 2:
		    start_pos = int(bit_positions[1])
		    end_pos = int(bit_positions[0])
		else:
		    start_pos = end_pos = int(bit_positions[0])
		encoding_str = encoding_str.replace(part + ">", ''.join(['0'] * (end_pos - start_pos + 1)))
		
		for pos in range(start_pos, end_pos+1):
		    replace_list.append(pos)
	
	encoding_str = encoding_str.replace(':', '').replace('n', '')
	replace_list = sorted(replace_list, reverse=True)  
	
	max_val = 2**len(replace_list)
	for idx in range(0, max_val):
	    bin_arr = "{0:b}".format(idx).split()
	    cur_encoding = encoding_str

	    format_args = '%0' + str(len(replace_list)) + 'd'
	    bin_arr = str(format_args % int(''.join(bin_arr)))
	    
	    for val in replace_list:
		cur_encoding = cur_encoding[:(len(encoding_str) - 1 - int(val))] + bin_arr[len(replace_list) - 1 - int(val)] + cur_encoding[(len(encoding_str) - int(val)):]
	    #print(hex(int(cur_encoding, 2)))
	    reg_encodings[name.replace("n_", str(idx) + "_")] = hex(int(cur_encoding, 2))

for elem in reg_encodings:
    print("sysRegMap[" + reg_encodings[elem] + "] = aarch64::" + elem + ";");
