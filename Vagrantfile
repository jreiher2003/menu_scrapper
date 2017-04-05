# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure(2) do |config|
  

  config.vm.box = "ubuntu/trusty64"

 
  # config.vm.box_check_update = false

  
  config.vm.network "forwarded_port", guest: 6021, host: 6021

 
  # config.vm.network "private_network", ip: "192.168.33.10"

  # config.vm.network "public_network"

 
  # config.vm.synced_folder "../data", "/vagrant_data"

  

 

 
  config.vm.provision "shell", inline: <<-SHELL
    sudo apt-get update -y
    sudo apt-get autoremove -y
    sudo apt-get upgrade -y
    sudo apt-get install python-pip -y
    sudo apt-get install python-virtualenv -y
    sudo apt-get install python-dev -y
    sudo apt-get install libpq-dev -y
    sudo apt-get install build-essential -y
    sudo apt-get install git -y
    sudo apt-get install libpq-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libffi-dev -y
    #sudo apt-get install autoconf libtool pkg-config python-opengl python-imaging python-pyrex python-pyside.qtopengl idle-python2.7  libqtgui4 libqtcore4 libqt4-xml libqt4-test libqt4-script libqt4-network libqt4-dbus  libgle3  -y
    git config --global user.name "Jeff Reiher"
    git config --global user.email "jreiher2003@yahoo.com"
    git config --global push.default upstream
    git config --global merge.conflictstyle diff3
    git config --global credential.helper 'cache --timeout=10000'
    git config --global core.autocrlf true
    wget https://raw.githubusercontent.com/git/git/master/contrib/completion/git-completion.bash
    wget https://raw.githubusercontent.com/git/git/master/contrib/completion/git-prompt.sh
    wget https://www.udacity.com/api/nodes/3333158951/supplemental_media/bash-profile-course/download
    cat download >> .bashrc
    rm download
   SHELL
end
