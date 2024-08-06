import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from io import BytesIO

# Directory to save the images
save_dir = "manga_images"

# Create the directory if it doesn't exist
os.makedirs(save_dir, exist_ok=True)

def download_image(img_url, save_path):
    try:
        response = requests.get(img_url)
        response.raise_for_status()  # Check for HTTP request errors
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {img_url} to {save_path}")
    except Exception as e:
        print(f"Failed to download {img_url}: {e}")

def download_images_from_chapter(chapter_url, chapter, base_url):
    try:
        response = requests.get(chapter_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all image tags
        img_tags = soup.find_all('img')
        for img_tag in img_tags:
            img_url = img_tag.get('src')
            if img_url and (img_url.endswith('.png') or img_url.endswith('.jpg')):
                # Create a full URL if the image URL is relative
                full_img_url = urljoin(base_url, img_url)
                img_name = os.path.basename(full_img_url)
                save_path = os.path.join(save_dir, f"chapter_{chapter}_{img_name}")
                download_image(full_img_url, save_path)
    except Exception as e:
        print(f"Failed to process chapter {chapter}: {e}")

def process_chapter(chapter, base_url):
    # Process the main chapter
    main_chapter_url = f"{base_url}{chapter}/"
    print(f'Crawling main chapter: {main_chapter_url}')
    download_images_from_chapter(main_chapter_url, chapter, base_url)
    
    # Process sub-chapters
    try:
        response = requests.get(main_chapter_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all sub-chapter links
        sub_chapter_links = soup.select(f'a[href*="{chapter}"]')
        sub_chapters = set()
        for link in sub_chapter_links:
            href = link.get('href')
            sub_chapter_number = href.split('/')[-2]  # extract sub-chapter number
            sub_chapters.add(sub_chapter_number)
        
        for sub_chapter in sub_chapters:
            if sub_chapter != str(chapter):  # skip the main chapter to avoid duplication
                sub_chapter_url = f"{base_url}{sub_chapter}/"
                print(f'Crawling sub-chapter: {sub_chapter_url}')
                download_images_from_chapter(sub_chapter_url, sub_chapter, base_url)
    except Exception as e:
        print(f"Failed to process chapter {chapter}: {e}")

def start_download():
    try:
        base_url = base_url_entry.get()
        start_chapter = int(start_chapter_entry.get())
        end_chapter = int(end_chapter_entry.get())
        for chapter in range(start_chapter, end_chapter + 1):
            process_chapter(chapter, base_url)
        messagebox.showinfo("Done", "Download completed!")
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid chapter numbers.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def display_cover_image():
    try:
        base_url = base_url_entry.get()
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tag = soup.find('div', class_='summary_image').find('img')
        if img_tag:
            img_url = img_tag['src']
            full_img_url = urljoin(base_url, img_url)
            response = requests.get(full_img_url)
            response.raise_for_status()
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((200, 300), Image.ANTIALIAS)
            img_tk = ImageTk.PhotoImage(img)
            cover_image_label.config(image=img_tk)
            cover_image_label.image = img_tk
        else:
            messagebox.showerror("Error", "Cover image not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Create the main window
root = tk.Tk()
root.title("Manga Downloader")

# Create and place the labels and entry fields
tk.Label(root, text="Base URL:").grid(row=0, column=0, padx=10, pady=10)
base_url_entry = tk.Entry(root, width=50)
base_url_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Start Chapter:").grid(row=1, column=0, padx=10, pady=10)
start_chapter_entry = tk.Entry(root)
start_chapter_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="End Chapter:").grid(row=2, column=0, padx=10, pady=10)
end_chapter_entry = tk.Entry(root)
end_chapter_entry.grid(row=2, column=1, padx=10, pady=10)

# Create and place the download button
download_button = tk.Button(root, text="Start Download", command=start_download)
download_button.grid(row=3, column=0, columnspan=2, pady=20)

# Create and place the cover image display button
cover_image_button = tk.Button(root, text="Show Cover Image", command=display_cover_image)
cover_image_button.grid(row=4, column=0, columnspan=2, pady=10)

# Create and place the label for the cover image
cover_image_label = tk.Label(root)
cover_image_label.grid(row=5, column=0, columnspan=2, pady=10)

# Run the main loop
root.mainloop()
