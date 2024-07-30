#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import argparse
import re 

home_path = "/home/keith/code/"
git_hub_username = "keith-taylor"
default_python = "3.12.4"
pyenv_virtualenv_suffix = "_env"
files_and_folders_list = ["src/__init__.py", "project.toml", "src/main.py", "docs/index.rst",
                              "tests/__init__.py"]

def run_command(command):
    try:
        result = subprocess.run(command, check=True, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        sys.exit(1) 

def main():
    parser = argparse.ArgumentParser(description="Set up a new Python project folder.")
    parser.add_argument("folder_name", help="Name of the project folder and virtual environment")
    parser.add_argument("--pyv", default=default_python, help="Python version to use")
    args = parser.parse_args()

    # Get list of installed Python versions
    # and check that these include default_python and args.pyv 
    pattern = re.compile(r'^\s*([0-9]+\.[0-9]+(\.[0-9]+)?)\s*$') # used to filter for numerical (non-alpha) values only
    installed_versions = run_command("pyenv versions --bare").splitlines() # get the installed versions list from pyenv
    
    # strips out virtualenvs from `installed_versions` leaving only actuall python version numbers:
    bare_python_versions = [line.strip() for line in installed_versions if pattern.match(line)] 
    
    # check if the default Python version specified at top of this file exists in pyenv
    if default_python not in bare_python_versions:
        print("\n*******************************************************************************************\nNote!\n")
        print(f"Python {default_python} is specified as the default version of Python but this is NOT currently installed. \n")
        print(f"You must either: ")
        print(f"\t- install Python {default_python} (`pyenv install {default_python}`) or,")
        print("\t- edit this script to specify an already intalled Python version as the default. \n")
        print("The currently installed Python versions are: ")
        for each_version in bare_python_versions:
            print(each_version) 
        print("*******************************************************************************************\n")
        sys.exit(1) 
    
    # check if the specified Python version is installed in pyenv  
    if args.pyv not in bare_python_versions:
        print("*******************************************************************************************\nNote!\n")
        print(f"Python version '{args.pyv}' is not currently installed in pyenv.")
        print("The Python versions currently installed are: ")
        # while printing the python versions installed in pyenv,
        # build a dict of option numbers and python versions for the user to choose from, 
        # this allows getting the user to choose a simple integer and reduce the potentail for errors
        count = 1
        version_dic = {}
        for each_version in bare_python_versions:
            print(f"({count}) {each_version}")
            version_dic[int(count)] = each_version
            count += 1 
            
        print("\nDo you want to: ")
        choice = input(f"\t[1] use one of the installed versions listed above \n\t[2] continue with the default Python version ({default_python}) \n\t[3] install a new Python version into pyenv or abort \nChoose: ").strip()
        if choice == '2':
            # 2. defualt python version choosen
            args.pyv = default_python
            print(f"\nSetting the Python version to: {args.pyv}")
            
        elif choice == '1':
            # 1. we're using one of the already installed Python versions 
            
            # creating a list of the installable option numbers for printing to screen
            version_option_nums = []
            for each_version in version_dic:
                version_option_nums.append(each_version)
            
            # prompt the user for a choice and then action that choice
            while True:
                try:
                    if len(version_option_nums) <8: # just in case there's a huge list of versions
                        selected_option = int(input(f"Please choose an option from the Python versions listed above {*(version_option_nums), } or 0 to exit: "))
                    else:
                        selected_option = int(input(f"Please choose an option from the Python versions listed above (1 to {len(version_option_nums)}) or 0 to exit: "))
                    if selected_option in version_option_nums:
                        args.pyv = version_dic[selected_option] # take the option number and lookup the Python version associated with it
                        print(f"\nSetting the Python version to: {args.pyv}")
                        break
                    elif selected_option == int(0):
                        print("\nAborting!")
                        sys.exit(1)
                    else:
                        print("Invalid input! Please enter an integer number from the options listed above.")
                except ValueError:
                    print("Invalid input! Please enter an integer value from the options listed above.")
        
        else:
            # 3. we're out of here, let's exit the script
            print("\nAborting! Please install your desired Python version into pyenv and run this script again. ")
            sys.exit(1)

    # Check if project folder already exists
    project_path = os.path.expanduser(f"{home_path}{args.folder_name}")
    if os.path.exists(project_path): 
        print(f"Error: Folder '{project_path}' already exists. Aborting.")
        print("You can delete this folder and run this script again if you wish.")
        sys.exit(1)
    else:
        print(f"Created folder: {project_path}")
        
    # Create project folders structure and initial files
    os.makedirs(project_path)
    for item in files_and_folders_list:
        item_path = os.path.join(project_path, item)
        if "." in item: # i.e. assuming it is a file
            # check the directory that's required exists, if not create
            os.makedirs(os.path.dirname(item_path), exist_ok=True)
            # Create an empty file
            with open(item_path, 'w') as f:
                pass
            print(f"Created file: {item_path}")
        else:
            # Create a directory
            os.makedirs(item_path, exist_ok=True)
            print(f"Created directory: {item_path}")
            print(f"added: {item_path}")
    
    # Copy default templates
    template_path = os.path.expanduser(f"{home_path}default_templates")
    if os.path.exists(template_path):
        for item in os.listdir(template_path):
            s = os.path.join(template_path, item)
            d = os.path.join(project_path, item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
        print("Copied default templates")
    else:
        print("Default templates folder not found")

    # Initialize git
    os.chdir(project_path)
    run_command("git init -b main")
    run_command("git add -A")
    run_command("git commit -m \"First commit, adding file structure.\" ")
    # run_command(f"git remote set-url origin git@github.com:{git_hub_username}/{args.folder_name}.git")
    # run_command("git push -u origin main")
    print("\n")
    print("*******************************************************************************************")
    print("NOTE!")
    print("A git repository was initialised. ")
    print("If you require a remote repo you need to add this manually. You can then link using, eg:")
    print(f"git remote set-url origin git@github.com:{git_hub_username}/{args.folder_name}.git")
    print("git push -u origin main")
    print("*******************************************************************************************\n")

    # Set Python version
    run_command(f"pyenv local {args.pyv}")
    print(f"The Python version was set to {args.pyv}")

    # Create virtual environment
    run_command(f"pyenv virtualenv {args.pyv} {args.folder_name}{pyenv_virtualenv_suffix}")
    run_command(f"pyenv local {args.folder_name}{pyenv_virtualenv_suffix}")
    print(f"Created and set pyenv local virtual environment: {args.folder_name}{pyenv_virtualenv_suffix}\n")

    print("Project setup complete!")

if __name__ == "__main__":
    main()
