# google-images-scraper

This Python script allows you to download images from Google Images based on a search query.

## Prerequisites

Before running the script, make sure you have the following installed:

- Python 3.9.13
- geckodriver 

You can install the required Python packages using the following command:

```bash
pip install -r requirements.txt
```
Make sure to download the geckodriver executable and place it in the same directory as your script.

## Usage

Run the script from the command line with the following command:

```bash
python google_scraper.py "your_search_query" --max_images max_number --scroll_num scroll_count --folder_location path_to_folder
```
- **your_search_query:** The query for which you want to download images.
- **max_number:** Maximum number of images to download (default is 50).
- **scroll_count:** Number of times to scroll down on the search page (default is 1).
- **path_to_folder:** Location to store downloaded images (default is the current directory).

Example:
```bash
python google_scraper.py "Nike men sneaker" --max_images 80 --scroll_num 2 --folder_location ./downloads
```

## Notes

- The script uses Mozilla Firefox as the browser, so make sure to have it installed.
- The script may not work if the structure of the Google Images page changes.

