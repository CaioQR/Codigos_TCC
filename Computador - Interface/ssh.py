from paramiko import SSHClient, AutoAddPolicy
import json
import os
import time

#Raspberry pi credentials and network info
host = "192.168.1.34"
port = 22
username = "pi"
password = "bayer"

#Json Data
path = "/home/pi/Documents/bayer_project/"
pi_images_path = "/home/pi/Documents/bayer_project/Images/"
local_images_path = "C:/Users/Henrique/Desktop/"
json_data = {
    "running_ensaio": "false", 
    "ensaio_data":{
        "id":"12345678", 
        "tecnico": "teste"
    }
}

#connect to Raspberry pi through SSH
def setup_ssh(host, port, username, password):
    try:
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(host, port, username, password)
        print("Conectado")
        return ssh
    except:
        print("Erro na conexão")
        return 1


#Replace Json
def replace_json(ssh, json_data, filename, path):
    try:
        sftp = ssh.open_sftp()
        with sftp.open(path+"/"+filename, 'w') as json_file:
            json.dump(json_data, json_file)
            json_file.close()
        print("Foi possível atualizar os dados")
        return 0
    except:
        print("Não foi possível atualizar os dados")
        return 1

#runs python script on ssh terminal
def run_script(ssh, filename, path):
    try:
        stdin, stdout, stderr = ssh.exec_command("cd "+path+";"+" python3 "+filename)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if err:
            print("Erro ao gerar imagens")
            return 1
        else:
            return 0
    except:
        print("Erro ao gerar imagens")
        return 1
    
#retreives images through SSH for a given path
def get_images(ssh, remote_path, local_path):
    try:
        sftp = ssh.open_sftp()
        for file in sftp.listdir(remote_path):
            file_remote = remote_path + file
            file_local = local_path + file
            #print(file_remote + '>>>' + file_local)
            sftp.get(file_remote, file_local)
        return 0
    except:
        print("Erro ao fazer download das imagens")
        return 1
print("->Conectando via SSH")
ssh = setup_ssh(host, port, username, password)
print("->Atualizando dados do ensaio")
replace_json(ssh, json_data, "display.json", path)
print("->Tirando fotos")
output = run_script(ssh, "camera.py", path)
print("->Fazendo download das imagens")
get_images(ssh, pi_images_path, local_images_path)
print("Concluído")