import tkinter as tk
from tkinter import filedialog, Scrollbar, Canvas

try:
    import cv2
    from PIL import Image, ImageTk
except ImportError as e:
    print("Required packages not found. Please install opencv-python and pillow.")
    print("You can install them by running: pip install opencv-python pillow")
    raise e


class ImageEditorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Editor App")
        self.master.geometry("800x600")  # Set a decent window size

        # Frame for the buttons
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)

        self.load_button = tk.Button(self.button_frame, text="Load Image", command=self.load_image)
        self.load_button.pack()

        # Frame for the image display
        self.image_frame = tk.Frame(master)
        self.image_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas to display the image
        self.canvas = Canvas(self.image_frame, bg="grey")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar for big images
        self.scroll_y = Scrollbar(self.image_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        # Store the loaded image
        self.cv_image = None
        self.tk_image = None

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            # Read the image using OpenCV
            self.cv_image = cv2.imread(file_path)
            # Convert from BGR to RGB
            cv_image_rgb = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2RGB)
            # Convert to PIL Image
            pil_image = Image.fromarray(cv_image_rgb)
            # Convert to ImageTk
            self.tk_image = ImageTk.PhotoImage(pil_image)

            # Clear previous image
            self.canvas.delete("all")

            # Display the image in the centre
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

            # Configure the scroll region
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

# Create the Tkinter window
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
