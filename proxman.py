#!/usr/bin/env python3

# (c) Péter Bohner; aka. nogatco
# LICENSE GPL-3.0
# PROXMAN is a tool to manage proxy servers via the command line.

# PROXMAN - Main

#               ---imports---
import sys
import os

#               ---function definitions---

#       ---functions for error handling---

#function: print usage and exit
#params: none
def print_usage():
    print("PROXMAN is a tool to manage proxy servers.")
    print("USAGE: [command] [args]")    
    print("COMMANDS:")
    print("help: print this")
    print("install: sets everything up for proxman. only needs to be run once.")
    print("current: prints current active proxy configuration")
    print("list: lists all defined proxy servers.")
    print("create: creates new proxy configuration. argument: [optional] config name")
    print("load: loads a proxy. argument: [required]config name: if 'none' then no proxy configuration will be used ")
    sys.exit(1)

#function: handles and prints exceptions
#param: exeption
#valid exeptions:   config_file_not_found
#                   permission_denied
def exception_handler(exception="unknown"):
    if exception=="config_file_not_found":
        print("config file not found. run install command again")
    if exception=="permisson_denied":
        print("permission denied. run as super user.")
    else:
        print("unknown exeption: ", exception)
    sys.exit(1)

#       ---helper functions---

#function: creates a file 
#params: fname: filename&path
def create_file(fname):
    fi = open(fname, 'a')
    fi.close()

#function: prepend some text to a file
#params: fname: file name&path
#        data: string to prepend
#from: SO: https://stackoverflow.com/questions/11229780/adding-text-and-lines-to-the-beginning-of-a-file-python
def prepend_to_file(fname, data):
        f = open(fname,'r+')
        lines = f.readlines() # read old content
        f.seek(0) # go back to the beginning of the file
        f.write(data) # write new content at the beginning
        for line in lines: # write old content after new
             f.write(line)
        f.close()

#       ---functions for commands---

#function: install proxman
#params: none
def install():

    # At the beginning to immediatly throw error if permission denied
    try:
        #add to apt.conf
        if os.path.exists("/etc/apt"):  # apt is installed
            #if exists back up apt.conf
            if os.path.exists("/etc/apt/apt.conf"):
                os.system("mv  /etc/apt/apt.conf /etc/apt/apt.conf.back")
            #create blank apt.conf
            create_file("/etc/apt/apt.conf")
            print("added apt.conf")
    except PermissionError:
        exception_handler("permisson_denied")

    #create files
    #expanduser is used for relative paths
    create_file(os.path.expanduser("~/.proxmanrc"))

    #create proxy config storage folder
    os.system("mkdir ~/.proxman-proxies")

    #add to .zshrc & .bashrc
    proxmanrc_source="source ~/.proxmanrc \n"
    if os.path.exists(os.path.expanduser("~/.zshrc")):
        prepend_to_file(os.path.expanduser("~/.zshrc"), proxmanrc_source)
        print("added to .zshrc")
    if os.path.exists(os.path.expanduser("~/.bashrc")):
        prepend_to_file(os.path.expanduser("~/.bashrc"), proxmanrc_source)
        print("added to .bashrc")
    
    print("sucess")
    sys.exit(0)

#function: print current active proxy
#params: none
def current():
    #there's a current active file: .active-proxy
    if os.path.isfile(os.path.expanduser("~/.proxman-proxies/.active-proxy")):
        os.system("cat ~/.proxman-proxies/.active-proxy")
    #if it doesn't exists there's no proxy set up
    else:
        print("no active proxy set.")
    sys.exit(0)

#function: lists all available proxies
#params: none
def list_proxies():
    #why not use the easy way
    os.system("ls ~/.proxman-proxies")
    sys.exit(0)

#function: creates a new proxy configuration
#params: none; uses sys.argv
def create():
    print("create not implemented. exiting.")
    sys.exit(0)

#function: loads a proxy configuration
#params: none; uses sys.argv
def load():
    print("load not implemented. exiting.")
    sys.exit(0)


#       --main function / misc---

#function: parses command given and executes correct function
#params: none; uses sys.argv
def parse_commands():
    # no command entered
    if len(sys.argv)<2:
        print("no command given.")
        print_usage()
    #call appropriate function for command entered
    if str(sys.argv[1]).lower()=="help":
        print_usage()
    elif str(sys.argv[1]).lower()=="install":
        install()
    elif str(sys.argv[1]).lower()=="current":
        current()
    elif str(sys.argv[1]).lower()=="list":
        list_proxies()
    elif str(sys.argv[1]).lower()=="create":
        create()
    elif str(sys.argv[1]).lower()=="load":
        load()    
    else:
        print("unknown command: ", sys.argv[1])
        print_usage()

#               ---class definitions---

#class: stores a proxy configuration as an object
class proxy():
    
    #function: constructor; initializes this instance from lines of config file
    #param: lines: lines from config file; if none: nothing is done; You need to call
    #                                                                create_proxy
    def __init__(self, lines=None):
        if lines is not None:
            print("sth")
    #function: init
    def create_proxy(proxy_type, proxy_ip, proxy_port, 
                     proxy_user=None, proxy_password=None):
        print("not implemented")

#               ---program execution---

parse_commands()
