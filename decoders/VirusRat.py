def config(data):
    dict = {}
    config = data.split("abccba")
    if len(config) > 5:
        dict["Domain"] = config[1]
        dict["Port"] = config[2]
        dict["Campaign Name"] = config[3]
        dict["Copy StartUp"] = config[4]
        dict["StartUp Name"] = config[5]
        dict["Add To Registry"] = config[6]
        dict["Registry Key"] = config[7]
        dict["Melt + Inject SVCHost"] = config[8]
        dict["Anti Kill Process"] = config[9]
        dict["USB Spread"] = config[10]
        dict["Kill AVG 2012-2013"] = config[11]
        dict["Kill Process Hacker"] = config[12]
        dict["Kill Process Explorer"] = config[13]
        dict["Kill NO-IP"] = config[14]
        dict["Block Virus Total"] = config[15]
        dict["Block Virus Scan"] = config[16]
        dict["HideProcess"] = config[17]
        return dict
    else:
        return None
