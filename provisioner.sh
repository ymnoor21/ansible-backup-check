#!/bin/bash

sudo apt-get -y update &&
	apt-get -y install build-essential checkinstall &&
	apt-get -y install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev &&
	apt-get -y install python-dev &&
	apt-get -y install python-pip &&
	pip install --upgrade pip
