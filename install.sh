#!/bin/bash

function Clean {
    sudo rm -f data/mapper/*
    sudo rm -f data/inspector/*
    sudo rm -f logs/*
    sudo rm -rf tmp
}

Clean
