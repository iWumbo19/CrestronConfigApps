
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


def GetSecret():
    pwdHash = 'c7c91ea881a7edbcfb2296c1f9b1236e815132fd5bf1cce1e79c88163197cf82'
    print("What is the password for AVServices")
    secret = getpass.getpass(prompt="")
    hash = hashlib.sha256(secret.encode('utf-8')).hexdigest()
    if hash == pwdHash:
        print("Password Accepted")
        return secret
    else:
        print("That password is incorrect")
        return GetSecret()


def AdminStart(ssh, host, port, hostname, avuser, secret, csIP):
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
        NoAdmin(ssh, host, port, hostname, avuser, secret, csIP)
    except:
        print(f"Something failed when trying to reconnect with {avuser} account")
        print(f"Shutting Down")
        input()
        sys.exit





def NoAdmin(ssh, host, port, hostname, avuser, secret, csIP):
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
    
            
    print(f"Script Complete")
    input()




def Main():
    host = GetIP()
    port = 22
    username = "admin"
    password = "admin"
    hostname = GetHostname()
    avuser = "AVServices"
    secret = GetSecret()
    csIP = GetCSIP()


    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port,username, password)
        print("Logged in with default Credentials")
    except:
        print("Default Credentials Failed or 'admin' credentials don't exist")
        print("Trying default AVServices")
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port, avuser, secret)
            print("Logged in with AVServices account")
            NoAdmin(ssh, host, port, hostname, avuser, secret, csIP)
        except:
            print("Couldn't log in with any default credentials. The program will now close")
            input()
            sys.exit()


#Program Entrance    
Main()