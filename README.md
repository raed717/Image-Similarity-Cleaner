# Image Similarity Cleaner

This script is designed to help manage storage space by identifying and removing similar images within a specified folder. Using perceptual hashing, it calculates the similarity between images, allowing the user to decide which duplicates to keep or delete. 

## Features

- **Perceptual Hashing:** Calculates image similarity using `imagehash`.
- **Interactive Deletion:** Allows the user to view similar images side-by-side and choose which to delete.
- **Automatic Deletion:** Automatically deletes smaller or larger images based on preference.
- **Trash Folder Support:** Optionally moves deleted images to a specified trash folder instead of permanent deletion.
- **Logging:** Records details of all deleted images and errors in `similar_images_log.txt`.

## Requirements

- Python 3.x
- Libraries: `PIL`, `imagehash`, `matplotlib`, `tqdm`, `argparse`, `logging`, `shutil`

Install required libraries:
```bash
pip install pillow imagehash matplotlib tqdm
Usage
Run the script with:

python image_cleaner.py <folder_path> [options]
Arguments
folder_path: The path to the folder containing images.
Options
--threshold : Similarity threshold for detecting duplicates. Default is 10.
--interactive : Enables interactive mode, where the user manually decides which images to delete.
--auto_keep_larger : When auto-deleting, keep the larger file (default).
--auto_keep_smaller : When auto-deleting, keep the smaller file.
--trash_folder : Path to a folder where deleted images will be moved instead of permanently deleting.
Example Commands
Run in interactive mode:


python image_cleaner.py ./images --threshold 5 --interactive
This will display similar images side-by-side and prompt the user to choose which to delete.

Run in automatic mode, keeping larger files, and using a trash folder:


python image_cleaner.py ./images --threshold 5 --auto_keep_larger --trash_folder ./deleted_images
Logging
All operations and errors are logged in similar_images_log.txt in the working directory.

License
This project is open-source and free to use.


This `README.md` covers installation, usage examples, and script options. Let me know if you'd like to add anything specific.