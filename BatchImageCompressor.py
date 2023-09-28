import os
import glob
import shutil
import threading
from PIL import Image, ImageOps
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd 

source_folder = os.path.dirname(os.path.abspath(__file__)) 
destination_folder = os.path.join(source_folder, "Converted") 

if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)
aspect_ratio = (16, 9) 
jpg_quality = 80 
padding_color = "#000000"

def convert_and_pad(file):
    file_name, file_ext = os.path.splitext(file)
    if file_ext.lower() in [".jpg",".png","jpeg"]:
        if file_ext.lower() == ".gif":
            shutil.copy(file, destination_folder)
        
        else:
            image = Image.open(file)
            
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            width, height = image.size
            
            new_width = max(width, int(height * aspect_ratio[0] / aspect_ratio[1]))
            new_height = max(height, int(width * aspect_ratio[1] / aspect_ratio[0]))
            
            new_image = Image.new("RGB", (new_width, new_height), padding_color)
            
            new_image.paste(image, ((new_width - width) // 2, (new_height - height) // 2))
            
            
            if file_ext.lower() == ".png":
                new_image.save(destination_folder + "/" + os.path.basename(file_name) + ".jpg", quality=jpg_quality)
            else:
                new_image.save(destination_folder + "/" + os.path.basename(file_name) + file_ext)
            
            image.close()


max_threads = 10 
semaphore = threading.Semaphore(max_threads)


def run_conversion():
    
    button.config(state=tk.DISABLED)
    
    count = 0
    
    global aspect_ratio
    global jpg_quality
    global padding_color
    global source_folder
    global destination_folder
    try:
        
        aspect_ratio = tuple(map(int, aspect_ratio_var.get().split(":")))
        
        jpg_quality = int(quality_var.get())
        
        padding_color = color_entry.get()
        if not padding_color.startswith("#"):
            raise ValueError("Invalid hex color")
        
        source_folder = source_label["text"]
        destination_folder = destination_label["text"]
        if not os.path.isdir(source_folder):
            raise ValueError("Invalid source directory")
        if not os.path.isdir(destination_folder):
            raise ValueError("Invalid destination directory")
    except ValueError as e:
        
        text_box.delete(1.0, tk.END) 
        text_box.insert(tk.END, f"Error: {e}") 
        
        button.config(state=tk.NORMAL)
        return
    
    for file in glob.glob(source_folder + "/*.*"):
        
        thread = threading.Thread(target=convert_and_pad, args=(file,))
        
        with semaphore:
            thread.start()
            
            count += 1
    
    thread.join()
    
    text_box.delete(1.0, tk.END) 
    text_box.insert(tk.END, f"Converted {count} files to {destination_folder}") 
    
    button.config(state=tk.NORMAL)


def select_source():
    
    directory = fd.askdirectory(title="Select source directory")
    
    if directory:
        source_label.config(text=directory)


def select_destination():
    
    directory = fd.askdirectory(title="Select destination directory")
    
    if directory:
        destination_label.config(text=directory)


window = tk.Tk()

window.title("Image Converter and Padder")

window.geometry("800x600")
window.minsize(800, 600)
window.maxsize(800, 600)

explanation_label = tk.Label(window, text="This script will convert and pad the images in the specified file directory to the specified aspect ratio and compress the files to jpg when possible.")

explanation_label.pack(pady=10)

source_label = tk.Label(window, text=source_folder)
source_button = tk.Button(window, text="Select source directory", command=select_source)

source_label.pack(pady=10)
source_button.pack(pady=10)

destination_label = tk.Label(window, text=destination_folder)
destination_button = tk.Button(window, text="Select destination directory", command=select_destination)

destination_label.pack(pady=10)
destination_button.pack(pady=10)

aspect_ratio_label = tk.Label(window, text="Select the aspect ratio (width:height):")
aspect_ratio_var = tk.StringVar(window)
aspect_ratio_var.set("16:9") 
aspect_ratio_options = ["4:3", "16:9", "16:10", "21:9", "32:9"] 
aspect_ratio_menu = tk.OptionMenu(window, aspect_ratio_var, *aspect_ratio_options)

aspect_ratio_label.pack(pady=10)
aspect_ratio_menu.pack(pady=10)

quality_label = tk.Label(window, text="Adjust the jpg quality (0-100):")
quality_var = tk.IntVar(window)
quality_var.set(80) 
quality_slider = tk.Scale(window, from_=0, to=100, orient=tk.HORIZONTAL, variable=quality_var)

quality_label.pack(pady=10)
quality_slider.pack(pady=10)

color_label = tk.Label(window, text="Enter the hex value of the padding color:")
color_entry = tk.Entry(window)
color_entry.insert(0, "#000000")
color_label.pack(pady=10)
color_entry.pack(pady=10)
# Create a button that calls the run_conversion function
button = tk.Button(window, text="Run Conversion", command=run_conversion)

button.pack(pady=10)
text_box = tk.Text(window, wrap=tk.WORD) 
text_box.pack(pady=10)
window.mainloop()