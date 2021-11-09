
import paramiko
import getpass
import socket
import sys
import hashlib
import base64
import uuid

def GetIP():
    print("What IP would you like to connect to:")
    IPaddr = input()
    try:
        socket.inet_aton(IPaddr)
        return IPaddr
    except socket.error:
        print("That is not a valid IPv4 address. Please Try again")
        GetIP()    
    
def GetHostname():
    print("What will the host name be for this device:")
    hostname = input()
    if (' ' in hostname or '_' in hostname) == True:
        print("White space or underscores are not allowed in hostnames. Try again.")
        return GetHostname()
    return hostname

def GetCSIP():
    print("What is the IP of the processor this device will point to:")
    IPaddr = input()
    try:
        socket.inet_aton(IPaddr)
        return IPaddr
    except socket.error:
        print("That is not a valid IPv4 address. Please Try again")
        GetCSIP()

def GetADUsers():
    print("Type AD enabled usernames. Seperate names with a single comma (no spaces)")
    adString = input()
    ADUsers = adString.split(',', -1)
    return ADUsers

def GetSecret():
    pwdHash = 'a0c5ad9a06d9a5c003dd94073b71aeaab480f4b2ec5e2de5a1943b291c02e459'
    salt = uuid.uuid4().hex
    print("What is the password for AVServices")
    secret = getpass.getpass(prompt="")
    hash = hashlib.sha256(secret.encode('utf-8') + salt.encode('utf-8')).hexdigest()
    if hash == pwdHash:
        return secret
    else:
        print("That password is incorrect")



def Main():
    host = GetIP()
    port = 22
    username = "admin"
    password = "admin"
    hostname = GetHostname()
    avuser = "AVServices"
    secret = GetSecret()
    csIP = GetCSIP()
    ADusers = GetADUsers()


    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port,username, password)
        print("Logged in with default Credentials")
    except:
        print("Default Credentials Failed or 'admin' credentials don't exist")
        print("The Program Will Now Close... Sorry")
        input()
        sys.exit()
        


    #Adds AVServices User
    try:
        print(f"Adding User {avuser} to device")
        stdin, stdout, stderr = ssh.exec_command(f"adduser -N:{avuser} -P:{secret}")
        lines = stdout.readlines()
        print(lines[0])
    except:
        print(stderr) 


    #Adds AVServices to Admin group
    try:
        print(f"Adding {avuser} to Administrator Group")
        stdin, stdout, stderr = ssh.exec_command(f"addusert -N:{avuser} -G:Administrators")
        lines = stdout.readlines()
        print(lines[0])
    except:
        print(stderr)



    #Closes Connection
    try:
        print(f"Closing Connection...")
        stdin, stdout, stderr = ssh.exec_command("bye")
        lines = stdout.readlines()
        print(lines[0])
    except:
        print(stderr)

        
    #Re-establishes Connection with new credentials
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port,avuser, secret)
        print("Connection back")
    except:
        print(f"Something failed when trying to reconnect with {avuser} account")



    #Attempts to delete admin
    try:
        print(f"Deleting Unsecure Admin Account")
        stdin, stdout, stderr = ssh.exec_command(f"deleteu {username}\nY")
        lines = stdout.readlines()
        print(lines[0])
    except:
        print(stderr)

        
    #Set IPID and Control System IP
    try:
        print(f"Setting IPIDs and Control System IP")
        stdin, stdout, stderr = ssh.exec_command(f"addmaster 0F {csIP}")
        lines = stdout.readlines()
        print(lines[0])
    except Exception:
        print(stderr)


    #Attempts to Change Hostname
    try:    
        print(f"Changing Hostname to {hostname}")
        stdin, stdout, stderr = ssh.exec_command(f"hostname {hostname}")
        lines = stdout.readlines()
        print(lines[0])
    except:
        print(stderr)
        
    
    #Set SNTP server
    try:    
        print(f"Setting SNTP Server")
        stdin, stdout, stderr = ssh.exec_command(f"sntp server:nic.unh.edu")
        lines = stdout.readlines()
        print(lines[0])
    except:
        print(stderr)
        
        
    #Adds all users to AD
    print("Adding users to ad.unh.edu AD")
    for name in ADusers:
        try:        
            print(f"Adding {name}")
            stdin, stdout, stderr = ssh.exec_command(f"addusert -N:ad.unh.edu\{name} -G:Administrators")
            lines = stdout.readlines()
            print(lines[0])
        except:
            print(stderr)    
    
            
    print(f"Script Complete")
    input()


def HashMaker():
    

    
HashMaker()


#Program Entrance    
#Main()