import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2

class ImageEditorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Editor App")

        # Add a Load Image button
        self.load_button = tk.Button(master, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=10)

        # Label to display the image
        self.image_label = tk.Label(master)
        self.image_label.pack()

        # Store the loaded image
        self.cv_image = None
        self.tk_image = None

    def load_image(self):
        # Open file dialog to select an image
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            # Read the image using OpenCV
            self.cv_image = cv2.imread(file_path)
            # Convert from BGR (OpenCV format) to RGB
            cv_image_rgb = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2RGB)
            # Convert to PIL Image
            pil_image = Image.fromarray(cv_image_rgb)
            # Convert to ImageTk
            self.tk_image = ImageTk.PhotoImage(pil_image)
            # Display the image
            self.image_label.config(image=self.tk_image)

# Create the Tkinter window
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
