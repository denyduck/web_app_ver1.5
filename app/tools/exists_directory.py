import os

def existing_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f'Vytvořen adresář {directory}')
    else:
        print(f'Adresář {directory} existuje')