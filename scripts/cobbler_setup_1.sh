# Copyright 2011 Armens Movsesjans movsesjans@gmail.com
# License: GNU General Public License, version 2 or later
# for AwaseConfigurations Project 
# http://awaseconfigurations.wordpress.com/
# https://github.com/AwaseConfigurations/main
# RR 1

#create a temp folder
mkdir ~/cobbler_wgets
cd ~/cobbler_wgets

#download preconfigured cobbler setup files and scripts from github:awaseconfigurations
#download ubuntu-11.04-alternate-i386.iso and ubuntu-11.04-server-i386.iso
wget https://raw.github.com/AwaseConfigurations/main/master/cobbler/settings
wget https://raw.github.com/AwaseConfigurations/main/master/cobbler/interfaces
wget https://raw.github.com/AwaseConfigurations/main/master/cobbler/dhcp_1.template
wget https://raw.github.com/AwaseConfigurations/main/master/cobbler/cobbler_add_systems_1.sh
wget https://raw.github.com/AwaseConfigurations/main/master/cobbler/cobbler_add_systems_server_1.sh
wget https://raw.github.com/AwaseConfigurations/main/master/cobbler/ubuntu-nqa-ws.seed
wget https://raw.github.com/AwaseConfigurations/main/master/cobbler/ubuntu-nqa-server.seed
wget https://raw.github.com/AwaseConfigurations/main/master/cobbler/wakeup_1.sh
wget http://releases.ubuntu.com/natty/ubuntu-11.04-alternate-i386.iso
wget http://releases.ubuntu.com/natty/ubuntu-11.04-server-i386.iso

#enable universe repo and install packages
sudo software-properties-gtk -e universe
sudo apt-get update
sudo apt-get install dhcp3-server cobbler cobbler-common wakeonlan rcconf

#start cobbler
sudo service cobbler start
sleep 1
sudo cobbler check

#copy cobbler setup files to where they belong
sudo cp interfaces /etc/network/
sudo /etc/init.d/networking restart
sudo cp settings /etc/cobbler/
sudo cp dhcp_1.template /etc/cobbler/dhcp.template
sudo cp ubuntu-nqa-ws.seed /var/lib/cobbler/kickstarts/
sudo cp ubuntu-nqa-server.seed /var/lib/cobbler/kickstarts/

#restart and rebuild cobbler
sudo service cobbler restart
sleep 1
sudo cobbler sync

#mount ubuntu images, import them with cobbler, and assign preconfigured preseeds
sudo mkdir /mnt/server
sudo mkdir /mnt/ws
sudo mount -o loop ubuntu-11.04-alternate-i386.iso /mnt/ws
sudo cobbler import --name=ubuntu-alternate --path=/mnt/ws --breed=ubuntu
sudo cobbler profile edit --name=ubuntu-alternate-i386 --kickstart=/var/lib/cobbler/kickstarts/ubuntu-nqa-ws.seed --kopts="priority=critical locale=en_US"

sudo mount -o loop ubuntu-11.04-server-i386.iso /mnt/server
sudo cobbler import --name=ubuntu-server --path=/mnt/server --breed=ubuntu
sudo cobbler profile edit --name=ubuntu-server-i386 --kickstart=/var/lib/cobbler/kickstarts/ubuntu-nqa-server.seed --kopts="priority=critical locale=en_US"

#restart and rebuild cobbler
sudo service cobbler restart
sleep 1
sudo cobbler sync

#run the script to add systems (machines) to same profile as preseed
#they will then pick this network install by default
chmod u+x cobbler_add_systems_1.sh
chmod u+x cobbler_add_systems_server_1.sh
./cobbler_add_systems_1.sh
./cobbler_add_systems_server_1.sh

#restart and rebuild cobbler
sudo service cobbler restart
sleep 1
sudo cobbler sync

#run the script to wake all up
chmod u+x wakeup_1.sh
./wakeup_1.sh

#make sure dhcp-server is off next time this machine is booted (our lab's requirements)
sudo rcconf --off isc-dhcp-server
