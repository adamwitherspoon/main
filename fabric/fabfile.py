from fabric.api import parallel, settings, run, sudo, local, roles, env, cd, put, get, hosts, task, hide
import socket
import paramiko
from random import choice
import string

env.user = 'ubuntu'
env.password = 'ubuntu'
env.hosts = ['host1.local', 'host2.local', 'host3.local', 'host4.local',  'host6.local', 'host8.local', 'host9.local', 'host10.local', 'host11.local', 'host12.local', 'host13.local', 'host14.local', 'host15.local', 'host16.local', 'host17.local', 'host18.local', 'host19.local', 'host21.local', 'host22.local', 'host23.local', 'host24.local', 'host25.local', 'host26.local', 'host27.local', 'host28.local', 'host29.local', 'host30.local']
env.roledefs = {'servers' : ['host1.local'],'workstations' : ['host2.local', 'host3.local', 'host4.local', 'host6.local', 'host8.local', 'host9.local', 'host10.local', 'host11.local', 'host12.local', 'host13.local', 'host14.local', 'host15.local', 'host16.local', 'host17.local', 'host18.local', 'host19.local', 'host21.local', 'host22.local', 'host23.local', 'host24.local', 'host25.local', 'host26.local', 'host27.local', 'host28.local', 'host29.local', 'host30.local']}

@task
@hosts('host1.local')
def init():
    """Initialise the server"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            setup_webserver()
            setup_squid()
            configure_reposource()
            
@task
@roles('workstations')
@parallel
def main():
    """Main installation task for workstations"""
    with settings(linewise=True,warn_only=True):
        if is_host_up(env.host):
            point_to_proxy()
            user_add('simo','password')
            configure_reposource()
            sudo("software-properties-gtk -e universe")
            update()
            if run("ls /etc/gnome").failed:
                install('ubuntu-desktop')
                local("wget http://myy.haaga-helia.fi/~a0900094/awasebg.jpg")
                set_bg("awasebg.jpg")
                local("wget http://myy.haaga-helia.fi/~a0903751/heitero.ogg")
                set_soundgreeting("heitero.ogg")
		run("setxkbmap fi")
                reboot()    

@task
def cmd(command):
    """Pass a command to the hosts"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            run(command)

@task
def cmds(command):
    """Pass a sudo command to the hosts"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            sudo(command)

@task
@parallel
def install(package):
    """Install a package"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get update")
            for retry in range(2):
                if sudo("apt-get -y install %s" % package).failed:
                    local("echo INSTALLATION ATTEMPT %s FAILED FOR " + env.host + ": failed to install %s $(date) >> ~/fail.log" % ((retry+1),package))
                else:
                    break

@task
@parallel
def install_auto(package):
    """Install a package answering yes to all questions"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get update")
            sudo('DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get install -o Dpkg::Options::="--force-confold" --force-yes -y %s' % package)

@task
@hosts('host1.local')
def install_apache():
    """Install Apache server with userdir enabled"""
    if is_host_up(env.host):
        sudo("apt-get update")
        sudo("apt-get -y install apache2")
        if run("ls /etc/apache2/mods-enabled/userdir.conf").failed:
            sudo("a2enmod userdir")
            sudo("/etc/init.d/apache2 restart")

@task
@parallel
def uninstall(package):
    """Uninstall a package"""
    if is_host_up(env.host):
        sudo("apt-get -y remove %s" % package)

@task
@parallel
def update():
    """Update apt-get"""
    if is_host_up(env.host):
        sudo("apt-get update")

@task
@parallel
def upgrade():
    """pass a sudo command to the hosts"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get update")
            sudo("apt-get -y upgrade")

@task 
@parallel
def upgrade_auto():
    """Update apt-get and Upgrade apt-get answering yes to all questions"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get update")
            sudo('apt-get upgrade -o Dpkg::Options::="--force-confold" --force-yes -y')

@task
@parallel
@roles('workstations')
def upgrade_distribution(codename="oneiric"):
    """Upgrade Ubuntu distribution DEFAULTS TO: oneiric"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            if run('lsb_release -c') == 'Codename:    %s' % codename:
                return
            configure_sources(codename)
            sudo("apt-get update")
            sudo('DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get dist-upgrade -o Dpkg::Options::="--force-confold" --force-yes -y')
            set_bg()
            set_soundgreeting()
            sudo("reboot")

@task
@parallel
def user_add(new_user, passwd=False):
    """Add new user"""
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        if is_host_up(env.host):
	    if not passwd:
                passwd = generate_passwd()
            if not sudo("echo -e '%s\n%s\n' | adduser %s" % (passwd,passwd,new_user)).failed:
                if env.host=='host1.local': 
                    sudo("mkdir /home/%s/public_html" % new_user)
                    sudo("chown %s:%s /home/%s/public_html/" % new_user)

@task
@parallel
def user_passwd(user, passwd=False):
    """Change password for user"""
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        if is_host_up(env.host):
            if not passwd:
                passwd = generate_passwd()
            sudo("echo -e '%s\n%s' | passwd %s" % (passwd,passwd,user))

@task
@parallel
def user_delete(user):
    """Delete user"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            sudo("deluser %s" % user)

@task
def status():
    """Display host status"""
    if is_host_up(env.host):
        run("uptime")
        run("uname -a")

@task
@parallel
def shut_down():
    """Shut down a host"""
    if is_host_up(env.host):
        sudo("shutdown -P 0")

@task
@parallel
def reboot():
    """Reboot a host"""
    if is_host_up(env.host):
        sudo("shutdown -r 0")

@task
def file_put(localpath, remotepath):
    """Put file from local path to remote path"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            put(localpath,remotepath)

@task
def file_get(remotepath, localpath):
    """Get file from remote path to local path"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            get(remotepath,localpath+'.'+env.host)

@task
def file_remove(remotepath):
    """Remove file at remote path"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            sudo("rm -r %s" % remotepath)

@task
@parallel
def configure_reposource():
    """Adds host1.local to repository list"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            with cd("/etc/apt/sources.list.d/"):
                sudo("echo deb http://host1.local/~ubuntu/ natty main >> repository.list")
                # remove duplicates:
                sudo("sort -u repository.list > repository.list.new")
                sudo("cat repository.list.new > repository.list")
                sudo("rm repository.list.new")

@task
@parallel
def configure_sources(sources="oneiric"):
    """Switch apt sources to different distribution"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            sudo("mv /etc/apt/apt.conf /etc/apt/simo.hng")
            install_auto('%s-sources' % sources)
            sudo("mv /etc/apt/simo.hng /etc/apt/apt.conf")
        
@task
@parallel
def set_bg(bg):
    """Set an image file to be used as background"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            if local("ls %s" % bg).failed:
                local("echo image file not found")
            else:
                put(bg,"/usr/share/backgrounds/warty-final-ubuntu.png",use_sudo=True)

@task
@parallel
def set_soundgreeting(soundfile):
    """Set a sound file to be used on login"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            if local("ls %s" % soundfile).failed:
                local("echo sound file not found")
            else:
                put(soundfile,"/usr/share/sounds/ubuntu/stereo/dialog-question.ogg",use_sudo=True)

@hosts('host1.local')
def configure_php():
    with settings(warn_only=True):
        if is_host_up(env.host):
            sudo("mv /etc/apt/apt.conf /etc/apt/simo.hng")
            install_auto('php-enable-users')
            sudo("mv /etc/apt/simo.hng /etc/apt/apt.conf")

@hosts('host1.local')
def setup_webserver():
    with settings(warn_only=True):
        if is_host_up(env.host):
            install_apache()
            install('php5')
            setup_reprepro()
            clonegit()
            configure_reposource()
            add_to_repo()
            if run('ls /etc/apache2/mods-enabled/php5.conf.hng').failed:
                configure_php()
                sudo("/etc/init.d/apache2 restart")
            run('mkdir backup')

@hosts('host1.local')
def clonegit():
    """Clones awaseConfigurations git source"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            install('git')
            with cd('~/'):
                run("git clone https://github.com/AwaseConfigurations/main")

@hosts('host1.local')
def add_to_repo():
    """Add sources to reprepro"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            with cd('~/public_html/'):
                run("cp ~/main/packages/php/php-enable-users/php-enable-users_0.1_all.deb ~/public_html/")
                run("cp ~/main/packages/apt/add-unimulti/add-unimulti_0.1_all.deb ~/public_html/")
                run("cp ~/main/packages/apt/oneiric-sources/oneiric-sources_0.1_all.deb ~/public_html/")
                run("reprepro includedeb natty add-unimulti_0.1_all.deb")
                run("reprepro includedeb natty oneiric-sources_0.1_all.deb")
                if run("reprepro includedeb natty php-enable-users_0.1_all.deb").failed:
                    setup_reprepro()
                    clonegit()
                    run("cp ~/main/packages/php/php-enable-users/php-enable-users_0.1_all.deb ~/public_html/")
                    run("cp ~/main/packages/apt/add-unimulti/add-unimulti_0.1_all.deb ~/public_html/")
                    run("cp ~/main/packages/apt/oneiric-sources/oneiric-sources_0.1_all.deb ~/public_html/")
                    run("reprepro includedeb natty php-enable-users_0.1_all.deb")                    
                    run("reprepro includedeb natty add-unimulti_0.1_all.deb")
                    run("reprepro includedeb natty oneiric-sources_0.1_all.deb")

@hosts('host1.local')
def setup_squid():
    """Setups Squid for host1.local"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            if run("ls /etc/squid/squid.conf").failed:
                sudo("apt-get update")
                sudo("apt-get -y install squid")
                run("wget https://raw.github.com/AwaseConfigurations/main/master/squid/squid.conf")
                sudo("cp squid.conf /etc/squid/squid.conf")
                sudo("chown root:root /etc/squid/squid.conf")
                sudo("service squid restart")
            
@hosts('host1.local')
def setup_reprepro():
    """Setups reprepro for host1.local"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            if run("ls ~/public_html/conf/").failed:
                sudo("apt-get update")
                sudo("apt-get -y install reprepro")    
                run("wget https://raw.github.com/AwaseConfigurations/main/master/scripts/reprepro_setup.sh")
                run("chmod +x reprepro_setup.sh")
                run("./reprepro_setup.sh")
                run("rm reprepro_setup.sh")
                
@parallel
def point_to_proxy():
    with settings(warn_only=True):
        if is_host_up(env.host):
            sudo("""echo 'Acquire { Retries "0"; HTTP { Proxy "http://host1.local:3128"; }; };' | tee /etc/apt/apt.conf""")

def generate_passwd(length = 10):
    return ''.join(choice(string.ascii_letters + string.digits) for _ in range(length))

def is_host_up(host):
    """Verify the host computer is online before action"""
    print('Attempting connection to host: %s' % host)
    original_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(1)
    host_up = True
    try:
        paramiko.Transport((host, 22))
    except Exception, e:
        host_up = False
        print('%s down, %s' % (host, e))
    finally:
        socket.setdefaulttimeout(original_timeout)
        return host_up

@task
def smartmon_setup():
	with settings(warn_only=True):
        	if is_host_up(env.host):
			if run('ls /etc/smartmontools').failed:
				install_auto('smartmontools')
				sudo('smartctl -s on -o on -S on /dev/sda')

@task
def smartmon():
	 with settings(warn_only=True):
                if is_host_up(env.host):
			smartmon_setup()
			sudo('smartctl -H /dev/sda')
