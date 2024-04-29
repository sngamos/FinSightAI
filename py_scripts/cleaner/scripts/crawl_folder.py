import os


def list_files_in_folder(directory):
    """
    Crawls a folder and returns a list of full paths of files within it.

    Parameters:
    - directory (str): The directory path to crawl.

    Returns:
    - list: A list of full file paths contained in the directory.
    """
    file_paths = []  # List to store full paths of files
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)  # Construct full file path
            file_paths.append(file_path)  # Add it to the list
    return file_paths