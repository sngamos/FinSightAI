import os
import subprocess
def get_cleaner_path():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Move one directory level up
    parent_dir = os.path.dirname(script_dir)
    # Construct the full path to the folder
    cleaner_folder_path = os.path.join(parent_dir, 'cleaner')
    return cleaner_folder_path

def get_dump_path():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Move one directory level up
    parent_dir = os.path.dirname(script_dir)
    # Construct the full path to the folder
    cleaner_folder_path = os.path.join(parent_dir, 'cleaner')
    json_folder_path = os.path.join(cleaner_folder_path,'json_dump')
    return json_folder_path

def check_json_exist():
    json_folder_path =get_dump_path()
    #print('Checking if json_dump exist')
    #check if json_dump folder exists, if not run cleaner to create json files and folder
    if not os.path.exists(json_folder_path):
        print('json_dump doesnt exist\nGenerating json files...')
        return False
    else:
        return json_folder_path

def make_json_dump(parent_dir):
    print('json_dump doesnt exist\nGenerating json files...')
    program_path = os.path.join(parent_dir,'scripts\\main.py')
    run_file(program_path)
    return os.path.join(parent_dir,'json_dump')


def run_file(file_path):
    try:
        # Run the Python script as a separate process
        result = subprocess.run(['python', file_path], check=True, text=True, capture_output=True)
        print(f"Script {file_path} executed successfully.")
        print("Output:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing script {file_path}:")
        print(e.output)

def get_jsons_ls():
    out_ls = []
    json_path = check_json_exist()
    if json_path ==False:
        json_path = make_json_dump(get_cleaner_path())
    for root, dirs, files in os.walk(json_path):
        for file in files:
            file_path = os.path.join(root, file)  # Construct full file path
            out_ls.append(file_path)  # Add it to the list
    return out_ls
    
    


