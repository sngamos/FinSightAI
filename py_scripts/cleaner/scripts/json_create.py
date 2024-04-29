import json
import os

folder_name = 'json_dump' #change as needed

def make_folder():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Move one directory level up
    parent_dir = os.path.dirname(script_dir)
    # Construct the full path to the folder
    folder_path = os.path.join(parent_dir, folder_name)
    
    # Check if the folder exists, and create it if it does not
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_name}' created at: {folder_path}")
    else:
        print(f"Folder '{folder_name}' already exists.")

def make_json(json_dict_input,json_filename=None):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Move one directory level up
    parent_dir = os.path.dirname(script_dir)
    folder_path = os.path.join(parent_dir, folder_name)
    if json_filename ==None:
        json_filename = input('please input json filename to save json file (without .json)')+'.json'
    file_path = os.path.join(folder_path, json_filename)
    with open(file_path,'w') as json_file:
        json.dump(json_dict_input,json_file,indent=4)
    print(f"Successfully created json file: {json_filename}")

