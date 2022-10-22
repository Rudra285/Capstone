My Garage App

The My Garage App is meant to allow vehicle owners to keep track of the maintenance performed to their vehicles over the course of the vehicle's life span. By implementing blockchain technology the mainteance follows the vehicle even when owners buy and sell a vehicle, allowing buyers to be better informed of their potential purchase. 

The Basics
  BigChainDB is the blockchain/immutable ledger technology used as the database to store maintenance information. 
      https://github.com/bigchaindb/bigchaindb/blob/master/README.md
      https://www.bigchaindb.com/
  KivyMD is a python based coding language which was chosen by the My Garage App team due to it being easy to use, cross platform, fast and its collection of       Material Design widgets
      https://kivymd.readthedocs.io/en/latest/
      https://kivy.org/
      https://gitlab.com/kivymd/KivyMD
   
Project Setup 
  Operating System:
    Ubuntu 20.04
  Drivers Required:
    Python 3.5+ and pip, pip3 and python 3 version of setuptools must be pre-installed. 
        sudo apt update
        sudo apt install python3
        sudo apt install -y python3-pip
        sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
        sudo pip3 install --upgrade setuptools
        
    Kivy:
      Update pip and other instllation dependencies: 
          python -m pip install --upgrade pip setuptools virtualenv
      Create a virtual environment for kivy: 
          python -m virtualenv kivy_venv
      Activate the virtual environment:
          source kivy_venv/bin/activate
      Your terminal should now preface the path with something like (kivy_venv), indicating that the kivy_venv environment is active.
      Install Kivy
          python -m pip install "kivy[base]" kivy_examples
          
    KivyMD:
      Install KivyMD:
          pip install kivymd
    
    BigChainDB Python:
      Install the latest stable BigchainDB Python Driver:
          pip3 install bigchaindb_driver
    
  BigChainDB Server:
    Test server which is wiped everyday:
        https://test.ipdb.io
    Or setup your own BigChainDB server by following the guide created by BigChainDB:
        https://bigchaindb.readthedocs.io/en/latest/installation/index.html
    
    
My Garage App:
  Install the My Garage App:
      git clone https://github.com/Rudra285/Capstone
  Change the bdb_root_url located on (list the pages) to the location of the BigChainDB server you are using
  
          
      
          
      
      
