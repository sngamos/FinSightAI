from key_finder import get_keys_of_interest
from cleaning import make_dict
from crawl_folder import list_files_in_folder
from config import get_configs
from json_create import make_json,make_folder

config_filename = 'config.txt'

if __name__ == '__main__':
    config_dict = get_configs(config_filename)
    #print(config_dict)
    csv_dump = config_dict['path']
    indicator_ls = config_dict['indicators']
    #first make list of all csv paths using folder crawler
    files_ls = list_files_in_folder(csv_dump)
    counter = 0
    for file_path in files_ls:
        key_ls = get_keys_of_interest(indicator_ls,file_path)
        #print(key_ls)
        temp_dict = make_dict(file_path,key_ls)
        print(temp_dict)
        company_name = file_path.split("\\")[-1].replace('.xls','')
        make_folder()
        make_json(temp_dict,company_name)
        counter +=1
    print(f"SUCCESS: Created {counter} json files")
    




    