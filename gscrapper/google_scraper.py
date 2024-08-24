from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import requests
import urllib.parse
import argparse
import os

def download_images(query, max_images, scroll_num, folder_location):

    options = Options()
    options.add_argument('--headless')  # Run in headless mode
    service = Service(executable_path='./chromedriver.exe')  # Ensure chromedriver is available
    driver = webdriver.Chrome(service=service, options=options)

    sleep_timer = 1

    driver.get('https://images.google.com/')

    search_box = driver.find_element(By.XPATH, '//*[@id="APjFqb"]')
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)

    for _ in range(scroll_num):
        driver.execute_script("window.scrollTo(1,100000)")
        print("Scroll Down")
        time.sleep(sleep_timer)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    images = soup.find_all("img", class_="rg_i Q4LuWd")
    time.sleep(2)

    # Create a folder to save the downloaded images with the query name
    folder_name = query.replace(' ', '_')  
    download_folder = os.path.join(folder_location, folder_name)
    
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    downloaded_images = 0
    image_number = 1  
    for index, image in enumerate(images):
        if downloaded_images >= max_images:
            break

        image_src = image.get('src') or image.get("data-src")
        if image_src and not image_src.startswith('data:'):
            # Check if the URL is relative and convert it to an absolute URL
            if not image_src.startswith('http'):
                base_url = driver.current_url
                image_src = urllib.parse.urljoin(base_url, image_src)

            # Get the image content using requests
            response = requests.get(image_src)
            if response.status_code == 200:
                # Rename and save the image to the folder
                image_filename = os.path.join(download_folder, f'image{image_number}.jpg')
                with open(image_filename, 'wb') as f:
                    f.write(response.content)
                downloaded_images += 1
                print(f"Image {downloaded_images} downloaded and saved as {image_filename}.")
                image_number += 1
            else:
                print(f"Failed to download image {index + 1}")
        else:
            #print(f"Image {index + 1} is a data URL and cannot be downloaded.")
            pass

    driver.close()
    
    print(f"Total pictures downloaded: {downloaded_images}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download images from Google Images")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--max_images", type=int, default=50, help="Maximum number of images to download")
    parser.add_argument("--scroll_num", type=int, default=1, help="Number of times to scroll down on the search page")
    parser.add_argument("--folder_location", type=str, default="./", help="Location to store downloaded images")
    args = parser.parse_args()

    download_images(args.query, args.max_images, args.scroll_num, args.folder_location)
