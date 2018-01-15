# ansible-backup-check
Check backup files using Ansible

# Pre-requisite
  - Virtualbox
  - Vagrant
  - [Google App Specific Password](https://security.google.com/settings/security/apppasswords) - You'll need to create a `Mail` app password.
  
# Setup
  - Install `Virtualbox` and `Vagrant` in your local machine.
  - Clone this repo.
  - Run `vagrant up`.
  - Once vagrant setup is complete, following assumptions will be made:
    - `machine1` will be the control machine.
    - Backup checks will be performed in `machine2` and `machine3`.
  - Now we need to copy `machine1`'s pubic key to `machine2` and `machine3`, so that Ansible script can use ssh tunnel when required.
    - Run `vagrant ssh machine1` in your local machine's terminal. You should be in `machine1`'s terminal now.
    - Copy the content of `~/.ssh/id_rsa.pub`.
    - Login into `machine2` using the command: `ssh ubuntu@192.168.77.22` (used in Vagrantfile) and providing the password for `ubuntu` user in Vagrantfile.
    - Once you are logged into `machine2`, append the copied content to `~/.ssh/authorized_keys`.
    - Repeat these above two steps for `machine3`.
    - Use `exit` command to logout from `machine2` or `machine3` to go back to `machine1` terminal.
  - While logged-in in `machine1` terminal, edit the `/etc/environment` file (you may need to use sudo) and append the following commands:
    ```bash
    export SMTP_HOST="smtp.gmail.com"
    export SMTP_PORT=587
    export SMTP_SEND_FROM='from_email@gmail.com'
    export SMTP_PASSWORD='google_mail_app_pass'
    export SMTP_SEND_TO='First Last <to_email@example.com>'
    ```
  - Now run `source /etc/environment` command and maybe check one of the env variable by echoing using the: `echo $SMTP_SEND_FROM` command. You should see a line printed with the value of `SMTP_SEND_FROM` from `/etc/environment` file. i.e: `from_email@gmail.com`.
  - If everything looks good so far, then we are ready to run the ansible script. Issue this command in your `machine1` terminal: `ansible-playbook automated_checks.yml`.
  - You will get an email in your `SMTP_SEND_TO` account if you have backup files missing in your archiever servers.
