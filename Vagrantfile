Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"

  config.vm.define "machine1" do |machine|
    machine.vm.hostname = "machine1"
    machine.vm.network "private_network", ip: "192.168.77.21"
    machine.vm.provision "shell", path: "provisioner.sh"
    machine.vm.provision "shell", inline: <<-SCRIPT
        sudo apt-get -y update && 
        apt-get -y install software-properties-common &&
        apt-add-repository -y ppa:ansible/ansible &&
        apt-get -y update &&
        apt-get -y install ansible &&
        echo "[archivers]" >> /etc/ansible/hosts &&
        echo "192.168.77.22" >> /etc/ansible/hosts &&
        echo "192.168.77.23" >> /etc/ansible/hosts &&
        cat /etc/ansible/hosts
      SCRIPT

    $script = <<-SCRIPT
      ssh-keygen -t rsa -b 4096 -C 'ubuntu@machine1' -N '' -f $HOME/.ssh/id_rsa
    SCRIPT

    machine.vm.provision "shell", inline: $script, privileged: false
  end

  config.vm.define "machine2" do |machine|
    machine.vm.hostname = "machine2"
    machine.vm.network "private_network", ip: "192.168.77.22"
    machine.vm.provision "shell", path: "provisioner.sh"
  end

  config.vm.define "machine3" do |machine|
    machine.vm.hostname = "machine3"
    machine.vm.network "private_network", ip: "192.168.77.23"
    machine.vm.provision "shell", path: "provisioner.sh"

    machine.vm.provision :ansible do |ansible|
      ansible.limit = "all"
      ansible.playbook = "playbook.yml"
    end
  end

  config.vm.provision "shell", inline: <<-SCRIPT
    echo "Updating ubuntu password"
    echo "ubuntu:ubuntu" | chpasswd
  SCRIPT
end
