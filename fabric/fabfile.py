from fabric.api import *
import socket
import paramiko
from fabric.contrib.console import confirm

env.user='ubuntu'
env.password='ubuntu'
env.hosts=['host1.local','host2.local', 'host3.local','host4.local','host5.local','host6.local','host7.local','host8.local','host9.local', 'host10.local','host11.local', 'host12.local','host13.local','host14.local','host15.local','host16.local','host17.local','host18.local','host19.local', 'host20.local','host21.local','host22.local','host23.local','host24.local','host25.local','host26.local','host27.local','host28.local','host29.local','host30.local']
env.roledefs={
'servers' : ['host1.local'],
'workstations' : ['host2.local','host3.local','host4.local','host5.local','host6.local','host7.local','host8.local','host9.local', 'host10.local','host11.local', 'host12.local','host13.local','host14.local','host15.local','host16.local','host17.local','host18.local','host19.local', 'host20.local','host21.local','host22.local','host23.local','host24.local','host25.local','host26.local','host27.local','host28.local','host29.local','host30.local']
}

def _is_host_up(host):
    original_timeout = socket.getdefaulttimeout()
    new_timeout = 1
    socket.setdefaulttimeout(new_timeout)
    host_status = False
    try:
        transport = paramiko.Transport((host, 22))
        host_status = True
    except:
        print('{host} down.'.format(host=host))
    socket.setdefaulttimeout(original_timeout)
    return host_status

@task(alias='init')
@hosts('host1.local')
@with_settings(warn_only=True)
def init():
	if not _is_host_up(env.host):
		return
	webserver_setup()
	squid_setup()
	add_reposource()
	run("wget https://raw.github.com/AwaseConfigurations/main/master/scripts/staticip.sh")
	run("chmod +x staticip.sh")
	sudo("./staticip.sh")
	#sshkey()
	#change_passwd('ubuntu','')

@task(alias='main')
@roles('workstations')
@parallel
@with_settings(warn_only=True,linewise=True)
def main():
	if not _is_host_up(env.host):
                return
	point_to_proxy()
	add_user('simo')
	add_reposource()
	sudo("software-properties-gtk -e universe")
        update()
	if run("ls /etc/gnome").failed:
		install('ubuntu-desktop')
		bg()
		soundgreeting()
		reboot()	
	

@task(alias='put_file')
@with_settings(warn_only=True)
def put_file(localpath, remotepath):
	if not _is_host_up(env.host):
                return
	put(localpath,remotepath)

@task(alias='get_file')
@with_settings(warn_only=True)
def get_file(remotepath, localpath):
	if not _is_host_up(env.host):
		return	
	get(remotepath,localpath+'.'+env.host)

@task(alias='remove_file')
@with_settings(warn_only=True)
def remove_file(remotepath):
	if not _is_host_up(env.host):
		return
	sudo("rm -r %s" % remotepath)

@task(alias='add_user')
@parallel
@with_settings(warn_only=True)
def add_user(new_user):
	if not _is_host_up(env.host):
		return	
	if sudo("useradd -m %s" % new_user).failed:
		print("User %s already exists!" % new_user)
		return
	if env.host=='host1.local': 
		sudo("mkdir /home/%s/public_html" % new_user)
		sudo("chown %s:%s /home/%s/public_html/" % (new_user,new_user,new_user))

@task(alias='change_passwd')
@with_settings(warn_only=True)
def change_passwd(user,passwod):
        if not _is_host_up(env.host):
		return	
	sudo("echo -e '%s\n%s' | passwd %s" % (passwod,passwod,user))

@task(alias='del_user')
@parallel
@with_settings(warn_only=True)
def delete_user(user):
	if not _is_host_up(env.host):
		return
	sudo("deluser %s" % user)

@task(alias='config')
@parallel
@with_settings(warn_only=True)
def config(conff):
	if not _is_host_up(env.host):
		return
	if conff=='php_enable':
		if env.host=='host1.local':
			#sudo("mv /etc/apt/apt.conf /etc/apt/simo.hng")
			auto_install('php-enable-users')
			#sudo("mv /etc/apt/simo.hng /etc/apt/apt.conf")
	elif conff=='apache_userdir':
		if env.host=='host1.local':
			#sudo("mv /etc/apt/apt.conf /etc/apt/simo.hng")
			install_apache()
			#sudo("mv /etc/apt/simo.hng /etc/apt/apt.conf")
	elif conff=='add_unimulti':
		#sudo("mv /etc/apt/apt.conf /etc/apt/simo.hng")
		auto_install('add-unimulti')
		#sudo("mv /etc/apt/simo.hng /etc/apt/apt.conf")
	elif conff=='oneiric-sources':
		#sudo("mv /etc/apt/apt.conf /etc/apt/simo.hng")
		auto_install('oneiric-sources')
		#sudo("mv /etc/apt/simo.hng /etc/apt/apt.conf")

@task
def status():
	if not _is_host_up(env.host):
		return
	run("uptime")
	run("uname -a")

@task(alias='shutdown')
@parallel
def shut_down():
	if not _is_host_up(env.host):
		return
	sudo("shutdown -P 0")

@task
@parallel
def reboot():
	if not _is_host_up(env.host):
		return
	sudo("shutdown -r 0")

@task(alias='install')
@parallel
@with_settings(warn_only=True)
def install(package):
	if not _is_host_up(env.host):
		return
	sudo("apt-get update")
	if sudo("apt-get -y install %s" % package).failed:
		local("echo FAIL "+env.host+": failed to install %s $(date) >> ~/fail.log" % package)
		for i in range(1,3):
			sudo("apt-get update")
                    	if sudo("apt-get -y install %s" % package).failed:
				local("echo MULTIFAIL "+env.host+": failed to install %s $(date) >> ~/fail.log" % package)

@task
@parallel
def uninstall(package):
	if not _is_host_up(env.host):
		return
	sudo("apt-get -y remove %s" % package)

@task
@parallel
def update():
	if not _is_host_up(env.host):
		return
	sudo("apt-get update")

@task(alias='upgrade')
@parallel
@with_settings(warn_only=True)
def upgrade():
	if not _is_host_up(env.host):
		return
	sudo("apt-get update")
	sudo("apt-get -y upgrade")

@task(alias='auto_install')
@parallel
@with_settings(warn_only=True)
def auto_install(package): # this will auto answer "yes" to all and keep old config files
	if not _is_host_up(env.host):
		return
	sudo("apt-get update")
	sudo('apt-get install -o Dpkg::Options::="--force-confold" --force-yes -y %s' % package)

@task(alias='auto_upgrade')
@parallel
@with_settings(warn_only=True)
def auto_upgrade():
        if not _is_host_up(env.host):
		return
	sudo("apt-get update")
        sudo('apt-get upgrade -o Dpkg::Options::="--force-confold" --force-yes -y')

@task(alias='auto_dist_upgrade')
@parallel
@roles('workstations')
@with_settings(warn_only=True)
def auto_dist_upgrade():
        if not _is_host_up(env.host):
		return
	if run('lsb_release -c') == 'Codename:	oneiric':
		return
	config('oneiric-sources')
	sudo("apt-get update")
	sudo('DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get dist-upgrade -o Dpkg::Options::="--force-confold" --force-yes -y')
	bg()
	soundgreeting()
	sudo("reboot")

@task
def outputtest():
	mystore = run('lsb_release -c') 
	if 'oneiric' in mystore:	
		print('its oneiric!!')
	else:
		print('else')

@task
@parallel
def add_reposource():
        if not _is_host_up(env.host):
		return
	with cd("/etc/apt/sources.list.d/"):
		sudo("echo deb http://172.28.212.1/~ubuntu/ natty main >> repository.list")
		# remove duplicates:
		sudo("sort -u repository.list > repository.list.new")
		sudo("cat repository.list.new > repository.list")
		sudo("rm repository.list.new")
		
@task
@hosts('host1.local')
def install_apache():
	if not _is_host_up(env.host):
		return
	sudo("apt-get update")
	sudo("apt-get -y install apache2")
	if run("ls /etc/apache2/mods-enabled/userdir.conf").failed:
		sudo("a2enmod userdir")
		sudo("/etc/init.d/apache2 restart")

@task(alias='webserver_setup')
@hosts('host1.local')
@with_settings(warn_only=True)
def webserver_setup():
	if not _is_host_up(env.host):
		return
	install_apache()
	install('php5')
	reprepro_setup()
	clonegit()
	add_reposource()
	add_to_repo()
	if run('ls /etc/apache2/mods-enabled/php5.conf.hng').failed:
		config('php_enable')
		sudo("/etc/init.d/apache2 restart")
	run('mkdir backup')

@task(alias='reprepro_setup')
@hosts('host1.local')
@with_settings(warn_only=True)
def reprepro_setup():
	if not _is_host_up(env.host):
                return
	if run("ls ~/public_html/conf/").failed:
        	sudo("apt-get update")
        	sudo("apt-get -y install reprepro")	
		run("wget https://raw.github.com/AwaseConfigurations/main/master/scripts/reprepro_setup.sh")
		run("chmod +x reprepro_setup.sh")
		run("./reprepro_setup.sh")
		run("rm reprepro_setup.sh")
	

@task(alias='add_to_repo')
@hosts('host1.local')
@with_settings(warn_only=True)
def add_to_repo():
	if not _is_host_up(env.host):
		return
	with cd('~/public_html/'):
		run("cp ~/main/packages/php/php-enable-users/php-enable-users_0.1_all.deb ~/public_html/")
		run("cp ~/main/packages/apt/add-unimulti/add-unimulti_0.1_all.deb ~/public_html/")
		run("cp ~/main/packages/apt/oneiric-sources/oneiric-sources_0.1_all.deb ~/public_html/")
		run("reprepro includedeb natty add-unimulti_0.1_all.deb")
		run("reprepro includedeb natty oneiric-sources_0.1_all.deb")
		if run("reprepro includedeb natty php-enable-users_0.1_all.deb").failed:
			reprepro_setup()
			clonegit()
			run("cp ~/main/packages/php/php-enable-users/php-enable-users_0.1_all.deb ~/public_html/")
			run("cp ~/main/packages/apt/add-unimulti/add-unimulti_0.1_all.deb ~/public_html/")
			run("cp ~/main/packages/apt/oneiric-sources/oneiric-sources_0.1_all.deb ~/public_html/")
			run("reprepro includedeb natty php-enable-users_0.1_all.deb")					
			run("reprepro includedeb natty add-unimulti_0.1_all.deb")
			run("reprepro includedeb natty oneiric-sources_0.1_all.deb")

@task(alias='clonegit')
@hosts('host1.local')
@with_settings(warn_only=True)
def clonegit():
	if not _is_host_up(env.host):
		return
	install('git')
	with cd('~/'):
		run("git clone https://github.com/AwaseConfigurations/main")

@task(alias='sshkey')
@with_settings(warn_only=True)
def sshkey():
	if not _is_host_up(env.host):
		return
	if local('ssh-copy-id '+env.user+'@'+env.host).failed:
		local('sudo apt-get -y install ssh')
		local('ssh-keygen -N "" -q -f .ssh/id_rsa -t rsa')
		local('ssh-copy-id '+env.user+'@'+env.host)
		

@task(alias='bg')
@parallel
@with_settings(warn_only=True)
def bg():
        if not _is_host_up(env.host):
                return
	if local("ls awasebg.jpg").failed:
		local("wget http://myy.haaga-helia.fi/~a0900094/awasebg.jpg")
        put("awasebg.jpg","/usr/share/backgrounds/warty-final-ubuntu.png",use_sudo=True)

@task(alias='set_bg')
@parallel
@with_settings(warn_only=True)
def set_bg(bg):
        if not _is_host_up(env.host):
                return
        if local("ls %s" % bg).failed:
                local("echo bg file not found")
		return
        put(bg,"/usr/share/backgrounds/warty-final-ubuntu.png",use_sudo=True)
	
@with_settings(warn_only=True)
def bg_old2():
	if not _is_host_up(env.host):
		return
	run("wget http://myy.haaga-helia.fi/~a0900094/awasebg.jpg")
	sudo("mv -b awasebg.jpg /usr/share/backgrounds/warty-final-ubuntu.png")

@with_settings(warn_only=True)
def bg_old():
	if not _is_host_up(env.host):
                return
	if put("awasebg.jpg","/tmp/").failed:
		local("wget http://myy.haaga-helia.fi/~a0900094/awasebg.jpg")
		put("awasebg.jpg","/tmp/")
	sudo("cp /tmp/awasebg.jpg /usr/share/backgrounds/warty-final-ubuntu.png")

@task(alias='cmd')
@with_settings(warn_only=True)
def cmd(command):
	if not _is_host_up(env.host):
                return
	run(command)

@task(alias='scmd')
@with_settings(warn_only=True)
def scmd(command):
	if not _is_host_up(env.host):
                return
        sudo(command)

@task(alias='point_to_proxy')
@parallel
@roles('workstations')
@with_settings(warn_only=True)
def point_to_proxy():
	if not _is_host_up(env.host):
                return
	sudo("""echo 'Acquire { Retries "0"; HTTP { Proxy "http://host1.local:3128"; }; };' | tee /etc/apt/apt.conf""")

@task(alias='sshfs')
@roles('workstations')
@with_settings(warn_only=True)
def sshfs():
	if not _is_host_up(env.host):
                return
	run('mkdir Desktop/backup')
	install('sshfs')
	run('sshfs ubuntu@host1.local:/home/ubuntu/backup/ /home/ubuntu/desktop/backup')

@task
@hosts('host1.local')
def squid_setup():
	if not _is_host_up(env.host):
		return
	if run("ls /etc/squid/squid.conf").failed:
		sudo("apt-get update")
		sudo("apt-get -y install squid")
		run("wget https://raw.github.com/AwaseConfigurations/main/master/squid/squid.conf")
	        sudo("cp squid.conf /etc/squid/squid.conf")
		sudo("chown root:root /etc/squid/squid.conf")
		sudo("service squid restart")

@task(alias='soundgreeting')
@parallel
@roles('workstations')
@with_settings(warn_only=True)
def soundgreeting():
        if not _is_host_up(env.host):
                return
	if local("ls heitero.ogg").failed:
		local("wget http://myy.haaga-helia.fi/~a0903751/heitero.ogg")
        put("heitero.ogg","/usr/share/sounds/ubuntu/stereo/dialog-question.ogg",use_sudo=True)

@task(alias='set_soundgreeting')
@parallel
@with_settings(warn_only=True)
def set_soundgreeting(soundfile):
        if not _is_host_up(env.host):
                return
        if local("ls %s" % soundfile).failed:
                local("echo soundfile file not found")
		return
        put(soundfile,"/usr/share/sounds/ubuntu/stereo/dialog-question.ogg",use_sudo=True)

@task(alias='fix')
@roles('workstations')
@with_settings(warn_only=True)
def fix():
	if not _is_host_up(env.host):
                return
	sudo('apt-get update')
	#install('sshfs')
	#run('sshfs ubuntu@host1.local:/home/ubuntu/backup/ /home/ubuntu/desktop/backup')
