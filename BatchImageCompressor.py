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
            scale = float(size_ratio_var.get())
            if not OriginalRatio:

                new_width = max(width, int(height * aspect_ratio[0] / aspect_ratio[1]))
                new_height = max(height, int(width * aspect_ratio[1] / aspect_ratio[0]))
            
                new_image = Image.new("RGB", (new_width, new_height), padding_color)
                
                new_image.paste(image, ((new_width - width) // 2, (new_height - height) // 2))
                resizedimage = new_image.resize((round(scale*new_image.width),round(scale*new_image.height)),resample=Image.LANCZOS)
                resizedimage.save(destfolder + "/" + os.path.basename(file_name) + ".jpg", quality=jpg_quality)
            else:
                
                resizedimage = image.resize((round(scale*image.width),round(scale*image.height)),resample=Image.LANCZOS)
                resizedimage.save(destfolder + "/" + os.path.basename(file_name) + ".jpg", quality=jpg_quality)

            
            image.close()
        count += 1
        text_box.config(state="normal")
        text_box.delete(1.0, tk.END) 
        text_box.insert(tk.END, f"Converted {count}/{maxcount} files to {destination_folder}") 
        text_box.config(state="disabled")


def run_conversion():
    
    button.config(state=tk.DISABLED)
    
    
    global aspect_ratio
    global jpg_quality
    global padding_color
    global source_folder
    global destination_folder
    global OriginalRatio
    global count
    global maxcount
    try:
        try:
            aspect_ratio = tuple(map(int, aspect_ratio_var.get().split(":")))
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
        
        text_box.delete(1.0, tk.END) 
        text_box.insert(tk.END, f"Error: {e}") 
        
        button.config(state=tk.NORMAL)
        return
    
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

            
    threadgroups = [tasks[i:i+chunk_size] for i in range(0, len(tasks), chunk_size)]   
    for workgroup in threadgroups:
        threads = []
        for task in workgroup:
            threads.append(threading.Thread(target=convert_and_pad, args=(task[0],task[1])))
        
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()




    
    button.config(state=tk.NORMAL)


def select_source():
    
    directory = fd.askdirectory(title="Select source directory",initialdir=source_label["text"])
    
    if directory:
        source_label.config(text=directory)


def select_destination():
    
    directory = fd.askdirectory(title="Select destination directory",initialdir=destination_label["text"])
    
    if directory:
        destination_label.config(text=directory)



window = tk.Tk()

window.title("Image Converter and Padder")


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
aspect_ratio_var.set("16:9") 
aspect_ratio_options = ["4:3", "16:9", "16:10", "21:9", "32:9","1:1", "Original:Original"] 
aspect_ratio_menu = tk.OptionMenu(window, aspect_ratio_var, *aspect_ratio_options)

size_ratio_label = tk.Label(window, text="Select Image size ratio")
size_ratio_var = tk.StringVar(window)
size_ratio_var.set("1.0") 
size_ratio_options = ["1.0", "0.5", "0.25"] 
size_ratio_menu = tk.OptionMenu(window, size_ratio_var, *size_ratio_options)

# Place the aspect ratio label in row 3, column 0, and align it to the right
aspect_ratio_label.grid(row=3, column=0, sticky="E", pady=10)
# Place the aspect ratio menu in row 3, column 1
aspect_ratio_menu.grid(row=3, column=1, pady=10)

size_ratio_label.grid(row=6, column=0, sticky="E", pady=10)
size_ratio_menu.grid(row=6, column=1, pady=10)

quality_label = tk.Label(window, text="Adjust the jpg quality (0-100):")
quality_var = tk.IntVar(window)
quality_var.set(80) 
quality_slider = tk.Scale(window, from_=0, to=100, orient=tk.HORIZONTAL, variable=quality_var)

# Place the quality label in row 4, column 0, and align it to the right
quality_label.grid(row=4, column=0, sticky="E", pady=10)
# Place the quality slider in row 4, column 1
quality_slider.grid(row=4, column=1,pady=10)

color_label = tk.Label(window, text="Enter the hex value of the padding color:")
color_entry = tk.Entry(window)
color_entry.insert(0,"#000000")
color_label.grid(row=5,column=0,pady=10,padx=0,sticky="E")
color_entry.grid(row=5,column=1,pady=10,padx=0)
# Create a button that calls the run_conversion function
button = tk.Button(window,text="Run Conversion",command=lambda: threading.Thread(target=run_conversion).start())

# Place the button in row 6,column 0,and span 2 columns
button.grid(row=7,column=1,columnspan=3,pady=52)
text_box = tk.Text(window,width =60,height =3) #text box
text_box.config(state="disabled")
text_box.grid(row =7,column =0,columnspan =1,pady =52,sticky="E") #place text box


window.mainloop()
