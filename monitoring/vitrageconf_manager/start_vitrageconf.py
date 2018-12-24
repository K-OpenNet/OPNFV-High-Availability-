
import subprocess
from ssh_manager import listener
import os
import time


class VitrageconfManager(object):

    def __init__(self, request):
        self.monitoring_tool = None
        self.server_ip = None
        self.server_port = None
        self.server_pass = None
        self.server_user = None
        self.host_name = None
        self.host_type = None
        self.vm_ip =  None
        self.vm_id = None
        self.vm_interface= None

        self.script = "/opt/stack/Inspection-System/install_agent.sh"                 # use for appending texts to script (real path in which script is locate )
        self.path_script = "/opt/stack/Inspection-System"                            # path of script
        self.data = None

        self.path_vitrage = "/etc/vitrage"                           # replace here with /etc/vitrage
        self.vitrage_conf = "/etc/vitrage/vitrage.conf"  # replace here with /etc/vitrage/vitrage.conf
        self.zabbix_conf = "/etc/vitrage/zabbix_conf.yaml"      # replace here with

        self.request = request


    def decode(self):
        self.data = self.request['vitrage_conf_policy']
        self.monitoring_tool = self.data['monitoring_tool']
        self.server_ip = self.data['server_ip']
        self.server_port = self.data['server_port']
        self.server_pass = self.data['server_pass']
        self.server_user = self.data['server_user']
        self.host_name = self.data['host_name']
        self.host_type = self.data['host_type']
        self.vm_ip = self.data['vm_ip']
        self.vm_id = self.data['vm_id']
        self.vm_interface = self.data['vm_interface']

    def make_script(self, number):

        open("%s/install_agent.sh" % self.path_script, 'w').close()  # make <install_agent> script

        subprocess.call("echo 'sudo echo \"ubuntu:ubuntu\" | chpasswd' >> '%s'" % self.script, shell=True)
        subprocess.call("echo 'sudo echo \"root:root\" | chpasswd' >> '%s'" % self.script, shell=True)
        subprocess.call("echo 'sudo apt-get -y update' >> '%s'" % self.script, shell=True)
        subprocess.call("echo 'sudo apt-get -y upgrade' >> '%s'" % self.script, shell=True)
        subprocess.call("echo 'sudo apt-get -y install zabbix-agent' >> '%s'" % self.script, shell=True)
        subprocess.call("echo 'sudo apt-get -y install apache2' >> '%s'" % self.script, shell=True)
        subprocess.call("echo '\n' >> '%s'" % self.script, shell=True)

        subprocess.call("echo 'sudo sed -i \"2s/.*/`ifconfig '%s' | grep \"inet addr:\"| cut -d: -f2 | awk \"{ print $1 }\"`/g\" \"/etc/hosts\"' >> '%s'" % (self.vm_interface, self.script), shell=True)           #replace testhosts to /etc/hosts
        subprocess.call("echo 'sudo sed -i \"s/Bcast/`cat /etc/hostname`/g\" \"/etc/hosts\"' >> '%s'" % self.script, shell=True)                                 #replace testhosts to /etc/hosts
        subprocess.call("echo 'sudo sed -i \"3s/.*/'%s'\\\tmonitor/g\" \"/etc/hosts\"' >> '%s'" % (self.vm_ip[number], self.script), shell=True)                        #replace testhosts to /etc/hosts
        subprocess.call("echo 'sudo /etc/init.d/networking restart' >> '%s'" % self.script, shell=True)
        subprocess.call("echo 'sudo echo \"zabbix ALL=NOPASSWD: ALL\" >> /etc/sudoers' >> '%s'" % self.script, shell=True)
        subprocess.call("echo '\n' >> '%s'" % self.script, shell=True)

        subprocess.call("echo 'sudo sed -i \"s/# EnableRemoteCommands=0/EnableRemoteCommands=1/\" \"/etc/zabbix/zabbix_agentd.conf\"' >> '%s'" % self.script, shell=True)
        subprocess.call("echo 'sudo sed -i \"s/Server=127.0.0.1/Server='%s'/\" \"/etc/zabbix/zabbix_agentd.conf\"' >> '%s'" % (self.server_ip, self.script), shell=True)
        subprocess.call("echo 'sudo sed -i \"s/ServerActive=127.0.0.1/ServerActive='%s':'%s'/\" \"/etc/zabbix/zabbix_agentd.conf\"' >> '%s'" % (self.server_ip, self.server_port, self.script), shell=True)
        subprocess.call("echo 'sudo sed -i \"s/Hostname=Zabbix server/Hostname=`cat /etc/hostname`/\" \"/etc/zabbix/zabbix_agentd.conf\"' >> '%s'" % self.script, shell=True)
        subprocess.call("echo '\n' >> '%s'" % self.script, shell=True)

        subprocess.call("echo 'sudo service apache2 restart' >> '%s'" % self.script, shell=True)
        subprocess.call("echo 'sudo service zabbix-agent restart' >> '%s'" % self.script, shell=True)

        # os.chmod("%s/install_agent" %path,0777)     #make <install_agent> shell script execute
        #ssh_manager.listener.start_script(self.vm_ip,self. )  # hosts,auth,file_name,local_path,remote_path

    def start_config(self):
        # add zabbix to list of datasources in /etc/vitrage/vitrage.conf
        subprocess.call(['sed', "-i", "20s/types = nova.host/types = zabbix,nova.host/g", self.vitrage_conf])
        subprocess.call(['sed', "-i", "35s/.*/[zabbix]/g", self.vitrage_conf])
        subprocess.call(['sed', "-i", "36s/.*/url = http:\/\/%s\/zabbix/g" %self.server_ip, self.vitrage_conf])
        subprocess.call(['sed', "-i", "37s/.*/password = %s/g" % self.server_pass, self.vitrage_conf])
        subprocess.call(['sed', "-i", "38s/.*/user = %s/g" % self.server_user, self.vitrage_conf])
        subprocess.call(['sed', "-i", "39s/.*/config_file = \/etc\/vitrage\/zabbix_conf.yaml/g" , self.vitrage_conf])

        if os.path.exists("%s" % self.zabbix_conf):
            pass
        else:
            open("%s/zabbix_conf.yaml" % self.path_vitrage, 'w').close()
            subprocess.call("echo 'zabbix:' >> '%s'" % self.zabbix_conf, shell=True)

        for number in range(0, len(self.host_name)):
            subprocess.call("echo '- zabbix_host: '%s'' >> '%s'" % (self.host_name[number], self.zabbix_conf), shell=True)
            subprocess.call("echo '  type: '%s'' >> '%s'" % (self.host_type, self.zabbix_conf), shell=True)
            subprocess.call("echo '  name: '%s'' >> '%s'" % (self.vm_id[number], self.zabbix_conf), shell=True)
        print("=================================================================")
        print("            Waiting For agent<->server connection                ")
        print("=================================================================")
        time.sleep(40)
        print("=================================================================")
        print("                  Restarting Vitrage-Service                     ")
        print("=================================================================")
        subprocess.call('sudo systemctl restart devstack@vitrage-collector.service', shell=True)
        subprocess.call('sudo systemctl restart devstack@vitrage-graph.service', shell=True)



    def start_script(self):
        self.decode()
        if self.monitoring_tool == "Zabbix":
            print("=================================================================")
            print("                      Making Script to VM                        ")
            print("=================================================================")
            for number in range(0, len(self.vm_ip)):
                self.make_script(number)
                if self.host_type == "nova.host":
                    print("This VM is Host")
                    listener.start_script([self.vm_ip[number]], ['root','root'], "install_agent.sh", self.path_script,
                                          "/home/ubuntu")
                else:
                    print("This VM is instance")
                    listener.start_script([self.vm_ip[number]], ['ubuntu','ubuntu'], "install_agent.sh", self.path_script,
                                          "/home/ubuntu")


