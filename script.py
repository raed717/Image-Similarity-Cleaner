import os
import imagehash
from PIL import Image
import logging
import matplotlib.pyplot as plt
from tqdm import tqdm
import argparse
import shutil

# Configure logging
logging.basicConfig(filename="similar_images_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

def hash_image(file_path):
    """Calculates the perceptual hash of an image to identify similarities."""
    try:
        with Image.open(file_path) as img:
            return imagehash.phash(img)
    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        return None

def display_and_confirm_deletion(original_path, duplicate_path):
    """
    Displays two similar images side by side and asks for confirmation to delete one.
    """
    # Load images
    img1 = Image.open(original_path)
    img2 = Image.open(duplicate_path)

    # Display images side by side
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    axs[0].imshow(img1)
    axs[0].axis('off')
    title1 = f"Original Image\n{original_path}"
    axs[0].set_title(title1)

    axs[1].imshow(img2)
    axs[1].axis('off')
    title2 = f"Duplicate Image\n{duplicate_path}"
    axs[1].set_title(title2)

    plt.show()

    # Get user confirmation
    choice = input(f"Options: '1' to delete original, '2' to delete duplicate, 'n' to keep both. Choice: ")

    # Close images
    plt.close(fig)
    img1.close()
    img2.close()

    # Delete based on user choice
    if choice.lower() == '1':
        return original_path
    elif choice.lower() == '2':
        return duplicate_path
    else:
        return None

def auto_delete_decision(original_path, duplicate_path, keep_larger=True):
    """
    Automatically decides which image to delete based on file size.
    """
    # Check if the files exist
    if not os.path.exists(original_path):
        logging.warning(f"Original file {original_path} not found.")
        return duplicate_path
    if not os.path.exists(duplicate_path):
        logging.warning(f"Duplicate file {duplicate_path} not found.")
        return original_path

    try:
        size_original = os.path.getsize(original_path)
    except FileNotFoundError:
        logging.warning(f"Original file {original_path} not found during size check.")
        return duplicate_path

    try:
        size_duplicate = os.path.getsize(duplicate_path)
    except FileNotFoundError:
        logging.warning(f"Duplicate file {duplicate_path} not found during size check.")
        return original_path

    if keep_larger:
        if size_original >= size_duplicate:
            return duplicate_path  # Delete smaller
        else:
            return original_path
    else:
        if size_original >= size_duplicate:
            return original_path  # Delete larger
        else:
            return duplicate_path

def find_and_delete_similar_images(folder_path, threshold, interactive=True, auto_keep_larger=True, trash_folder=None):
    """
    Finds and deletes similar images using perceptual hash difference.
    """
    hashes = {}
    similar_images = set()
    image_files = []
    deleted_files = set()  # Keep track of deleted files

    # Collect all image files
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.nef')):
                file_path = os.path.join(root, file_name)
                image_files.append(file_path)

    print(f"Processing {len(image_files)} images...")

    # Compute hashes with progress bar
    hash_dict = {}
    for file_path in tqdm(image_files, desc="Hashing images"):
        file_hash = hash_image(file_path)
        if file_hash is not None:
            hash_dict[file_path] = file_hash

    # Find similar images
    processed = set()
    items = list(hash_dict.items())
    for i, (file_path, file_hash) in enumerate(tqdm(items, desc="Comparing images")):
        if file_path in processed or file_path in deleted_files or not os.path.exists(file_path):
            continue
        duplicates = []
        for other_path, other_hash in items[i+1:]:
            if other_path not in processed and other_path not in deleted_files and os.path.exists(other_path):
                if abs(file_hash - other_hash) < threshold:
                    duplicates.append(other_path)

        if duplicates:
            processed.add(file_path)
            processed.update(duplicates)
            similar_images.add(file_path)
            similar_images.update(duplicates)

            for duplicate_path in duplicates:
                if duplicate_path in deleted_files or not os.path.exists(duplicate_path):
                    continue
                logging.info(f"Similar images found: {file_path} and {duplicate_path}")

                # Decide whether to delete one of the images
                if interactive:
                    delete_path = display_and_confirm_deletion(file_path, duplicate_path)
                else:
                    delete_path = auto_delete_decision(file_path, duplicate_path, keep_larger=auto_keep_larger)

                if delete_path:
                    if trash_folder:
                        # Move file to trash folder
                        os.makedirs(trash_folder, exist_ok=True)
                        shutil.move(delete_path, os.path.join(trash_folder, os.path.basename(delete_path)))
                    else:
                        os.remove(delete_path)
                    logging.info(f"Deleted image: {delete_path}")
                    print(f"Deleted image: {delete_path}")

                    # Add deleted file to deleted_files set
                    deleted_files.add(delete_path)
                else:
                    print(f"Both images kept: {file_path} and {duplicate_path}")

    print(f"Total similar images found: {len(similar_images)}")
    print("Log file created: similar_images_log.txt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find and delete similar images.')
    parser.add_argument('folder_path', type=str, help='Path to the folder containing images.')
    parser.add_argument('--threshold', type=int, default=10, help='Threshold for image similarity (default: 10)')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode.')
    parser.add_argument('--auto_keep_larger', action='store_true', help='When auto-deleting, keep the larger file (default).')
    parser.add_argument('--auto_keep_smaller', action='store_true', help='When auto-deleting, keep the smaller file.')
    parser.add_argument('--trash_folder', type=str, help='Folder to move deleted images instead of deleting permanently.')
    args = parser.parse_args()

    if args.auto_keep_smaller:
        auto_keep_larger = False
    else:
        auto_keep_larger = True

    find_and_delete_similar_images(
        folder_path=args.folder_path,
        threshold=args.threshold,
        interactive=args.interactive,
        auto_keep_larger=auto_keep_larger,
        trash_folder=args.trash_folder
    )

