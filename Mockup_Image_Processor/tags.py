import google.generativeai as genai

# Initialize the Google AI Studio API key
API_KEY = "AIzaSyAmIuFevL08rSbm6T1ROHnRZHjQSSxQwTg"

# Configure the API with the key
genai.configure(api_key=API_KEY)

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
    

    
#Design tags
def process_images_and_create_mockups(input_folder, output_folder, template_image_path, highlight_image_path, csv_file_path, bounding_box):
#ye loop mai changing hai , or argument remove krna hai design tags
                for png_file in png_files:
                png_file_path = os.path.join(root, png_file)
                new_folder_name = create_new_folder_name(png_file)
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
                    
                    create_mockup_images(template_image_path, highlight_image_path, new_folder_path)
                    csv_data.append([new_folder_path, new_folder_name, design_tags, ""])
                except Exception as e:
                    logging.error(f"Error processing file {png_file}: {e}")
            
            update_csv(csv_file_path, csv_data)


#Tshirt design agy saro mai same change hai , argument remove krna design_tags ka function se or 4 lines add kr k design_tags ko refer krdena csv mai
def process_tshirt_mockups(input_folder_tshirt, output_folder_tshirt, mockup_folder_tshirt, csv_file_path):
#yeh add krna hai 4 lines or cv ka column me refer krdena design_tags and remove design_tags argument from function
          for index, png_file in enumerate(png_files):

                # Generate tags using the PNG file name as the product title
                product_title = os.path.splitext(png_file)[0]
                product_type = "PNG SVG"
                tags = process_and_generate_tags(product_title, product_type)
                design_tags = ', '.join(tags)

                # Process and save mockups
                process_and_save_tshirt_mockups(png_file, new_folder_path, mockup_folder_tshirt,input_folder_tshirt)


#cup mockups..
def process_cup_mockups(input_folder_cup, output_folder_cup, mockup_folder_cups, csv_file_path):
#same changings

    for index, png_file in enumerate(png_files):
        # Determine design code and new folder name
        design_code = f"{index + 1:05d}"
        new_folder_name = create_new_cup_folder_name(png_file, design_code)
        new_folder_path = os.path.join(cup_mockup_folder, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)

        # Generate tags using the PNG file name as the product title
        product_title = os.path.splitext(png_file)[0]
        product_type = "40oz Tumbler Cup"
        tags = process_and_generate_tags(product_title, product_type)
        design_tags = ', '.join(tags)

        # Process and save mockups
        process_and_save_cup_mockups(png_file, new_folder_path, mockup_folder_cups,input_folder_cup)

        # Update CSV with folder path, name, and design tags
        row_data = {
            # "Folder Path": new_folder_path,
            # "Folder Name": new_folder_name,
            # "Design Tags": design_tags,
            "Cup Folder Path": new_folder_path,
            "Cup Title": new_folder_name,
            "Cup Tags": design_tags, ##########yeh appending
            "Cup Listing To Copy": ""
        }
        row_data_list.append(row_data)
    df = pd.concat([df, pd.DataFrame(row_data_list)], axis=1)

    # Save DataFrame to CSV
    df.to_csv(csv_file_path, index=False)
    logging.info(f"Processing completed. CSV file saved at: {csv_file_path}")

#hat mockupss..
    png_files = [f for f in os.listdir(input_folder_hat) if f.lower().endswith('.png')]
    row_data_list = []
    for index, png_file in enumerate(png_files):
        # Determine design code and new folder name
        design_code = f"{index + 1:05d}"
        new_folder_name = create_new_hat_folder_name(png_file, design_code)
        new_folder_path = os.path.join(hat_mockup_folder, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)


        # Generate tags using the PNG file name as the product title
        product_title = os.path.splitext(png_file)[0]
        product_type = "Headwear Cap Trucker Snapback"
        tags = process_and_generate_tags(product_title, product_type)
        design_tags = ', '.join(tags)
        

        # Process and save mockups
        process_and_save_hat_mockups(png_file, new_folder_path, mockup_folder_hats,input_folder_hat)

        # Update CSV with folder path, name, and design tags
        row_data = {
            # "Folder Path": new_folder_path,
            # "Folder Name": new_folder_name,
            "Design Tags": design_tags,
            "Hat Folders Paths": new_folder_path,
            "Hat Title": new_folder_name,
            "Hat Tags": "",
            "Hat Listing Copy": ""
        }
        row_data_list.append(row_data)
        
    df = pd.concat([df, pd.DataFrame(row_data_list)], axis=1)

    # Save DataFrame to CSV
    df.to_csv(csv_file_path, index=False)
    logging.info(f"Processing completed. CSV file saved at: {csv_file_path}")


#transfer mockup
def process_transfer_mockups(input_folder_transfer, output_folder_transfer, mockup_folder_transfer, csv_file_path):
    # Process PNG files
    png_files = [f for f in os.listdir(input_folder_transfer) if f.lower().endswith('.png')]
    row_data_list = []
    for index, png_file in enumerate(png_files):
        # Determine design code and new folder name
        design_code = f"{index + 1:05d}"
        new_folder_name = create_new_transfer_folder_name(png_file, design_code)
        new_folder_path = os.path.join(transfer_mockup_folder, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)


        # Generate tags using the PNG file name as the product title
        product_title = os.path.splitext(png_file)[0]
        product_type = "Heat Tranfers DTF"
        tags = process_and_generate_tags(product_title, product_type)
        design_tags = ', '.join(tags)

        # Process and save mockups
        process_and_save_transfer_mockups(png_file, new_folder_path, mockup_folder_transfer,input_folder_transfer)

        # Update CSV with folder path, name, design tags, and transfer tags
        row_data = {
            "Transfer Folder path": new_folder_path,
            "Transfer Title": new_folder_name,
            "Transfer Tags": design_tags,
            "Transfer Listing Copy": ""
        }
        row_data_list.append(row_data)

    df = pd.concat([df, pd.DataFrame(row_data_list)], axis=1)
        
    # Save DataFrame to CSV
    df.to_csv(csv_file_path, index=False)
    logging.info(f"Processing completed. CSV file saved at: {csv_file_path}")
