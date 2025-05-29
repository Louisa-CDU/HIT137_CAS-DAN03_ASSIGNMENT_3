import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar, Canvas
from PIL import Image, ImageTk
import cv2
class CustomCanvas(Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class ImageEditorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Advanced Image Editor")
        self.master.geometry("1200x720")

        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)

        self.image_frame = tk.Frame(master)
        self.image_frame.pack(fill="both", expand=True)

        self.canvas = CustomCanvas(self.image_frame, bg="grey")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scroll_y = Scrollbar(self.image_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.cropped_frame = tk.Frame(master, bg="lightgrey")
        self.cropped_frame.pack(fill="x")

        self.cropped_label = tk.Label(self.cropped_frame, bg="lightgrey", text="Cropped image will appear here")
        self.cropped_label.pack(pady=10)

        self.resize_slider = tk.Scale(self.cropped_frame, from_=10, to=200, orient="horizontal",
                                      label="Resize %", command=self.resize_cropped_image)
        self.resize_slider.set(100)
        self.resize_slider.pack(pady=10)

        tk.Button(self.button_frame, text="Load Image", command=self.load_image).pack(side="left", padx=5)
        tk.Button(self.button_frame, text="Save Cropped Image (Ctrl+S)", command=self.save_cropped_image).pack(side="left", padx=5)
        tk.Button(self.button_frame, text="Undo (Ctrl+Z)", command=self.undo_crop).pack(side="left", padx=5)
        tk.Button(self.button_frame, text="Toggle Grayscale", command=self.toggle_grayscale).pack(side="left", padx=5)

        self.cv_image = None
        self.tk_image = None
        self.cropped_cv_image = None
        self.cropped_tk_image = None
        self.crop_history = []
        self.is_grayscale = False

        self.start_x = self.start_y = self.rect = None

        self.canvas.bind("<ButtonPress-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.do_crop)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)
        self.master.bind('<Control-s>', self.save_cropped_image_shortcut)
        self.master.bind('<Control-z>', self.undo_crop_shortcut)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if file_path:
            self.cv_image = cv2.imread(file_path)
            self.is_grayscale = False
            rgb_image = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2RGB)
            self.tk_image = ImageTk.PhotoImage(Image.fromarray(rgb_image))
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def start_crop(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def do_crop(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def end_crop(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        x1, y1 = int(min(self.start_x, end_x)), int(min(self.start_y, end_y))
        x2, y2 = int(max(self.start_x, end_x)), int(max(self.start_y, end_y))
        if self.cv_image is not None and x2 > x1 and y2 > y1:
            cropped = self.cv_image[y1:y2, x1:x2]
            if cropped.size > 0:
                if self.cropped_cv_image is not None:
                    self.crop_history.append(self.cropped_cv_image.copy())
                self.cropped_cv_image = cropped
                self.show_cropped_image()

    def resize_image(self, image, scale):
        width = int(image.shape[1] * scale / 100)
        height = int(image.shape[0] * scale / 100)
        return cv2.resize(image, (width, height))

    def show_cropped_image(self, scale=100):
        if self.cropped_cv_image is not None:
            resized = self.resize_image(self.cropped_cv_image, scale)
            display_image = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY if self.is_grayscale else cv2.COLOR_BGR2RGB)
            display_image = Image.fromarray(display_image)
            self.cropped_tk_image = ImageTk.PhotoImage(display_image)
            self.cropped_label.config(image=self.cropped_tk_image, text="")

    def resize_cropped_image(self, value):
        self.show_cropped_image(scale=int(value))

    def toggle_grayscale(self):
        self.is_grayscale = not self.is_grayscale
        self.show_cropped_image(scale=int(self.resize_slider.get()))

    def save_cropped_image(self):
        if self.cropped_cv_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            if file_path:
                scale = int(self.resize_slider.get())
                resized = self.resize_image(self.cropped_cv_image, scale)
                save_img = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY) if self.is_grayscale else resized
                cv2.imwrite(file_path, save_img)
                messagebox.showinfo("Saved", f"Image saved to {file_path}")

    def undo_crop(self):
        if self.crop_history:
            self.cropped_cv_image = self.crop_history.pop()
            self.show_cropped_image()
        else:
            self.cropped_label.config(image="", text="No previous crop to undo.")

    def save_cropped_image_shortcut(self, event):
        self.save_cropped_image()

    def undo_crop_shortcut(self, event):
        self.undo_crop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
