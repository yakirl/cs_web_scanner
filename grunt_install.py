__author__ = 'Samuel'

from git import Repo
import os
import shutil

repo_url = "https://github.com/yargalot/grunt-accessibility.git"

BASE_DIR = os.path.dirname(__file__)
#BASE_DIR = "E:\\files\\backups\\latest_linux_backup\\cs_web_scanner_proj"
#BASE_DIR = "/home/yakir/cs_web_scanner_proj"

LOCAL_REPO = os.path.join(BASE_DIR, "Grunt_repo_demo")
LOCAL_DIR  = os.path.join(BASE_DIR, "Grunt_demo")
GRUNT_DIR  = os.path.join(BASE_DIR, "node_modules", "grunt-accessibility")
TEST_DIR   = os.path.join(GRUNT_DIR, "example")

#print ("setting up environment...")
#if not os.path.exists(LOCAL_REPO):
#    os.mkdir(LOCAL_REPO)
#    print ("Cloning grunt-accessibility from git...")
#    Repo.clone_from(repo_url, LOCAL_REPO)
#if not os.path.exists(LOCAL_DIR):
#    os.mkdir(LOCAL_DIR)
#os.chdir(LOCAL_DIR)
#
#
#
#print ("\nInstalling npm...")
#os.system('sudo apt-get install npm -y')
#
#
#print ("\nInstalling Grunt Deps...")
#os.system("sudo npm install -g grunt-cli")
#os.system("sudo npm install grunt")
#os.system("sudo npm install grunt-accessibility")
#os.system("sudo npm install grunt --save-dev time-grunt")
#os.system("sudo npm install grunt --save-dev load-grunt-tasks")
#os.system("sudo npm install grunt --save-dev grunt-bump")
#os.system("sudo npm install grunt --save-dev grunt-contrib-clean")
#os.system("sudo npm install grunt --save-dev grunt-contrib-jshint")
#os.system("sudo npm install grunt --save-dev grunt-contrib-nodeunit")
#os.system("sudo npm install grunt --save-dev grunt-contrib-watch")
#os.system("sudo npm install grunt --save-dev grunt-debug-task")
#
try:
    if not os.path.exists(TEST_DIR):
        os.makedirs(TEST_DIR)
except:
    print ("Error: repository from git didn't clone properly or NPM not installed")
    raise

cmd='cp '+os.path.join(BASE_DIR, 'Gruntfile.js')+' '+GRUNT_DIR+' --force'
os.system(cmd)
#if not os.path.isfile(GRUNT_DIR+"/Gruntfile.js"):
#    shutil.copyfile(LOCAL_REPO+"/Gruntfile.js",GRUNT_DIR)

print ("All installed properly!")
