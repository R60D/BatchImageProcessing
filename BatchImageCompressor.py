import os
import glob
import multiprocessing
from multiprocessing import Pool
import shutil
import threading
from PIL import Image
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd 
from concurrent.futures import ThreadPoolExecutor
import pickle
import numpy as np
source_folder = os.path.dirname(os.path.abspath(__file__)) 
destination_folder = os.path.join(source_folder, "Converted") 

if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)
aspect_ratio = (16, 9) 
jpg_quality = 80 
padding_color = "#000000"
OriginalRatio = False
count = 0
maxcount = 0


# Define a function that takes an image format and a tuple of height and width
def resize_image(Image):
    try:
        convertedsize = tuple(map(int, resolution_var.get().split("x")))
    except:
        return Image
    # Open the image file with the given format
    # Resize the image to the given size
    return Image.resize(convertedsize)
    # Return the image object

def get_dir_size(dir_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(dir_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    # return the total size in megabytes
    return round(total_size / (1024 * 1024),1)

def pillow_function(image, green_value):
    # Load the image and get its size
    img = image
    width, height = img.size

    # Create a new image with the same size and mode as the original image
    new_img = Image.new(img.mode, (width, height))

    # Loop through the pixels of the original image
    for x in range(width):
        for y in range(height):
            # Get the RGB values of the pixel
            r, g, b = img.getpixel((x, y))

            # Set the green value to the specified value
            g = int(green_value*255)

            # Put the new RGB values in the new image
            new_img.putpixel((x, y), (r, g, b))

    # Return the new image
    return new_img

def convert_and_pad(file,destfolder):
    global count
    file_name, file_ext = os.path.splitext(file)
    if file_ext.lower() in [".jpg",".tga",".png",".jpeg"]:
        if file_ext.lower() == ".gif":
            shutil.copy(file, destination_folder)
        else:
            try:
                image = Image.open(file)
            except:
                print("corrupted image : " +file)
                return
            
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            width, height = image.size
            try:
                if not os.path.exists(destfolder):
                    os.makedirs(destfolder)
            except:
                1
            if not OriginalRatio:

                new_width = max(width, int(height * aspect_ratio[0] / aspect_ratio[1]))
                new_height = max(height, int(width * aspect_ratio[1] / aspect_ratio[0]))
            
                new_image = Image.new("RGB", (new_width, new_height), padding_color)
                
                new_image.paste(image, ((new_width - width) // 2, (new_height - height) // 2))
                if green_var.get():
                    new_image = pillow_function(resize_image(new_image),0.5)
                else:
                    new_image = resize_image(new_image)
            else:
                if green_var.get():
                    new_image = pillow_function(resize_image(image),0.5)
                else:
                    new_image = resize_image(image)
            new_image.save(destfolder + "/" + os.path.basename(file_name) + ".jpg", quality=jpg_quality)

            
            image.close()
        count += 1
        text_box.config(state="normal")
        text_box.delete(1.0, tk.END) 
        text_box.insert(tk.END, f"Converted {count}/{maxcount} files to {destination_folder}") 
        text_box.config(state="disabled")


def run_conversion():
    print(green_var.get())
    button.config(state=tk.DISABLED)
    
    
    global aspect_ratio
    global jpg_quality
    global padding_color
    global source_folder
    global destination_folder
    global OriginalRatio
    global count
    global maxcount
    maxcount = 0
    try:
        try:
            aspect_ratio = tuple(map(int, aspect_ratio_var.get().split(":")))
            OriginalRatio = False
        except:
            OriginalRatio = True

        
        jpg_quality = int(quality_var.get())
        
        padding_color = color_entry.get()
        if not padding_color.startswith("#"):
            padding_color = "#000000"
        
        source_folder = source_label["text"]
        destination_folder = destination_label["text"]
        if not os.path.isdir(source_folder):
            raise ValueError("Invalid source directory")
        if not os.path.isdir(destination_folder):
            raise ValueError("Invalid destination directory")
    except ValueError as e:
        text_box.config(state="normal")
        text_box.delete(1.0, tk.END) 
        text_box.insert(tk.END, f"Error: {e}") 
        text_box.config(state="disabled")
        
        button.config(state=tk.NORMAL)
        print("END")    
        return
    print("END")    
    # Loop through the source folder and its subfolders
    tasks = []
    count = 0
    chunk_size = 16
    for root, dirs, files in os.walk(source_folder):
        # Loop through the files in each folder
        for file in files:
            # Get the full path of the file
            file_path = os.path.join(root, file)
            # Get the destination path by replacing the source folder with the destination folder
            destination_path = root.replace(source_folder, destination_folder)
            tasks.append([file_path,destination_path])
            maxcount += 1

    print("END")        
    threadgroups = [tasks[i:i+chunk_size] for i in range(0, len(tasks), chunk_size)]   
    for workgroup in threadgroups:
        threads = []
        for task in workgroup:
            threads.append(threading.Thread(target=convert_and_pad, args=(task[0],task[1])))
        
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
    
    

    text_box.config(state="normal")
    text_box.delete(1.0, tk.END) 
    text_box.insert(tk.END, f"Converted {count} files. {get_dir_size(source_folder)}MB -> {get_dir_size(destination_folder)} MB ") 
    text_box.config(state="disabled")




    
    button.config(state=tk.NORMAL)


def select_source():
    
    directory = fd.askdirectory(title="Select source directory",initialdir=source_label["text"])
    
    if directory:
        source_label.config(text=directory)


def select_destination():
    
    directory = fd.askdirectory(title="Select destination directory",initialdir=destination_label["text"])
    
    if directory:
        destination_label.config(text=directory)





# Define a function to save the variables to a file
def save_variables():
    # Get the values of the variables
    source = source_label["text"]
    destination = destination_label["text"]
    aspect_ratio = aspect_ratio_var.get()
    resolution = resolution_var.get()
    quality = quality_var.get()
    color = color_entry.get()
    # Create a dictionary to store the variables
    variables = {"source": source, "destination": destination, "aspect_ratio": aspect_ratio, "resolution": resolution, "quality": quality, "color": color}
    # Open a file in write mode
    file = open("variables.pkl", "wb")
    # Use pickle to dump the variables to the file
    pickle.dump(variables, file)
    # Close the file
    file.close()
    # Show a message that the variables are saved
    text_box.config(state="normal")
    text_box.delete(1.0, "end")
    text_box.insert(1.0, "Variables saved successfully.")
    text_box.config(state="disabled")

# Define a function to load the variables from a file
def load_variables():
    # Use a try-except block to handle any errors
    try:
        # Open a file in read mode
        file = open("variables.pkl", "rb")
        # Use pickle to load the variables from the file
        variables = pickle.load(file)
        # Close the file
        file.close()
        # Set the values of the variables
        source_label["text"] = variables["source"]
        destination_label["text"] = variables["destination"]
        aspect_ratio_var.set(variables["aspect_ratio"])
        resolution_var.set(variables["resolution"])
        quality_var.set(variables["quality"])
        color_entry.delete(0, "end")
        color_entry.insert(0, variables["color"])
        text_box.config(state="normal")
        text_box.delete(1.0, "end")
        text_box.insert(1.0, "Variables loaded successfully.")
        text_box.config(state="disabled")
    except:
        # Show a message that the file is not found or corrupted
        text_box.config(state="normal")
        text_box.delete(1.0, "end")
        text_box.insert(1.0, "No file found or file corrupted. Please enter the variables manually.")
        text_box.config(state="disabled")

window = tk.Tk()

window.title("Batch jpg converter")


explanation_label = tk.Label(window,  justify="center", text="This script will convert and pad the images in the specified file directory to the specified aspect ratio and compress the files to jpg when possible.")

# Place the explanation label in row 0, column 0, and span 2 columns
explanation_label.grid(row=0, column=0, columnspan=2, pady=10)

source_label = tk.Label(window, text=source_folder)
source_button = tk.Button(window, text="Select source directory", command=select_source)
    
# Place the source label in row 1, column 0, and align it to the right
source_label.grid(row=1, column=0, sticky="E", pady=10)
# Place the source button in row 1, column 1
source_button.grid(row=1, column=1, pady=10)

destination_label = tk.Label(window, text=destination_folder)
destination_button = tk.Button(window, text="Select destination directory", command=select_destination)

# Place the destination label in row 2, column 0, and align it to the right
destination_label.grid(row=2, column=0, sticky="E", pady=10)
# Place the destination button in row 2, column 1
destination_button.grid(row=2, column=1, pady=10)

aspect_ratio_label = tk.Label(window, text="Select the aspect ratio (width:height):")
aspect_ratio_var = tk.StringVar(window)
aspect_ratio_var.set("Original") 
aspect_ratio_options = ["4:3", "16:9", "16:10", "21:9", "32:9","1:1", "Original"] 
aspect_ratio_menu = tk.OptionMenu(window, aspect_ratio_var, *aspect_ratio_options)

# Create a label for the resolution parameter
resolution_label = tk.Label(window, text="Select the image resolution (width x height):")
resolution_var = tk.StringVar(window)
resolution_var.set("Original")
resolution_options = ["Original","512x512", "1024x1024", "2048x2048", "4096x4096", "8192x8192"]
resolution_menu = ttk.Combobox(window, textvariable=resolution_var, values=resolution_options)
# Place the resolution label in row 4, column 0, and align it to the right
resolution_label.grid(row=4, column=0, sticky="E", pady=10)
# Place the resolution menu in row 4, column 1
resolution_menu.grid(row=4, column=1, pady=10)


# Place the aspect ratio label in row 3, column 0, and align it to the right
aspect_ratio_label.grid(row=3, column=0, sticky="E", pady=10)
# Place the aspect ratio menu in row 3, column 1
aspect_ratio_menu.grid(row=3, column=1, pady=10)


quality_label = tk.Label(window, text="Adjust the jpg quality (0-100):")
quality_var = tk.IntVar(window)
quality_var.set(80) 
quality_slider = tk.Scale(window, from_=0, to=100, orient=tk.HORIZONTAL, variable=quality_var)

# Place the quality label in row 4, column 0, and align it to the right
quality_label.grid(row=7, column=0, sticky="E", pady=10)
# Place the quality slider in row 4, column 1
quality_slider.grid(row=7, column=1,pady=10)

green_label = tk.Label(window, text="Set Green Channel to 0.5")
green_var = tk.BooleanVar(window)
green_var.set(80) 

green_button = tk.Checkbutton(window,variable=green_var)

# Place the quality label in row 4, column 0, and align it to the right
green_label.grid(row=9, column=0, sticky="E", pady=10)
# Place the quality slider in row 4, column 1
green_button.grid(row=9, column=1,pady=10)

color_label = tk.Label(window, text="Enter the hex value of the padding color:")
color_entry = tk.Entry(window)
color_entry.insert(0,"#000000")
color_label.grid(row=5,column=0,pady=10,padx=0,sticky="E")
color_entry.grid(row=5,column=1,pady=10,padx=0)
# Create a button that calls the run_conversion function
button = tk.Button(window,text="Run Conversion",command=lambda: threading.Thread(target=run_conversion).start())

# Place the button in row 6,column 0,and span 2 columns
button.grid(row=8,column=1,columnspan=3,pady=52)
text_box = tk.Text(window,width =60,height =3) #text box
text_box.config(state="disabled")
text_box.grid(row =8,column =0,columnspan =1,pady =52,sticky="E") #place text box

# Create a button to call the save_variables function
save_button = tk.Button(window, text="Save Variables", command=save_variables)
# Place the save button in row 9, column 0
save_button.grid(row=9, column=2, pady=10)
# Bind the Ctrl+S shortcut to the save_variables function
window.bind("<Control-s>", lambda event: save_variables())

# Create a button to call the load variables function
save_button = tk.Button(window, text="Load Variables", command=load_variables)
# Place the save button in row 9, column 0
save_button.grid(row=9, column=3, pady=10)
# Bind the Ctrl+S shortcut to the save_variables function
window.bind("<Control-r>", lambda event: load_variables())

# Call the load_variables function at the beginning of the script
load_variables()

window.mainloop()