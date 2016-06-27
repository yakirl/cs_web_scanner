#!/bin/bash

LOG_FILE="logs/install.log"

echo "install log" > $LOG_FILE
sudo chmod 777 $LOG_FILE

function Clean {
    echo "Cleaning..."
    sudo rm -f data/mapper/*
    sudo rm -f data/inspector/*
    sudo rm -f data/reports
    sudo rm -f logs/*
    sudo rm -rf tmp
}


function InstallPackages {
    #install basic usefull packages:
    sudo apt-get update > $LOG_FILE
    sudo apt-get upgrade >> $LOG_FILE
    pkgs=( python-git python-tk  trash-cli git meld gedit vim tree dconf-tools python-pip )
    for pkg in ${pkgs[@]}; do
        sudo apt-get -y install  $pkg >> $LOG_FILE
    done
}

function InstallPython {
    sudo pip install --upgrade pip >> $LOG_FILE
    sudo apt-get build-dep matplotlib >> $LOG_FILE
    sudo apt-get build-dep numpy >> $LOG_FILE

    pkgs=( bs4 matplotlib numpy enum certifi pulp )
    for pkg in ${pkgs[@]}; do
        sudo pip install $pkg > /dev/null >> $LOG_FILE
    done
}


function SaveLoadConfs {
    if [[ $1 == "load" ]]; then
        FROM="~/home_backup"
        TO="~/"
    elif [[ $1 == "save" ]]; then
        FROM="~/"
        TO="~/home_backup"
        mkdir $TO
    else
        Use
    fi

    CONF_FILES=( ".gitconfig" ".vimrc" ".bashrc" )
    for file in ${CONF_FILES[@]}; do
        sudo cp -Rf ${FROM}/${file}  ${TO}
    done

    sudo cp -f ${FROM}/.config/gtk-3.0/gtk.css ${TO}/.config/gtk-3.0/gtk.css
    # close all terminals and reopen

}

function setCtags {
    # ctags for python:
    sudo apt-get -y install  aptitude >> $LOG_FILE
    aptitude install exuberant-ctags >> $LOG_FILE
    echo "--python-kinds=-i" > ~/.ctags
}



if   (( $# == 0 )); then
	InstallPackages
	InstallPython
	python grunt_install.py
elif [[ $1 == "clean" ]]; then
	Clean 
elif [[ $1 == "build-dep" ]]; then
	InstallPackages
	InstallPython
else
	echo "Use: $0 "
	echo "or:"
	echo "Use: $0 <clean/build-dep>"
	exit
fi


