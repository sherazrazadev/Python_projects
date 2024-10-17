import os
import threading
import shutil
import pandas as pd
from PIL import Image, ImageEnhance, ImageOps, ImageDraw
import numpy as np
import potrace
from colorgram import colorgram
from sklearn.metrics import pairwise_distances_argmin
# GUI setup
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import google.generativeai as genai

# Initialize the Google AI Studio API key
# API_KEY = "AIzaSyAmIuFevL08rSbm6T1ROHnRZHjQSSxQwTg"

# Function to configure the API with the provided key
def configure_api(api_key):
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        messagebox.showerror("API Configuration Error", f"Failed to configure API: {e}")
        return False
    
# Configure the API with the key
def process_and_generate_tags(product_title, product_type):
    # Create the prompt based on product details
    prompt = (
        f"Give me 13 Etsy search phrases for the {product_title} {product_type}, "
        "maximum of 20 characters per phrase, no repeated words in any of the phrases, separated by commas, no list numbers."
    )

    try:
        # Load the model and generate the response
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        # Extract generated text and process it
        tags = response.text
        tag_list = tags.split(',')

        # Validate and clean up the tags
        tag_list = tag_list[:13]  # Ensure we have exactly 13 tags
        validated_tags = [tag.strip()[:20] for tag in tag_list]  # Trim any tag that exceeds 20 characters

        return validated_tags
    except Exception as e:
        print("Failed to generate tags:", str(e))
        return []
# Determine the log directory
home_dir = Path.home()
if os.name == 'nt':
    log_dir = home_dir / 'AppData' / 'Local' / 'Mockup Processor'
else:
    log_dir = home_dir / '.local' / 'share' / 'Mockup Processor'

log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / 'errors.log'

import logging
logging.basicConfig(
    # filename=log_file,  # Log file name
    level=logging.INFO,       # Set the logging level to ERROR
    format='%(asctime)s - %(levelname)s - %(message)s'  # Optional log message format
)


template_bounding_box = [(886, 227), (2577, 1773)]

# Function to create required folders in the output directory
def create_output_folders(base_folder):
    folders = ["Cup Mockup", "Design Mockup", "Hat Mockup", "RENAMED PNG", "Transfer Mockup", "Tshirt Mockup"]
    for folder in folders:
        os.makedirs(os.path.join(base_folder, folder), exist_ok=True)


import os
import shutil
import logging

# Constants for processing and mockup creation
MAX_WIDTH = 3000
MAX_HEIGHT = 3000
PNG_OPACITY = 0.8

# Pre-defined coordinates for each mockup image (multiple pastes) and rotation angles
tshirt_mockup_details = {
    "1.jpg": {
        "coordinates": [(1185, 308), (1858, 308), (1858, 1121), (1181, 1117)]
    },
    "3.jpg": {
        "coordinates": [(1061, 492), (1734, 492), (1738, 1312), (1061, 1304)]
    },
    "4.jpg": {
        "coordinates": [(826, 317), (1759, 312), (1755, 1429), (838, 1433)]
    },
    "5.jpg": {
        "coordinates": [(945, 529), (1639, 525), (1647, 1375), (941, 1375)]
    },
    "6.jpg": {
        "coordinates": [(619, 362), (1639, 367), (1639, 1596), (623, 1588)]
    }
}

# Function to create a new folder name based on PNG file name for tshirts
def create_new_tshirt_folder_name(png_file, design_code):
    # Define replacements for tshirt types
    tshirt_types = {
        'T-Shirt': 'T-Shirt, Sweatshirt, Hoodie, Tote Bag - ',
        'Raglan Baseball Tee': 'T-Shirt, Sweatshirt, Hoodie, Tote Bag - ',
        'Tank Top': 'T-Shirt, Sweatshirt, Hoodie, Tote Bag - ',
        'V-Neck T-Shirt': 'T-Shirt, Sweatshirt, Hoodie, Tote Bag - '
    }

    # Extract base name without extension
    base_name = os.path.splitext(png_file)[0]

    # Identify and replace the last words with corresponding tshirt type
    for tshirt_type, replacement in tshirt_types.items():
        if base_name.endswith(tshirt_type):
            base_name = base_name.replace(tshirt_type, replacement)
            break

    # Construct final folder name
    return f"{base_name}{design_code}"


# Function to process and save mockups for each PNG file in T-shirts
# Function to process and save mockups for each PNG file in T-shirts
def process_and_save_tshirt_mockups(png_file, folder_path, mockup_folder_tshirt, input_folder_tshirt):
    mockup_files = ["1.jpg", "3.jpg", "4.jpg", "5.jpg", "6.jpg"]
    png_source_path = os.path.join(input_folder_tshirt, png_file)

    for mockup_file in mockup_files:
        mockup_path = os.path.join(mockup_folder_tshirt, mockup_file)
        if not os.path.exists(mockup_path):
            logging.error(f"Mockup file not found: {mockup_path}")
            continue
        mockup_image = Image.open(mockup_path).convert("RGBA")
        png_image = Image.open(png_source_path).convert("RGBA")

        # Get predefined coordinates for the current mockup image
        coordinates = tshirt_mockup_details.get(mockup_file, {}).get("coordinates", None)
        if not coordinates:
            continue

        # Get bounding box from coordinates
        left = min(coordinates[0][0], coordinates[1][0], coordinates[2][0], coordinates[3][0])
        right = max(coordinates[0][0], coordinates[1][0], coordinates[2][0], coordinates[3][0])
        top = min(coordinates[0][1], coordinates[1][1], coordinates[2][1], coordinates[3][1])
        bottom = max(coordinates[0][1], coordinates[1][1], coordinates[2][1], coordinates[3][1])
        bounding_box = (left, top, right, bottom)

        # Resize PNG to fit within the bounding box and get adjusted position
        png_resized, position = resize_and_center_tshirt_image(png_image, bounding_box)

        # Paste the resized PNG into the mockup image at the adjusted position
        mockup_image.paste(png_resized, position, png_resized)

        # Save the combined image
        mockup_image.save(os.path.join(folder_path, mockup_file), "PNG")

    # Copy additional files
    shutil.copy(os.path.join(mockup_folder_tshirt, "2.jpg"), os.path.join(folder_path, "2.jpg"))
    shutil.copy(os.path.join(mockup_folder_tshirt, "7.jpg"), os.path.join(folder_path, "7.jpg"))
    shutil.copy(os.path.join(mockup_folder_tshirt, "8.jpg"), os.path.join(folder_path, "8.jpg"))

    

# Function to resize and center the image within the bounding box for T-shirts
# Function to resize and center the image within the bounding box for T-shirts
def resize_and_center_tshirt_image(image, bounding_box):
    max_width = bounding_box[2] - bounding_box[0]
    max_height = bounding_box[3] - bounding_box[1]
    
    # Resize the image to fit within the bounding box
    image.thumbnail((max_width, max_height), Image.LANCZOS)
    image = image.copy()

    # Check if the image is landscape (wider than tall)
    png_width, png_height = image.size
    if png_width > png_height:
        # Calculate the adjustment to move the PNG up for landscape images
        move_up_amount = 50  # Moving up by 50 pixels (about 4 fingers' width)
        # Ensure we don't move it beyond the bounding box
        new_top = max(bounding_box[1], bounding_box[1] - move_up_amount)
        position = (bounding_box[0] + (max_width - png_width) // 2, new_top)
    else:
        # For non-landscape images, center it normally
        position = (bounding_box[0] + (max_width - png_width) // 2,
                    bounding_box[1] + (max_height - png_height) // 2)

    return image, position


# Function to paste the image on the mockup at the specified coordinates for tshirts
def paste_tshirt_image_on_mockup(mockup_image, png_image, coordinates):
    # Calculate the position to center the image within the bounding box
    x_coords = [coord[0] for coord in coordinates]
    y_coords = [coord[1] for coord in coordinates]
    center_x = (max(x_coords) + min(x_coords)) // 2
    center_y = (max(y_coords) + min(y_coords)) // 2
    position = (center_x - png_image.width // 2, center_y - png_image.height // 2)

    # Paste the image onto the mockup with transparency
    mockup_image.paste(png_image, position, png_image)

    return mockup_image


#------Cup mockup------

# # Pre-defined coordinates for each mockup image (multiple pastes) and rotation angles
# cups_mockup_details = {
#     "1.jpg": {
#         "coordinates": [
#             [(1918, 677), (2383, 821), (2193, 1718), (1712, 1601)],  # Top image 
#             [(1568, 2230), (2067, 2337), (1930, 2866), (1487, 2772)]  # Bottom image 
#         ],
#         "rotation": 12
#     },
#     "2.jpg": {
#         "coordinates": [
#             [(1918, 797), (2434,951), (2193, 1848), (1712, 1731)], # Top Image
#             [(1574, 2224), (2061, 2331), (1930, 2848), (1487, 2772)] # bottom image
#         ],
#         "rotation": 13
#     },
#     "4.jpg": {
#         "coordinates": [
#             [(1504, 1020), (2277, 1092), (2126, 2350), (1374, 2257)]
#         ],
#         "rotation": 6
#     },
#     "5.jpg": {
#         "coordinates": [
#             [(1718, 2365), (3050, 2365), (3065, 3990), (1711, 3969)]
#         ],
#         "rotation": 0
#     }
# }

# # Function to create a new folder name based on PNG file name for cups
# def create_new_cup_folder_name(png_file, design_code):
#     # Define replacements for cup types
#     cup_types = {
#         'T-Shirt': '40oz Tumbler Quencher, 16oz Libbey Cup, 11oz Mug - ',
#         'Raglan Baseball Tee': '40oz Tumbler Quencher, 16oz Libbey Cup, 11oz Mug - ',
#         'Tank Top': '40oz Tumbler Quencher, 16oz Libbey Cup, 11oz Mug - ',
#         'V-Neck T-Shirt': '40oz Tumbler Quencher, 16oz Libbey Cup, 11oz Mug - '
#     }

#     # Extract base name without extension
#     base_name = os.path.splitext(png_file)[0]

#     # Identify and replace the last words with corresponding cup type
#     for cup_type, replacement in cup_types.items():
#         if base_name.endswith(cup_type):
#             base_name = base_name.replace(cup_type, replacement)
#             break

#     # Construct final folder name
#     return f"{base_name}{design_code}"

# # Function to process and save mockups for each PNG file in cups
# def process_and_save_cup_mockups(png_file, folder_path, mockup_folder_cups,input_folder_cup):
#     mockup_files = ["1.jpg", "2.jpg", "4.jpg", "5.jpg"]
#     png_source_path = os.path.join(input_folder_cup, png_file)

#     for mockup_file in mockup_files:
#         mockup_path = os.path.join(mockup_folder_cups, mockup_file)
#         if not os.path.exists(mockup_path):
#             logging.error(f"Mockup file not found: {mockup_path}")
#             continue
#         mockup_image = Image.open(mockup_path).convert("RGBA")
#         png_image = Image.open(png_source_path).convert("RGBA")

#         # Get rotation angle for the current mockup file
#         rotation_angle = cups_mockup_details.get(mockup_file, {}).get("rotation", 0)

#         # Process and save for each set of coordinates
#         for coord_set in cups_mockup_details.get(mockup_file, {}).get("coordinates", []):
#             png_resized = resize_and_center_cup_image(png_image, coord_set)

#             # Rotate PNG image if necessary
#             if rotation_angle:
#                 # Rotate clockwise by positive angle
#                 png_resized = png_resized.rotate(-rotation_angle, resample=Image.BICUBIC, expand=True)

#             # Paste the image centered within each bounding box
#             mockup_image = paste_cup_image_on_mockup(mockup_image, png_resized, coord_set)

#         # Save the combined image
#         mockup_image = mockup_image.convert("RGB")  # Convert back to RGB before saving as JPEG
#         mockup_image.save(os.path.join(folder_path, mockup_file), "JPEG")
#     shutil.copy(os.path.join(mockup_folder_cups,"3.jpg"), os.path.join(folder_path, "3.jpg"))

# # Function to resize and center the image within the bounding box for cups
# def resize_and_center_cup_image(image, coordinates):
#     # Calculate the bounding box dimensions
#     x_coords = [coord[0] for coord in coordinates]
#     y_coords = [coord[1] for coord in coordinates]
#     bbox_width = max(x_coords) - min(x_coords)
#     bbox_height = max(y_coords) - min(y_coords)

#     # Resize image to fit within the bounding box
#     image.thumbnail((bbox_width, bbox_height), Image.LANCZOS)
#     image = image.copy()

#     return image

# # Function to paste the image on the mockup at the specified coordinates for cups
# def paste_cup_image_on_mockup(mockup_image, png_image, coordinates):
#     # Calculate the position to center the image within the bounding box
#     x_coords = [coord[0] for coord in coordinates]
#     y_coords = [coord[1] for coord in coordinates]
#     center_x = (max(x_coords) + min(x_coords)) // 2
#     center_y = (max(y_coords) + min(y_coords)) // 2
#     position = (center_x - png_image.width // 2, center_y - png_image.height // 2)

#     # Paste the image onto the mockup with transparency
#     mockup_image.paste(png_image, position, png_image)

#     return mockup_image
# Pre-defined coordinates for each mockup image (multiple pastes) and rotation angles
cups_mockup_details = {
    "1.jpg": {
        "coordinates": [
            [(1888, 877), (2353, 1021), (2173, 1918), (1682, 1801)],  # Top image (unchanged)
            [(1568, 2230), (2067, 2337), (1880, 2866), (1537, 2772)]  # Bottom image (compressed)
        ],
        "rotation": 12
    },
    "2.jpg": {
        "coordinates": [
            [(1858, 897), (2374, 1051), (2133, 1948), (1652, 1831)],  # Top image (shifted left)
            [(1574, 2224), (2061, 2331), (1880, 2848), (1537, 2772)]  # Bottom image (compressed)
        ],
        "rotation": 13
    },
    "4.jpg": {
        "coordinates": [
            [(1504, 1020), (2277, 1092), (2126, 2350), (1374, 2257)]
        ],
        "rotation": 6
    },
    "5.jpg": {
        "coordinates": [
            [(1718, 2365), (3050, 2365), (3065, 3990), (1711, 3969)]
        ],
        "rotation": 0
    }
}

# Function to create a new folder name based on PNG file name for cups
def create_new_cup_folder_name(png_file, design_code):
    # Define replacements for cup types
    cup_types = {
        'T-Shirt': '40oz Tumbler Quencher, 16oz Libbey Cup, 11oz Mug - ',
        'Raglan Baseball Tee': '40oz Tumbler Quencher, 16oz Libbey Cup, 11oz Mug - ',
        'Tank Top': '40oz Tumbler Quencher, 16oz Libbey Cup, 11oz Mug - ',
        'V-Neck T-Shirt': '40oz Tumbler Quencher, 16oz Libbey Cup, 11oz Mug - '
    }

    # Extract base name without extension
    base_name = os.path.splitext(png_file)[0]

    # Identify and replace the last words with corresponding cup type
    for cup_type, replacement in cup_types.items():
        if base_name.endswith(cup_type):
            base_name = base_name.replace(cup_type, replacement)
            break

    # Construct final folder name
    return f"{base_name}{design_code}"
# Function to process and save mockups for each PNG file in cups
def process_and_save_cup_mockups(png_file, folder_path, mockup_folder_cups, input_folder_cup):
    mockup_files = ["1.jpg", "2.jpg", "4.jpg", "5.jpg"]
    png_source_path = os.path.join(input_folder_cup, png_file)

    for mockup_file in mockup_files:
        mockup_path = os.path.join(mockup_folder_cups, mockup_file)
        if not os.path.exists(mockup_path):
            logging.error(f"Mockup file not found: {mockup_path}")
            continue
        mockup_image = Image.open(mockup_path).convert("RGBA")
        png_image = Image.open(png_source_path).convert("RGBA")

        # Get rotation angle for the current mockup file
        rotation_angle = cups_mockup_details.get(mockup_file, {}).get("rotation", 0)

        # Process and save for each set of coordinates
        for coord_set in cups_mockup_details.get(mockup_file, {}).get("coordinates", []):
            png_resized = resize_and_center_cup_image(png_image, coord_set)

            # Rotate PNG image if necessary
            if rotation_angle:
                png_resized = png_resized.rotate(-rotation_angle, resample=Image.BICUBIC, expand=True)

            # Paste the image centered within each bounding box
            mockup_image = paste_cup_image_on_mockup(mockup_image, png_resized, coord_set)

        # Save the combined image
        mockup_image = mockup_image.convert("RGB")  # Convert back to RGB before saving as JPEG
        mockup_image.save(os.path.join(folder_path, mockup_file), "JPEG")
    
    # Copy the "3.jpg" mockup unchanged
    shutil.copy(os.path.join(mockup_folder_cups, "3.jpg"), os.path.join(folder_path, "3.jpg"))

# Function to resize and center the image within the bounding box for cups
def resize_and_center_cup_image(image, coordinates, scale_factor=1.0):
    # Calculate the bounding box dimensions
    x_coords = [coord[0] for coord in coordinates]
    y_coords = [coord[1] for coord in coordinates]
    bbox_width = max(x_coords) - min(x_coords)
    bbox_height = max(y_coords) - min(y_coords)

    # Resize image to fit within the bounding box, applying the scale factor
    image.thumbnail((int(bbox_width * scale_factor), int(bbox_height * scale_factor)), Image.LANCZOS)
    image = image.copy()

    return image

# Function to paste the image on the mockup at the specified coordinates for cups
def paste_cup_image_on_mockup(mockup_image, png_image, coordinates):
    # Calculate the position to center the image within the bounding box
    x_coords = [coord[0] for coord in coordinates]
    y_coords = [coord[1] for coord in coordinates]
    center_x = (max(x_coords) + min(x_coords)) // 2
    center_y = (max(y_coords) + min(y_coords)) // 2
    position = (center_x - png_image.width // 2, center_y - png_image.height // 2)

    # Paste the image onto the mockup with transparency
    mockup_image.paste(png_image, position, png_image)

    return mockup_image


#------Hat mockups------

# Pre-defined bounding_box for each mockup image (multiple pastes) and rotation angles
hats_mockup_details = {
    "1.jpg": [
        [(1084, 668), (1711, 719), (1695, 1161), (1050, 1128)]
    ],
    "2.jpg": [
        [(577, 916), (1053, 934), (1009, 1259), (536, 1234)],
        [(1589, 971), (2075, 982), (2068, 1288), (1576, 1285)]
    ]
}


# Function to create a new folder name based on PNG file name for hats
def create_new_hat_folder_name(png_file, design_code):
    # Define replacements for hat types
    hat_types = {
        'T-Shirt': 'Trucker Cap, Bucket Hat, Snapback, Beanie - ',
        'Raglan Baseball Tee': 'Trucker Cap, Bucket Hat, Snapback, Beanie - ',
        'Tank Top': 'Trucker Cap, Bucket Hat, Snapback, Beanie - ',
        'V-Neck T-Shirt': 'Trucker Cap, Bucket Hat, Snapback, Beanie - '
    }

    # Extract base name without extension
    base_name = os.path.splitext(png_file)[0]

    # Identify and replace the last words with corresponding hat type
    for hat_type, replacement in hat_types.items():
        if base_name.endswith(hat_type):
            base_name = base_name.replace(hat_type, replacement)
            break

    # Construct final folder name
    return f"{base_name}{design_code}"


# Function to process and save mockups for each PNG file in T-shirts
def process_and_save_hat_mockups(png_file, folder_path, mockup_folder_hats,input_folder_hat):
    mockup_files = ["1.jpg", "2.jpg"]
    png_source_path = os.path.join(input_folder_hat, png_file)

    for mockup_file in mockup_files:
        mockup_path = os.path.join(mockup_folder_hats, mockup_file)
        if not os.path.exists(mockup_path):
            logging.error(f"Mockup file not found: {mockup_path}")
            continue
        mockup_image = Image.open(mockup_path).convert("RGBA")
        png_image = Image.open(png_source_path).convert("RGBA")

        # Create a copy of the mockup image for each PNG file
        final_mockup_image = mockup_image.copy()

        # Process and paste for each set of bounding_box
        for coord_set in hats_mockup_details.get(mockup_file, []):
            png_resized = resize_and_center_hat_image(png_image, coord_set)
            final_mockup_image = paste_hat_image_on_mockup(final_mockup_image, png_resized, coord_set)

        # Save the combined image
        combined_image_path = os.path.join(folder_path, mockup_file)
        final_mockup_image.save(combined_image_path, "PNG")

    shutil.copy(os.path.join(mockup_folder_hats, "3.jpg"), os.path.join(folder_path, "3.jpg"))

# # Function to resize and center the image within the bounding box for T-shirts
def resize_and_center_hat_image(image, bounding_box):
    # Calculate the bounding box dimensions
    x_coords = [coord[0] for coord in bounding_box]
    y_coords = [coord[1] for coord in bounding_box]
    bbox_width = max(x_coords) - min(x_coords)
    bbox_height = max(y_coords) - min(y_coords)

    # Resize image to fit within the bounding box
    image.thumbnail((bbox_width, bbox_height), Image.LANCZOS)
    image = image.copy()

    return image


# Function to paste the image on the mockup at the specified bounding_box for hats
def paste_hat_image_on_mockup(mockup_image, png_image, bounding_box):
    # Calculate the position to center the image
    min_x = min(coord[0] for coord in bounding_box)
    min_y = min(coord[1] for coord in bounding_box)

    # Calculate the image size
    png_width, png_height = png_image.size

    # Calculate the bounding box width and height
    x_coords = [coord[0] for coord in bounding_box]
    y_coords = [coord[1] for coord in bounding_box]
    bbox_width = max(x_coords) - min(x_coords)
    bbox_height = max(y_coords) - min(y_coords)

    # Calculate position to center image
    position = (
        min_x + (bbox_width - png_width) // 2,
        min_y + (bbox_height - png_height) // 2
    )

    # Paste the resized PNG into the mockup image
    mockup_image.paste(png_image, position, png_image)
    return mockup_image



#--------Transfer mockups-------

# Pre-defined coordinates for each mockup image (multiple pastes with rotation angles)
transfer_mockup_coordinates = {
    "1.jpg": [
        # Adult Size - No Change
        {
            "coords": [
                (int(1398 - 40), int(530)),
                (int(2487 - 40), int(478)),
                (int(2523), int(1556)),
                (int(1461), int(1608))
            ],
            "rotation": 0  # No rotation needed
        },
        # Youth Size - No Change
        {
            "coords": [
                (int(442 + (1116 - 442) * 0.8), int(1067 + (923 - 1067) * 0.8 + 20)),
                (int(1116 + (1246 - 1116) * 0.8), int(923 + (1582 - 923) * 0.8 + 20)),
                (int(1246 + (604 - 1246) * 0.8), int(1582 + (1698 - 1582) * 0.8 + 20)),
                (int(604 + (442 - 604) * 0.8), int(1698 + (1067 - 1698) * 0.8 + 20))
            ],
            "rotation": 13  # Same angle
        },
        # Pocket Size - Reduced by 20%
        {
            "coords": [
                (int(958 + (1344 - 958) * 0.8), int(177 + (230 - 177) * 0.8)),
                (int(1344 + (1294 - 1344) * 0.8), int(230 + (614 - 230) * 0.8)),
                (int(1294 + (906 - 1294) * 0.8), int(614 + (566 - 614) * 0.8)),
                (int(906 + (958 - 906) * 0.8), int(566 + (177 - 566) * 0.8))
            ],
            "rotation": -12  # Slight pivot remains unchanged
        }
    ],
    "2.jpg": [
        # Youth Size - No Change
        {
            "coords": [
                (int(359), int(818)),
                (int(670), int(816)),
                (int(675), int(1179)),
                (int(363), int(1184))
            ],
            "rotation": 0
        },
        # Adult Size
        {"coords": [(1138, 544), (1558, 568), (1537+20, 1082+20), (1118 -20, 1054 -20)], "rotation": -3},  # No rotation  Adult size

        {
            "coords": [
                (int(2179), int(846)),
                (int(2349), int(836)),
                (int(2358), int(1033)),
                (int(2186), int(1040))
            ],
            "rotation": 5
        }
    ]
}

# Function to create a new folder name based on PNG file name for transfers
def create_new_transfer_folder_name(png_file, design_code):
    # Define replacements for transfer types
    transfer_types = {
        'T-Shirt': 'Dtf Transfer, Direct To Film, Screen - ',
        'Raglan Baseball Tee': 'Dtf Transfer, Direct To Film, Screen - ',
        'Tank Top': 'Dtf Transfer, Direct To Film, Screen - ',
        'V-Neck T-Shirt': 'Dtf Transfer, Direct To Film, Screen - '
    }

    # Extract base name without extension
    base_name = os.path.splitext(png_file)[0]

    # Identify and replace the last words with corresponding transfer type
    for transfer_type, replacement in transfer_types.items():
        if base_name.endswith(transfer_type):
            base_name = base_name.replace(transfer_type, replacement)
            break

    # Construct final folder name
    return f"{base_name}{design_code}"

# Function to process and save mockups for each PNG file
def process_and_save_transfer_mockups(png_file, folder_path, mockup_folder_transfer,input_folder_transfer):
    mockup_files = ["1.jpg", "2.jpg"]
    png_source_path = os.path.join(input_folder_transfer, png_file)

    for mockup_file in mockup_files:
        mockup_path = os.path.join(mockup_folder_transfer, mockup_file)
        if not os.path.exists(mockup_path):
            logging.error(f"Mockup file not found: {mockup_path}")
            continue
        mockup_image = Image.open(mockup_path).convert("RGBA")
        png_image = Image.open(png_source_path).convert("RGBA")

        # Create a copy of the mockup image for each PNG file
        final_mockup_image = mockup_image.copy()

        # Process and paste for each set of coordinates with rotation
        for item in transfer_mockup_coordinates.get(mockup_file, []):
            coord_set = item["coords"]
            rotation_angle = item["rotation"]
            png_resized = resize_and_center_image(png_image, coord_set, rotation_angle, mockup_file)
            final_mockup_image = paste_image_on_mockup(final_mockup_image, png_resized, coord_set)

        # Save the combined image in PNG format to preserve transparency
        combined_image_path = os.path.join(folder_path, mockup_file)
        final_mockup_image.save(combined_image_path, "PNG")


def resize_and_center_image(image, coordinates, rotation_angle, mockup_file):
    # Calculate the bounding box dimensions
    x_coords = [coord[0] for coord in coordinates]
    y_coords = [coord[1] for coord in coordinates]
    bbox_width = max(x_coords) - min(x_coords)
    bbox_height = max(y_coords) - min(y_coords)

    # Create a copy of the image to ensure the original image is unchanged
    image_copy = image.copy()

    # Resize image to fit within the bounding box
    image_copy.thumbnail((bbox_width, bbox_height), Image.LANCZOS)

    # For adult size in 2.jpg, append extra space at the bottom if the PNG is landscape
    if mockup_file == "2.jpg" and bbox_height > image_copy.size[1]:
        # Create a new image with extra space at the bottom
        new_image = Image.new("RGBA", (image_copy.size[0], bbox_height), (0, 0, 0, 0))
        new_image.paste(image_copy, (0, 0))  # Paste the resized image at the top
        image_copy = new_image  # Replace image_copy with the new image

    # Rotate the image if needed
    if rotation_angle != 0:
        image_copy = image_copy.rotate(rotation_angle, expand=True)

    return image_copy



# Function to paste the image on the mockup at the specified coordinates
def paste_image_on_mockup(mockup_image, png_image, coordinates):
    # Calculate the bounding box dimensions
    x_coords = [coord[0] for coord in coordinates]
    y_coords = [coord[1] for coord in coordinates]
    bbox_width = max(x_coords) - min(x_coords)
    bbox_height = max(y_coords) - min(y_coords)

    # Calculate the position to center the image
    min_x = min(x_coords)
    min_y = min(y_coords)
    png_width, png_height = png_image.size
    position = (
        min_x + (bbox_width - png_width) // 2,
        min_y + (bbox_height - png_height) // 2
    )

    # Paste the resized PNG into the mockup image
    mockup_image.paste(png_image, position, png_image)
    return mockup_image


class Mockups:
    def __init__(self, mockups_folder="Mockups") -> None:
        self._mockups_folder = mockups_folder
        
    @property
    def tshirt_mockups(self):
        return os.path.join(self._mockups_folder, "Clothing")
    
    @property
    def cup_mockups(self):
        return os.path.join(self._mockups_folder, "Cups") 
    
    @property
    def hat_mockups(self):
        return os.path.join(self._mockups_folder, "Hats")  
    
    @property
    def transfer_mockups(self):
        return os.path.join(self._mockups_folder, "Transfers") 
    
    @property
    def template_image_path(self):
        return os.path.join(os.path.join(self._mockups_folder, "Designs"), "1.jpg")  
    
    @property
    def highlight_image_path(self):
        return os.path.join(os.path.join(self._mockups_folder, "Designs"), "2.png")  
    

class MockupProcessor:
    def __init__(self):
        self.mockup_paths = Mockups()
    
    
    def process_folder(self, input_folder, output_folder, png_start_number):
        subfolders = [f.path for f in os.scandir(input_folder) if f.is_dir()]

        for subfolder in subfolders:
            logging.info("processing subfolder: " + subfolder)
            png_start_number = self.process_subfolder(subfolder, output_folder, png_start_number)
            
    def process_subfolder(self, subfolder, output_folder, png_start_number):
        subfolder_name = os.path.basename(subfolder)
        subfolder_output = os.path.join(output_folder, subfolder_name)
        
        # Create the same subfolder structure in the output directory
        os.makedirs(subfolder_output, exist_ok=True)
        create_output_folders(subfolder_output)
        
        # Path to PNG files inside the current subfolder
        png_folder = os.path.join(subfolder, "PNG")
        
        # Check if PNG folder exists
        if not os.path.exists(png_folder):
            logging.error(f"PNG folder not found in {subfolder}")
            return
        
        # CSV path for current subfolder
        csv_path = os.path.join(subfolder_output, f"{subfolder_name}.csv")
        
        # Process PNG files
        png_files = [f for f in os.listdir(png_folder) if f.lower().endswith('.png')]
        rows = []
        for index, png_file in enumerate(png_files):
            logging.info(f"processing PNG file: {png_file}")
            # copy and rename the png file
            design_code = png_start_number + index - 1
            png_source_path = os.path.join(png_folder, png_file)
            png_dest_path = os.path.join(subfolder_output, "RENAMED PNG", f"{design_code + 1}.png")
            shutil.copy(png_source_path, png_dest_path)
            
            rows.append({
            # **self.process_tshirt_mockup(design_code, png_file, png_folder, subfolder_output),
            **self.process_cup_mockup(design_code, png_file, png_folder, subfolder_output),
            # **self.process_hat_mockup(design_code, png_file, png_folder, subfolder_output),
            # **self.process_transfer_mockup(design_code, png_file, png_folder, subfolder_output),
            # **self.process_images_and_create_mockups(design_code, png_file, png_folder, subfolder_output)
            })
            
            
        logging.info(f"Processing completed for {subfolder_name}. CSV file saved at: {csv_path}")
        df = pd.DataFrame(rows)
        df.to_csv(csv_path, index=False)
        return png_start_number + len(png_files)
    
    def process_tshirt_mockup(self, index, png_file, png_folder, subfolder_output):
        
        design_code = f"{index + 1:05d}"
        new_folder_name = create_new_tshirt_folder_name(png_file, design_code)
        tshirt_mockup_folder = os.path.join(subfolder_output, "Tshirt Mockup")
        new_folder_path = os.path.join(tshirt_mockup_folder, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)

        # Generate tags using the PNG file name as the product title
        product_title = os.path.splitext(png_file)[0]
        product_type = "T-Shirt Sweatshirt Hoodie"
        tags = process_and_generate_tags(product_title, product_type)
        design_tags = ', '.join(tags)


        # Process and save mockups
        process_and_save_tshirt_mockups(png_file, new_folder_path, self.mockup_paths.tshirt_mockups, png_folder)

        # Copy PNG file to RENAMED PNG folder with new name
        renamed_png_folder = os.path.join(subfolder_output, "PNG")
        os.makedirs(renamed_png_folder, exist_ok=True)
        new_png_name = f"{new_folder_name}.png"
        new_png_path = os.path.join(renamed_png_folder, new_png_name)
        original_png_path = os.path.join(png_folder, png_file)
        shutil.copy(original_png_path, new_png_path)
        logging.info("processed tshirts mockups")
        return {
            "Tshirt Folder Path": new_folder_path,
            "Tshirt Title": new_folder_name,
            "Tshirt Tags": design_tags,
            "Tshirt Listing To Copy": ""
        }
        
    def process_cup_mockup(self, index, png_file, png_folder, subfolder_output):
        # Determine design code and new folder name
        design_code = f"{index + 1:05d}"
        new_folder_name = create_new_cup_folder_name(png_file, design_code)
        cup_mockup_folder = os.path.join(subfolder_output, "Cup Mockup")
        new_folder_path = os.path.join(cup_mockup_folder, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)

        # Generate tags using the PNG file name as the product title
        product_title = os.path.splitext(png_file)[0]
        product_type = "40oz Tumbler Cup"
        tags = process_and_generate_tags(product_title, product_type)
        design_tags = ', '.join(tags)

        # Process and save mockups
        process_and_save_cup_mockups(png_file, new_folder_path, self.mockup_paths.cup_mockups, png_folder)
        logging.info("processed cups mockups")
        return {
            "Cup Folder Path": new_folder_path,
            "Cup Title": new_folder_name,
            "Cup Tags": design_tags,
            "Cup Listing To Copy": ""
        }

    def process_hat_mockup(self, index, png_file, png_folder, subfolder_output):
        design_code = f"{index + 1:05d}"
        new_folder_name = create_new_hat_folder_name(png_file, design_code)
        hat_mockup_folder = os.path.join(subfolder_output, "Hat Mockup")
        new_folder_path = os.path.join(hat_mockup_folder, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)


        # Generate tags using the PNG file name as the product title
        product_title = os.path.splitext(png_file)[0]
        product_type = "Headwear Cap Trucker Snapback"
        tags = process_and_generate_tags(product_title, product_type)
        design_tags = ', '.join(tags)
        

        # Process and save mockups
        process_and_save_hat_mockups(png_file, new_folder_path, self.mockup_paths.hat_mockups, png_folder)
        logging.info("processed hats mockups")
        return {
            "Hat Folders Paths": new_folder_path,
            "Hat Title": new_folder_name,
            "Hat Tags": design_tags,
            "Hat Listing Copy": ""
        }


    def process_transfer_mockup(self, index, png_file, png_folder, subfolder_output):
        design_code = f"{index + 1:05d}"
        new_folder_name = create_new_transfer_folder_name(png_file, design_code)
        transfer_mockup_folder = os.path.join(subfolder_output, "Transfer Mockup")
        new_folder_path = os.path.join(transfer_mockup_folder, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)


        # Generate tags using the PNG file name as the product title
        product_title = os.path.splitext(png_file)[0]
        product_type = "Heat Tranfers DTF"
        tags = process_and_generate_tags(product_title, product_type)
        design_tags = ', '.join(tags)

        # Process and save mockups
        process_and_save_transfer_mockups(png_file, new_folder_path, self.mockup_paths.transfer_mockups, png_folder)
        logging.info("processed transfer mockups")
        return {
            "Transfer Folder Path": new_folder_path,
            "Transfer Title": new_folder_name,
            "Transfer Tags": design_tags,
            "Transfer Listing Copy": ""
        }
        
    # def process_images_and_create_mockups(self, input_folder, output_folder, template_image_path, highlight_image_path, csv_file_path, bounding_box):
    def process_images_and_create_mockups(self, index, png_file, png_folder, subfolder_output):

        def create_new_folder_name(png_file):
            clothing_types = {
                'T-Shirt': 'Png Bundle',
                'Raglan Baseball Tee': 'Png Bundle',
                'Tank Top': 'Png Bundle',
                'V-Neck T-Shirt': 'Png Bundle'
            }
            
            base_name = os.path.splitext(png_file)[0]
            for clothing_type, replacement in clothing_types.items():
                if clothing_type in base_name:
                    base_name = base_name.replace(clothing_type, f'{replacement}, Popular SVG Printable, Digital Download')
                    break
            return base_name

        def resize_image(image, max_width):
            width_percent = (max_width / float(image.size[0]))
            height = int((float(image.size[1]) * float(width_percent)))
            return image.resize((max_width, height), Image.LANCZOS)

        def trim_image(image):
            bbox = image.convert('RGBA').getbbox()
            if bbox:
                return image.crop(bbox)
            return image

        def apply_color_adjust(image):
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.25)
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.25)
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.25)
            return image

        def apply_halftone_effect(image, dot_size=10, transparency_ratio=0.5):
            draw = ImageDraw.Draw(image)
            adjusted_dot_size = int(dot_size * (1 + transparency_ratio))  # Adjust dot spacing for more transparency
            for i in range(0, image.size[0], adjusted_dot_size):
                for j in range(0, image.size[1], adjusted_dot_size):
                    draw.point((i, j), fill="black")
            return image
        def apply_invert(image):
            if image.mode == "RGBA":
                r, g, b, a = image.split()
                rgb_image = Image.merge("RGB", (r, g, b))
            else:
                rgb_image = image.convert("RGB")
            
            inverted_image = ImageOps.invert(rgb_image)
            
            if image.mode == "RGBA":
                r, g, b = inverted_image.split()
                inverted_image = Image.merge("RGBA", (r, g, b, a))
            
            return inverted_image

        def convert_image_to_svg(input_image_path, output_svg_path, scaling_factor=0.2, alpha_threshold=50):
            # Step 1: Resize the image
            image = Image.open(input_image_path)
            new_width = int(image.width * scaling_factor)
            new_height = int(image.height * scaling_factor)
            resized_image = image.resize((new_width, new_height), Image.LANCZOS)
            
            # Step 2: Prepare the image for tracing
            resized_image = resized_image.convert('RGBA')
            white_background = Image.new('RGBA', resized_image.size, (255, 255, 255, 255))
            image_with_white_bg = Image.alpha_composite(white_background, resized_image)
            image_rgb = image_with_white_bg.convert('RGB')
            
            # Step 3: Extract dominant colors
            used = colorgram.extract(image_rgb, 100)
            dominant_colors = np.array([color.rgb for color in used if color.proportion > 0.01])
            
            # Step 4: Prepare the image for tracing
            image_array = np.array(resized_image)
            rows, cols, _ = image_array.shape
            transparent_mask = image_array[:, :, 3] < alpha_threshold
            
            rgb_pixels = image_array[:, :, :3].reshape(-1, 3)
            alpha_channel = image_array[:, :, 3].reshape(-1, 1)
            closest_colors_indices = pairwise_distances_argmin(rgb_pixels, dominant_colors)
            closest_colors_indices[transparent_mask.flatten()] = len(dominant_colors)
            
            # Step 5: Create SVG output
            combined_svg_output = f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{cols}" height="{rows}">\n'
            
            for i, color in enumerate(dominant_colors):
                layer_pixels = np.full_like(rgb_pixels, fill_value=0)
                mask = (closest_colors_indices == i)
                layer_pixels[mask] = color
                
                layer_image = layer_pixels.reshape(rows, cols, 3)
                layer_pil_image = Image.fromarray(layer_image.astype('uint8'), 'RGB')
                bw_image = ImageOps.grayscale(layer_pil_image)
                bw_image = bw_image.point(lambda x: 0 if x == 0 else 255, '1')
                bitmap = potrace.Bitmap(np.array(bw_image))
                bitmap.invert()
                path = bitmap.trace()
                
                path_data = ""
                for curve in path:
                    path_data += "M {} {}".format(curve.start_point.x, curve.start_point.y)
                    for segment in curve.segments:
                        if segment.is_corner:
                            path_data += " L {} {}".format(segment.c.x, segment.c.y)
                        else:
                            path_data += " C {} {} {} {} {} {}".format(segment.c1.x, segment.c1.y,
                                                                    segment.c2.x, segment.c2.y,
                                                                    segment.end_point.x, segment.end_point.y)
                
                color_tuple = tuple(int(c) for c in color)
                combined_svg_output += f'<path d="{path_data}" fill="rgb{color_tuple}" fill-rule="nonzero" />\n'
            
            combined_svg_output += '</svg>'
            
            # Save the final SVG
            with open(output_svg_path, 'w') as f:
                f.write(combined_svg_output)
            
            logging.info(f"Final combined SVG file saved to: {output_svg_path}")

        def process_png(file_path, version, output_folder):
            try:
                if version == "V5-svg":
                    svg_save_path = os.path.join(output_folder, f"{version}.svg")
                    convert_image_to_svg(file_path, svg_save_path)
                    return svg_save_path

                image = Image.open(file_path).convert("RGBA")
                image = resize_image(image, 3000)
                image = trim_image(image)
                
                if version == "V1-ready":
                    pass
                elif version == "V2-colouradjust":
                    image = apply_color_adjust(image)
                elif version == "V3-halftone":
                    image = apply_halftone_effect(image)
                elif version == "V4-invert":
                    image = apply_invert(image)
                else:
                    return
                
                save_path = os.path.join(output_folder, f"{version}.png")
                image.save(save_path, "PNG", dpi=(300, 300))
                logging.info(f"Processed and saved {version} for {os.path.basename(file_path)} in {output_folder}")

                return save_path
            except Exception as e:
                logging.error(f"Error processing {file_path} for {version}: {e}")

        #PNG position and template shrink
        def paste_centered(base_image, overlay_image, bounding_box, padding_factor=0.05):
            (x1, y1), (x2, y2) = bounding_box
            box_width = x2 - x1
            box_height = y2 - y1

            # Add padding to the top and bottom
            padding = int(box_height * padding_factor)
            y1 += padding  # Move the top down by the padding amount
            y2 -= padding  # Move the bottom up by the padding amount

            overlay_width, overlay_height = overlay_image.size
            aspect_ratio = min(box_width / overlay_width, (y2 - y1) / overlay_height)
            new_size = (int(overlay_width * aspect_ratio), int(overlay_height * aspect_ratio))
            resized_overlay = overlay_image.resize(new_size, Image.LANCZOS)

            # Center the resized overlay within the adjusted bounding box
            paste_position = (x1 + (box_width - new_size[0]) // 2, y1 + (y2 - y1 - new_size[1]) // 2)
            base_image.paste(resized_overlay, paste_position, mask=resized_overlay)


        def create_mockup_images(template_image_path, highlight_image_path, design_mockup_folder):
            try:
                template_image = Image.open(template_image_path).convert("RGBA")
                highlight_image = Image.open(highlight_image_path).convert("RGBA")

                for version in ["V1-ready", "V2-colouradjust", "V3-halftone", "V4-invert", "V5-svg"]:
                    try:
                        effect_image_path = os.path.join(design_mockup_folder, f"{version}.png")
                        if os.path.exists(effect_image_path):
                            effect_image = Image.open(effect_image_path).convert("RGBA")

                            mockup_image = template_image.copy()
                            paste_centered(mockup_image, effect_image, template_bounding_box)
                            mockup_image.paste(highlight_image, (0, 0), mask=highlight_image)

                            mockup_path = os.path.join(design_mockup_folder, f"mock{version}.png")
                            mockup_image.save(mockup_path, "PNG", dpi=(300, 300))
                            logging.info(f"Created mockup image: {mockup_path}")
                        elif version == "V5-svg":
                            # No mockup creation for SVG, just ensure it's processed
                            svg_file_path = os.path.join(design_mockup_folder, f"{version}.svg")
                            if os.path.exists(svg_file_path):
                                logging.info(f"SVG file processed: {svg_file_path}")
                        else:
                            logging.error(f"Effect image {effect_image_path} not found.")
                    except Exception as e:
                        logging.error(f"Error creating mockup for {version}: {e}")
            except Exception as e:
                logging.error(f"Error creating mockups: {e}")

        png_file_path = os.path.join(png_folder, png_file)
        new_folder_name = create_new_folder_name(png_file)
        design_mockup_folder = os.path.join(subfolder_output, "Design Mockup")
        new_folder_path = os.path.join(design_mockup_folder, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)

        # Generate tags using the PNG file name as the product title
        product_title = os.path.splitext(png_file)[0]
        product_type = "PNG SVG"
        tags = process_and_generate_tags(product_title, product_type)
        design_tags = ', '.join(tags)

        try:
            for version in ["V1-ready", "V2-colouradjust", "V3-halftone", "V4-invert", "V5-svg"]:
                process_png(png_file_path, version, new_folder_path)
            
            create_mockup_images(self.mockup_paths.template_image_path, self.mockup_paths.highlight_image_path, new_folder_path)
            logging.info("processed design mockups")
            return {
                    "Design Folder Path": new_folder_path, 
                    "Design Title": new_folder_name, 
                    "Design Tags": design_tags, 
                    "Design Listing To Copy": ""
                }
        except Exception as e:
            logging.error(f"Error processing file {png_file}: {e}")
            return {}


class MockupProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mockup Processor")
        self.load_paths_from_config()
        self.csv_path = None
        root.geometry("550x250")
        self.worker_thread = None
        self.root.iconbitmap('logo.ico')

        # Input folder selection
        self.input_folder_label = tk.Label(root, text="Input Folder:")
        self.input_folder_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.input_folder_path = tk.StringVar()
        self.input_folder_entry = tk.Entry(root, textvariable=self.input_folder_path, width=50)
        self.input_folder_entry.grid(row=0, column=1, padx=0, pady=5)
        
        self.input_folder_button = tk.Button(root, width=10, text="Browse", command=self.select_input_folder)
        self.input_folder_button.grid(row=0, column=2, padx=0, pady=5)
        
        # Output folder selection
        self.output_folder_label = tk.Label(root, text="Output Folder:")
        self.output_folder_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.output_folder_path = tk.StringVar()
        self.output_folder_entry = tk.Entry(root, textvariable=self.output_folder_path, width=50)
        self.output_folder_entry.grid(row=1, column=1, padx=0, pady=5)
        
        self.output_folder_button = tk.Button(root, width=10, text="Browse", command=self.select_output_folder)
        self.output_folder_button.grid(row=1, column=2, padx=0, pady=5)
        
        # api_key input
        self.api_key_label = tk.Label(root, text="API KEY:")
        self.api_key_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.api_key_entry = tk.Entry(root, width=50)
        self.api_key_entry.grid(row=2, column=1, padx=0, pady=5)
        
        # PNG start number
        self.PNG_NO_label = tk.Label(root, text="PNG Start Number:")
        self.PNG_NO_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        def validate_integer_input(new_value):
            """Validate whether the new_value is an integer."""
            if new_value == "" or new_value.isdigit():
                return True
            return False
        
        vcmd = root.register(validate_integer_input)
        
        self.PNG_NO_entry = tk.Entry(root, width=50, validate="key", validatecommand=(vcmd, "%P"))
        self.PNG_NO_entry.grid(row=3, column=1, padx=0, pady=5)

        # Process button
        self.process_button = tk.Button(root, text="Start", width=42, command=self.handle_click)
        self.process_button.grid(row=4, column=1, padx=10, pady=20)
        
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=5, column=1, columnspan=1, padx=10, pady=5)


    def load_paths_from_config(self):
        config_file = "config.txt"
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                lines = f.readlines()
                for line in lines:
                    key, value = line.strip().split("=")
                    if key == "MOCKUP_FOLDER_CUPS":
                        self.mockup_folder_cups_path = value
                    elif key == "MOCKUP_FOLDER_HATS":
                        self.mockup_folder_hats_path = value
                    elif key == "MOCKUP_FOLDER_TRANSFER":
                        self.mockup_folder_transfer_path = value
                    elif key == "MOCKUP_FOLDER_TSHIRT":
                        self.mockup_folder_tshirt_path = value
                    elif key == "MOCKUP_FOLDER_TEMPLATE":
                        self.template_image_path = value
                    elif key == "MOCKUP_FOLDER_HIGHLIGHT":
                        self.highlight_image_path = value
        else:
            raise FileNotFoundError(f"Configuration file {config_file} not found.")
        
    def select_input_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.input_folder_path.set(folder_selected)

    def select_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder_path.set(folder_selected)

    # def select_template_image(self):
    #     file_selected = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png")])
    #     if file_selected:
    #         self.template_image_path.set(file_selected)

    # def select_highlight_image(self):
    #     file_selected = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png")])
    #     if file_selected:
    #         self.highlight_image_path.set(file_selected)
    
    def handle_click(self):
        """
        It creates a new worker if the initial worker is either done processing or 
        no worker is processing yet. it is inplace to handle multi-click mistakes
        """
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showerror('Task In Progress', 'Another task is already running')
            return
        self.worker_thread = threading.Thread(target=self.process_files, daemon=True)
        self.worker_thread.start()
    
    def process_files(self):
        # Get input values
        input_folder = self.input_folder_path.get()
        output_folder = self.output_folder_path.get()
        api_key = self.api_key_entry.get()
        png_start_number = int(self.PNG_NO_entry.get()) if self.PNG_NO_entry.get() else 1
        template_image_path = self.template_image_path
        highlight_image_path = self.highlight_image_path
        
        if not input_folder or not output_folder or not api_key or not png_start_number or not template_image_path or not highlight_image_path:
            messagebox.showerror("Input Error", "Please provide all inputs.")
            return

        # Initialize progress
        self.progress["value"] = 10
        # self.root.update_idletasks()

        try:
            logging.info("processing started")
            configure_api(api_key)
            logging.info("api configured")
            processor = MockupProcessor()
            processor.process_folder(input_folder, output_folder, png_start_number)

            messagebox.showinfo("Success", "Processing completed successfully.")
        except Exception as e:
            messagebox.showerror("Processing Error", str(e))

# Create and run the application
root = tk.Tk()
app = MockupProcessorApp(root)
root.mainloop()
