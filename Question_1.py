import subprocess
import sys

# Try importing and install if missing
def install_and_import(package_name, import_name=None):
    try:
        if import_name is None:
            import_name = package_name
        __import__(import_name)
    except ImportError:
        print(f"Package '{package_name}' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"'{package_name}' installed. Restarting script...")
        __import__(import_name)

# Attempt to import/install required packages
install_and_import("opencv-python", "cv2")
install_and_import("pillow", "PIL")
import cv2
from PIL import Image, ImageTk

class CustomCanvas(Canvas):
    """Subclass of Canvas to demonstrate inheritance."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class ImageEditorApp:
    """Main application class handling image editing operations."""
    def __init__(self, master):
        self.master = master
        self.master.title("Image Editor App")
        self.master.geometry("1200x720")

        # Button Frame
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)

        self.load_button = tk.Button(self.button_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.button_frame, text="Save Cropped Image (Ctrl+S)", command=self.save_cropped_image)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.undo_button = tk.Button(self.button_frame, text="Undo (Ctrl+Z)", command=self.undo_crop)
        self.undo_button.pack(side=tk.LEFT, padx=5)

        self.toggle_gray_button = tk.Button(self.button_frame, text="Toggle Grayscale", command=self.toggle_grayscale)
        self.toggle_gray_button.pack(side=tk.LEFT, padx=5)

        # Image Display Frame
        self.image_frame = tk.Frame(master)
        self.image_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = CustomCanvas(self.image_frame, bg="grey")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.cropped_frame = tk.Frame(self.image_frame, bg="lightgrey")
        self.cropped_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.cropped_label = tk.Label(self.cropped_frame, bg="lightgrey", text="Cropped image will appear here")
        self.cropped_label.pack(pady=10)

        self.resize_slider = tk.Scale(self.cropped_frame, from_=10, to=200, orient=tk.HORIZONTAL,
                                      label="Resize %", command=self.resize_cropped_image)
        self.resize_slider.set(100)
        self.resize_slider.pack(pady=10)

        self.scroll_y = Scrollbar(self.image_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.cv_image = None
        self.tk_image = None
        self.cropped_cv_image = None
        self.cropped_tk_image = None
        self.is_grayscale = False

        # For cropping
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.crop_history = []

        # Event bindings
        self.canvas.bind("<ButtonPress-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.do_crop)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)
        self.master.bind('<Control-s>', self.save_cropped_image_shortcut)
        self.master.bind('<Control-z>', self.undo_crop_shortcut)

    def load_image(self):
        """Load an image from file and display it on the canvas."""
        try:
            file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif")])
            if file_path:
                self.cv_image = cv2.imread(file_path)
                self.is_grayscale = False
                rgb_image = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2RGB)
                self.tk_image = ImageTk.PhotoImage(Image.fromarray(rgb_image))
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
                self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load image:\n{e}")

    def start_crop(self, event):
        """Begin a cropping rectangle on mouse press."""
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def do_crop(self, event):
        """Update the cropping rectangle as the mouse moves."""
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def end_crop(self, event):
        """Complete the crop and show the cropped image."""
        try:
            end_x = self.canvas.canvasx(event.x)
            end_y = self.canvas.canvasy(event.y)
            x1, y1 = int(min(self.start_x, end_x)), int(min(self.start_y, end_y))
            x2, y2 = int(max(self.start_x, end_x)), int(max(self.start_y, end_y))

            if self.cv_image is not None:
                cropped = self.cv_image[y1:y2, x1:x2]
                if cropped.size > 0:
                    if self.cropped_cv_image is not None:
                        self.crop_history.append(self.cropped_cv_image.copy())
                    self.cropped_cv_image = cropped
                    self.show_cropped_image()
        except Exception as e:
            messagebox.showerror("Crop Error", f"Could not crop image:\n{e}")

    def resize_image(self, image, scale):
        """Resize a given image to the specified scale percentage."""
        width = int(image.shape[1] * scale / 100)
        height = int(image.shape[0] * scale / 100)
        return cv2.resize(image, (width, height))

    def show_cropped_image(self, scale=100):
        """Display the cropped image at a specified scale, applying grayscale if toggled."""
        if self.cropped_cv_image is not None:
            resized = self.resize_image(self.cropped_cv_image, scale)
            if self.is_grayscale:
                gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                display_image = Image.fromarray(gray)
            else:
                rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                display_image = Image.fromarray(rgb)
            self.cropped_tk_image = ImageTk.PhotoImage(display_image)
            self.cropped_label.config(image=self.cropped_tk_image, text="")

    def resize_cropped_image(self, value):
        """Resize image when slider is adjusted."""
        self.show_cropped_image(scale=int(value))

    def toggle_grayscale(self):
        """Toggle grayscale preview for the cropped image."""
        self.is_grayscale = not self.is_grayscale
        self.show_cropped_image(scale=int(self.resize_slider.get()))

    def save_cropped_image(self):
        """Save the cropped image (resized and current mode) to file."""
        if self.cropped_cv_image is not None:
            try:
                file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                         filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
                if file_path:
                    scale = int(self.resize_slider.get())
                    resized = self.resize_image(self.cropped_cv_image, scale)
                    if self.is_grayscale:
                        resized = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                    cv2.imwrite(file_path, resized)
                    print(f"Image saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save image:\n{e}")

    def undo_crop(self):
        """Revert to the previous cropped image, if available."""
        if self.crop_history:
            self.cropped_cv_image = self.crop_history.pop()
            self.show_cropped_image()
        else:
            self.cropped_label.config(image="", text="No previous crop to undo.")

    def save_cropped_image_shortcut(self, event):
        """Keyboard shortcut for saving cropped image."""
        self.save_cropped_image()

    def undo_crop_shortcut(self, event):
        """Keyboard shortcut for undoing the crop."""
        self.undo_crop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
