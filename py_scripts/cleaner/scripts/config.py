import os

def read_config_file(file_name):
    """
    Reads a text file and prints its content.
    Parameters:
    - file_path: str, the path to the text file to be read.
    """
    try:
        # Append the file name to the current directory path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(script_dir, file_name)
        #print(full_path)
        with open(full_path, 'r') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print(f"The file at {file_name} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_configs(config_filename):
    string = read_config_file(config_filename)
    out = {}
    lines=string.split('\n')
    for line in lines:
        if len(line)>0:
            if line[0] == '#':
                newl=line.split("[")
                if newl[0] == '#csv_dump_path: ':
                    out['path'] = newl[1][:-1]
                elif newl[0] == '#indicator_of_interest: ':
                    indicator_ls = newl[1][:-1].split(';')
                    out['indicators'] = indicator_ls
    return out    



