# Image Converter and Padder

This is a Python script that converts and pads the images in a specified directory to a common aspect ratio and compresses them to jpg format. It uses the Pillow library for image manipulation and the Tkinter library for creating a graphical user interface.

## Used Versions
- Python 3.10
- Pillow 10.0

## Usage

- Run the script using `python image_converter_and_padder.py`
- A window will appear with some options to configure the conversion process.
- Select the source directory where the images are located by clicking on the "Select source" button.
- Select the destination directory where the converted images will be saved by clicking on the "Select destination" button.
- Choose one of the common aspect ratios from the drop-down menu labeled "Aspect ratio".
- Enter the jpg quality in the range of 0 to 100 in the entry box labeled "Quality".
- Enter the padding color in hexadecimal format (e.g. "#FFFFFF" for white) in the entry box labeled "Color".
- Click on the "Convert" button to start the conversion process.
- A text box will show a message when the conversion process is completed.
- The script will convert and pad all the images in the source directory that have one of these extensions: ".jpg", ".tga", ".png", ".jpeg". 
- The script will copy any ".gif" files without modifying them.
- The script will save the converted images as ".jpg" files in the destination directory with the same file name as the original image.
- The script will use multithreading to speed up the conversion process. The maximum number of threads is set to 10 by default, but you can change it by modifying the `max_threads` variable in the code.
