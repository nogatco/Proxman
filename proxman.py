#!/usr/bin/env python3

# (c) Péter Bohner; aka. nogatco
# LICENSE GPL-3.0
# PROXMAN is a tool to manage proxy servers via the command line.

# PROXMAN - Main

#               ---imports---
import sys
import os
import re
import urllib.parse
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
#valid exeptions:   file_not_found
#                   permission_denied
#                   invalid_name
#                   invalid_input_format
#                   name_taken
#                   parameter missinf
def exception_handler(exception="unknown"):
    if exception=="config_file_not_found":
        print("config file not found. run install command again")
    elif exception=="permisson_denied":
        print("permission denied. run as super user.")
    elif exception=="invalid_name":
        print("This is an invalid name for a proxy config. The name may only contain:")
        print("letters; numbers; hypen")
        print("And may not be called: 'none' ")
    elif exception=="invalid_input_format":
        print("input format is invalid.")
    elif exception=="name_taken":
        print("this name is already taken. Choose a different one.")
    elif exception=="parameter_missing":
        print("missing parameter. invalid usage.")
        print_usage()
    else:
        print("unknown exeption: ", exception)
    sys.exit(1)

#       ---helper functions---

#function: creates a file 
#params: fname: filename&path
def create_file(fname,sudo=False):
    if sudo == True:
        os.system("sudo touch "+fname)
    else:
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

#function: validates if name given is valid for a proxy config.
#param: name: the name to validate
def validate_name(name):
    #regex for Alphanumeric and '-' characters
    reg = re.compile(r'[\w-]+$')
    #if invalid
    if reg.match(name) is None:
        return False
    else:
        if name=="none":
            return False
        else:
            return True

#function: saves proxy config in config folder
#params: proxy_obj: Proxy object
#        name: name of config
def save_proxy(proxy_obj, name):
    fi = open(os.path.expanduser("~/.proxman-proxies/"+name),"w+")
    for ptype in proxy_obj.proxy_type:
        fi.write(ptype+" ")
    fi.write("\n")
    fi.write(proxy_obj.proxy_ip+"\n")
    fi.write(proxy_obj.proxy_port+"\n")
    if proxy_obj.proxy_user is not None:
        fi.write(proxy_obj.proxy_user+"\n")
        fi.write(proxy_obj.proxy_password+"\n")
    fi.close()

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
                os.system("sudo mv  /etc/apt/apt.conf /etc/apt/apt.conf.back")
            #create blank apt.conf
            create_file("/etc/apt/apt.conf", True)
            print("added apt.conf")
    except PermissionError:
        exception_handler("permisson_denied")
    #these chowns are here, because sometimes the permissions get messed up.
    #chmods for the same reason
    os.system("sudo chown $(whoami) /etc/apt/apt.conf")
    os.system("sudo chmod -R 777 /etc/apt/apt.conf")
    #create files
    #expanduser is used for relative paths
    create_file(os.path.expanduser("~/.proxmanrc"))
    os.system("sudo chown $(whoami) ~/.proxmanrc")
    os.system("sudo chmod 777 ~/.proxmanrc")
    #create proxy config storage folder
    os.system("mkdir ~/.proxman-proxies")
    os.system("sudo chown $(whoami) ~/.proxman-proxies")
    os.system("sudo chmod -R 777 ~/.proxman-proxies")
    #add to .zshrc & .bashrc
    proxmanrc_source="source ~/.proxmanrc \n"
    if os.path.exists(os.path.expanduser("~/.zshrc")):
        prepend_to_file(os.path.expanduser("~/.zshrc"), proxmanrc_source)
        print("added to .zshrc")
    if os.path.exists(os.path.expanduser("~/.bashrc")):
        prepend_to_file(os.path.expanduser("~/.bashrc"), proxmanrc_source)
        print("added to .bashrc")
    #add +x to all files
    os.system("chmod +x proxman.py")
    os.system("chmod +x update-proxy-env-bash")
    os.system("chmod +x update-proxy-env-zsh")
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
    #why not use the easy way; just list directory.
    os.system("ls ~/.proxman-proxies")
    sys.exit(0)

#function: creates a new proxy configuration
#params: none; uses sys.argv
def create():
    name=""
    #if name given as parameter
    if len(sys.argv) > 2:
        name = sys.argv[2]
    else:
        name = input("Name of config: ")
    #if the name is invalid; call the exception handler
    if validate_name(name) == False:
        exception_handler("invalid_name")
    #if name is taken call exception handler
    if os.path.isfile(os.path.expanduser("~/.proxman-proxies/"+name)):
        exception_handler("name_taken")
    #get other info:
    
    #proxy type
    proxy_type_in = input("Type of proxy[http;https;ftp;] in a space separated list :")
    if proxy_type_in=="":
        exception_handler("invalid_input_format")
    #check if input is correct; else throw error
    proxy_type = proxy_type_in.split(" ")
    for pt in proxy_type:
        if pt!="http" and pt!="https" and pt!="ftp":
            exception_handler("invalid_input_format")
    #split to list
    
    
    #proxy ip
    proxy_ip = input("proxy ip: ")
    #check if input matches regex; else throw error
    reg_proxy_ip = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    if reg_proxy_ip.match(proxy_ip) is None:
        exception_handler("invalid_input_format")
    
    #proxy port
    proxy_port = input("proxy port: ")
    #check if port entered is a valid number; if not, throw exception
    if proxy_port.isdigit() == False:
        exception_handler("invalid_input_format")
    
    #proxy username&password
    proxy_user_in = input("proxy username(if not required; leave blank):")
    proxy_user = None
    proxy_password = None
    if proxy_user_in != "":
        #url-escape special characters
        proxy_user=urllib.parse.quote(proxy_user_in)
        #password
        proxy_password_in = input("Proxy password:")
        #check that input is not empty; else throw error
        if proxy_password_in == "":
            print("password can not be blank")
            exception_handler("invalid_input_format")
        #url-escape special characters
        proxy_password = urllib.parse.quote(proxy_password_in)
    
    #create proxy object
    proxy_obj = Proxy()
    proxy_obj.create_proxy(proxy_type, proxy_ip, proxy_port, 
                           proxy_user, proxy_password)
    #save
    save_proxy(proxy_obj,name)
    
    sys.exit(0)

#function: loads a proxy configuration
#params: none; uses sys.argv
def load():
    #check if parameter given
    if len(sys.argv) < 3:
        exception_handler("parameter_missing")

    #fix ******* apt.conf permissions
    os.system("sudo chmod 777 /etc/apt/")

    #check if parameter is none; if true, remove proxy config
    if sys.argv[2] == "none":
        os.system('printf \'http_proxy=""\nexport https_proxy=""\nexport ftp_proxy=""\n\' > ~/.proxmanrc')
        os.system("sudo rm -f /etc/apt/apt.conf")
        os.system("sudo printf '' >/etc/apt/apt.conf")
        sys.exit(0)
    #check if file exists
    if os.path.isfile(os.path.expanduser("~/.proxman-proxies/"+str(sys.argv[2]))) == False:
        exception_handler("file_not_found")
    #create proxy object
    fi = open(os.path.expanduser("~/.proxman-proxies/"+str(sys.argv[2])),"r")
    #read().splitlines is used instead of readlines, 
    # in order to remove the \n at the end of lines
    proxy_obj = Proxy(fi.read().splitlines())
    fi.close()

    #edit .proxmanrc
    #craft data
    data = "#!/usr/bin/env bash\n"
    for pt in proxy_obj.proxy_type:
        #still proxy_type contains '' as it's last item; 
        #this line filters everything invalid.
        if pt=="http" or pt=="https" or pt=="ftp":
            data += "export "+pt+"_proxy='"+pt+"://"
            if proxy_obj.proxy_user is not None:
                data += proxy_obj.proxy_user+":"+proxy_obj.proxy_password+"@"
            data += proxy_obj.proxy_ip+":"+str(proxy_obj.proxy_port)+"/'\n"
    #write to file
    fi = open(os.path.expanduser("~/.proxmanrc"),"w")
    fi.write(data)
    fi.close()
    
    #edit apt.conf
    #craft data
    #format Acquire::http::Proxy "http://user:pwd@ip:port/";
    data = ""
    for pt in proxy_obj.proxy_type:
        if pt=="http" or pt=="https" or pt=="ftp":
            data += 'Acquire::'+pt+'::Proxy "'+pt+'://'
            if proxy_obj.proxy_user is not None:
                data += proxy_obj.proxy_user+":"+proxy_obj.proxy_password+"@"
            data += proxy_obj.proxy_ip+":"+str(proxy_obj.proxy_port)+'/";\n'
    #escaping '%' for printf
    data = data.replace("%","%%")
    #writing changes
    #this is done using a system call for super user privileges using sudo, 
    #but not to mess up the privileges on other files, as calling the script as root
    #would.
    #printf is used, because echo is inconsistent with new lines
    
    os.system("sudo printf '"+data+"' >/etc/apt/apt.conf")

    #set active-proxy: ~/.proxman-proxies/.active-proxy
    os.system("echo " + sys.argv[2] + "> ~/.proxman-proxies/.active-proxy")
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
class Proxy():
    
    #   ---variables---
    proxy_type = None
    proxy_ip = None
    proxy_port = None
    proxy_user = None
    proxy_password = None

    #   ---functions---

    #function: constructor; initializes this instance from lines of config file
    #param: lines: lines from config file; if none: nothing is done; You need to call
    #                                                                create_proxy
    def __init__(self, lines=None):
        #only do anything is lines are not None
        if lines is not None:
            self.proxy_type = str(lines[0]).split(" ")
            self.proxy_ip = str(lines[1])
            self.proxy_port = int(lines[2])
            if len(lines) > 3:
                self.proxy_user = str(lines[3])
                self.proxy_password = str(lines[4])
            else:
                self.proxy_user = None
                self.proxy_password = None
                
    
    #function: init from variables
    #param type ip port password
    def create_proxy(self, proxy_type, proxy_ip, proxy_port, 
                     proxy_user = None, proxy_password = None):
        self.proxy_type = proxy_type
        self.proxy_ip = proxy_ip
        self.proxy_port = proxy_port
        self.proxy_user = proxy_user
        self.proxy_password = proxy_password


#               ---program execution---

parse_commands()
