# -*- mode: ruby -*-
# vi: set ft=ruby :

# WARNING: You will need the following plugin:
# vagrant plugin install vagrant-docker-compose
if Vagrant.plugins_enabled?
  unless Vagrant.has_plugin?('vagrant-docker-compose')
    puts 'Plugin missing.'
    system('vagrant plugin install vagrant-docker-compose')
    puts 'Dependencies installed, please try the command again.'
    exit
  end
end

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
    # Every Vagrant development environment requires a box. You can search for
    # boxes at https://atlas.hashicorp.com/search.
    config.vm.box = "ubuntu/bionic64"
    config.vm.hostname = "orders"
  
    # set up network ip and port forwarding
    config.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"
    config.vm.network "forwarded_port", guest: 8001, host: 8001, host_ip: "127.0.0.1"
    config.vm.network "forwarded_port", guest: 5432, host: 5432, host_ip: "127.0.0.1"

    config.vm.network "private_network", ip: "192.168.33.10"
  
    # Windows users need to change the permission of files and directories
    # so that nosetests runs without extra arguments.
    # Mac users can comment this next line out
    config.vm.synced_folder ".", "/vagrant", mount_options: ["dmode=775,fmode=664"]
  
    ######################################################################
    # Create a virtual machine
    ######################################################################
    config.vm.provider "virtualbox" do |vb|
      # Customize the amount of memory on the VM:
      vb.memory = "512"
      vb.cpus = 1
      # Fixes some DNS issues on some networks
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
    end
  
    ######################################################################
    # Copy some files to make developing easier
    ######################################################################
  
    # Copy your .gitconfig file so that your git credentials are correct
    if File.exists?(File.expand_path("~/.gitconfig"))
      config.vm.provision "file", source: "~/.gitconfig", destination: "~/.gitconfig"
    end
  
    # Copy your ssh keys for github so that your git credentials work
    if File.exists?(File.expand_path("~/.ssh/id_rsa"))
      config.vm.provision "file", source: "~/.ssh/id_rsa", destination: "~/.ssh/id_rsa"
    end
  
    # Copy your ~/.vimrc file so that vi looks the same
    if File.exists?(File.expand_path("~/.vimrc"))
      config.vm.provision "file", source: "~/.vimrc", destination: "~/.vimrc"
    end
    # Copy your IBM Cloud API Key if you have one
    if File.exists?(File.expand_path("~/.bluemix/apiKey.json"))
      config.vm.provision "file", source: "~/.bluemix/apiKey.json", destination: "~/.bluemix/apiKey.json"
    end

    ######################################################################
    # Add PostgreSQL docker container
    ######################################################################
    # docker run -d --name postgres -p 5432:5432 -v psql_data:/var/lib/postgresql/data postgres
    config.vm.provision :docker do |d|
      d.pull_images "postgres:alpine"
      d.run "postgres:alpine",
         args: "-d --name postgres -p 5432:5432 -v psql_data:/var/lib/postgresql/data -e POSTGRES_PASSWORD=postgres"
    end

    ############################################################
    # Create a Python 3 environment for development work
    ############################################################
    config.vm.provision "shell", inline: <<-SHELL
      # Update and install
      apt-get update
      apt-get install -y git tree wget python3-dev python3-pip python3-venv apt-transport-https
      apt-get upgrade python3
      # Create a Python3 Virtual Environment and Activate it in .profile
      sudo -H -u vagrant sh -c 'python3 -m venv ~/venv'
      sudo -H -u vagrant sh -c 'echo ". ~/venv/bin/activate" >> ~/.profile'
      sudo -H -u vagrant sh -c '. ~/venv/bin/activate && cd /vagrant && pip install -r requirements.txt'
      #Add a test DB
      docker exec postgres psql -c 'create database testdb;' -U postgres
    SHELL

    ############################################################
    # Add Docker compose
    ############################################################
    config.vm.provision :docker_compose
    # config.vm.provision :docker_compose,
    #   yml: "/vagrant/docker-compose.yml",
    #   rebuild: true,
    #   run: "always"

  ######################################################################
  # Setup a Bluemix and Kubernetes environment
  ######################################################################
  config.vm.provision "shell", inline: <<-SHELL
    echo "\n************************************"
    echo " Installing IBM Cloud CLI..."
    echo "************************************\n"
    # Install IBM Cloud CLI as Vagrant user
    sudo -H -u vagrant sh -c 'curl -sL http://ibm.biz/idt-installer | bash'
    sudo -H -u vagrant sh -c "echo 'source <(kubectl completion bash)' >> ~/.bashrc"
    sudo -H -u vagrant sh -c "ibmcloud cf install --version 6.46.1"
    sudo -H -u vagrant sh -c "echo alias ic=/usr/local/bin/ibmcloud >> ~/.bash_aliases"
    echo "\n"
    echo "If you have an IBM Cloud API key in ~/.bluemix/apiKey.json"
    echo "You can login with the following command:"
    echo "\n"
    echo "ibmcloud login -a https://cloud.ibm.com --apikey @~/.bluemix/apiKey.json -r us-south"
    echo "\n"
    echo "\n************************************"
    echo " For the Kubernetes Dashboard use:"
    echo " kubectl proxy --address='0.0.0.0'"
    echo "************************************\n"
  SHELL

  end