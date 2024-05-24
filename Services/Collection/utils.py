import glob
import os


def clean_out_csvs(path: str) -> None:
    """
    Delete all current csvs in a given path
    :param path: The path to the folder we want to delete all files in
    :return: None
    """
    try:
        files = glob.glob(os.path.join(path, '*'))
        for file in files:
            if os.path.isfile(file):
                os.remove(file)
    except OSError:
        print("Error occurred while deleting files.")
