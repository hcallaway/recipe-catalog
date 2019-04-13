# Full Stack Web Developer Nanodegree Progam
## Item Catalog Project
### By Houston Callaway

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Requirements](#requirements)
- [Getting Started](#getting-started)
- [App Use]("#app-use)

## Requirements
* [Vagrant](https://www.vagrantup.com/downloads.html)
* [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)
* [Vagrant Configuration](https://github.com/udacity/fullstack-nanodegree-vm) - provided by Udacity

## Getting Started
### Can run with Python 2.7 or Python 3.x
* Install [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) -- You do not need to launch VirtualBox after installing
    * Note: **Ubuntu 14.04 Users** you will need to install VirtualBox using the Ubuntu Software Center, due to a reported bug
* Install [Vagrant](https://www.vagrantup.com/downloads.html)
    * Confirm Vagrant install is successful by running `vagrant --version`
* Download the VM configuration: [FSND-Virtual-Machine.zip](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip) or fork and clone the [Github Repository](https://github.com/udacity/fullstack-nanodegree-vm)
* After extracting .zip or cloning repo into desire directory, `cd` into the folder, then `cd` into the **/vagrant** directory
* Start the subdirectory by running the command `vagrant up` within the **/vagrant** directory
* Once `vagrant up` has completed, run `vagrant ssh` to log in to the newly installed Linux VM
* Cd to `/vagrant` to view shared folder file
* Run `python project.py` to start the project!

If you have any issues with the vagrant installation or configuration, you can view a more complete version of instructions [Here](https://github.com/udacity/fullstack-nanodegree-vm)

## App Use

To view JSON endpoints, visit `localhost:5000/recipes.json` (for recipes) or `localhost:5000/users.json` to see list of users in the app

![json-example](https://imgur.com/73i7W2t.jpg)

You can add, edit, and delete recipes 

View recipes based on category by clicking the categories dropdown in the navigation bar

![categories-location](https://imgur.com/R26JwPm.jpg)

[(Back to TOC)](#table-of-contents)