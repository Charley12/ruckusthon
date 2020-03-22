__author__ = "Richard O'Dwyer"
__email__ = "richard@richard.do"
__license__ = "None"

import re
from operator import itemgetter
import numpy as np
import sys

def process_log(log):
    requests = get_requests(log)
    files = get_files(requests)
    totals = file_occur(files)
    return totals

def get_requests(f):
    log_line = f.read()
    pat = (r''
           '(\d+.\d+.\d+.\d+)\s-\s-\s' #IP address
           '\[(.+)\]\s' #datetime
           '"(?:GET|POST|PUT|DELETE)\s(.+)\s\w+/.+"\s' #requested file
           '(\d+)\s' #status
           '(\d+)\s' #bandwidth
           '"(.+)\"\s' #referrer
           '"(.+)\"\s' #referrer
           '"(.+)"' #user agent
        )
    requests = find(pat, log_line)
    return requests

def find(pat, text):
    match = re.findall(pat, text)
    if match:
        return match
    return False

def correctUrl(url):
    if("//" in url):
        url = url.replace("//","/")
    if(url.find("?")!= -1):
        url = url[0:url.find("?")]
    return url

def correctVersionAndId(url, isCorrectVersion):
    items = url.split('/')
    #correct version
    if(isCorrectVersion):
        for i in range(len(items)):
            if(('v' in items[i]) and ('_' in items[i])):
                items[i] = "{api_version}"
    
    #correct id except wlans id
    for i in range(len(items)):
        if("-" in items[i]):
            items[i] = "{" + items[i-1] + "_id}" 

    #correct wlans id
    if(items[len(items)-2] == "wlans"):
        items[len(items)-1] = "{wlans_id}"
      
    t = tuple(items)
    return "/".join(t)

def get_files(requests):
    #get requested files with req
    requested_files = []
    for req in requests:
        # req[2] for req file match, change to
        # data you want to count totals

        url = correctUrl(req[2])
        url = correctVersionAndId(url, True)

        requested_files.append(url)
    return requested_files

def correcrAll(log, normalizeVersion, file):
    requests = get_requests(log)

    for req in requests:
        # req[2] for req file match, change to
        # data you want to count totals
        url = correctUrl(req[2])
        url = correctVersionAndId(url, normalizeVersion)
        
        tup_list = list(req)
        
        tup_list[1] = "- ["+ tup_list[1] +"]"
        tup_list[2] = "\"" + url + "\""

        tup_list[5] = "\"" + tup_list[5] + "\""
        tup_list[6] = "\"" + tup_list[6] + "\""
        tup_list[7] = "\"" + tup_list[7] + "\""

        
        print(tup_list)

        file.write(" ".join(tuple(tup_list))+ "\n")
        
      
def file_occur(files):
    # file occurrences in requested files
    d = {}
    for file in files:
        d[file] = d.get(file,0)+1
    return d

if __name__ == '__main__':

    normalizeVersion = ""

    if (len(sys.argv)<2):
        print("please enter access log file path")
        exit()

    file_path = sys.argv[1]
    

    if (len(sys.argv)>2):
        normalizeVersion = sys.argv[2]

    f = open("out.log", "w")
    #nginx access log, standard format
    log_file = open(file_path, 'r')
    
    if(normalizeVersion == "needVersion"):
        correcrAll(log_file, False ,f)
    else:
        correcrAll(log_file, True ,f)

    f.close()

    print("*****************************************")
    print("*******please check the out.log**********")
    print("*****************************************")


   
