import xml.etree.ElementTree as ET
import glob
import os


def change_xml_files(images_path):
    files_changed_in_path = 0
    for file_path in glob.iglob(images_path + '/*.xml'):
        tree = ET.parse(file_path)
        changed_file = False

        folder_in_file = tree.find('folder').text
        image_path_in_file = tree.find('path').text

        folder_name = os.path.basename(os.path.dirname(file_path))
        if folder_in_file != folder_name:
            changed_file = True
            tree.find('folder').text = folder_name

        image_path = os.path.dirname(file_path) + os.sep + tree.find('filename').text
        if image_path_in_file != image_path:
            changed_file = True
            tree.find('path').text = image_path

        if changed_file:
            tree.write(file_path)
            files_changed_in_path += 1

    return files_changed_in_path


# Navigate to path of AI training and testing images.
os.chdir('Tensorflow/workspace/images/')

# Keep track of the amount of files changed so this can be displayed to the user.
files_changed = 0

# Loop through all training images.
os.chdir(os.getcwd() + '/train')
files_changed += change_xml_files(os.getcwd())

# Loop through all testing images.
os.chdir(os.getcwd() + '../../test')
files_changed += change_xml_files(os.getcwd())

print(f"Successfully changed {files_changed} XML files.")
