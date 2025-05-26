import tkinter as tk
from tkinter import filedialog, Scrollbar, Canvas, messagebox
from PIL import Image, ImageTk
import subprocess
import sys
import cv2

class CustomCanvas(Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class ImageEditorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Editor App")
        self.master.configure(bg="#D9F2D0")
        self.master.geometry("1200x820")

        self.instructions_frame = tk.Frame(master, bg="yellow")
        self.instructions_frame.pack(fill=tk.X, pady=5, padx=10)

        self.instructions = tk.Label(self.instructions_frame,
            text="📌 Load an image. Click and drag to crop. Use the slider to resize. Use Grayscale, Undo, Redo, Restart or Save.",
            bg="yellow", fg="black", font=("Segoe UI Emoji", 11, "bold"), anchor="w", padx=10)
        self.instructions.pack(fill=tk.X)

        self.button_frame = tk.Frame(master, bg="#D9F2D0")
        self.button_frame.pack(pady=5)

        btn_cfg = dict(font=("Arial", 10), bg="#00B050", fg="white", activebackground="#009444", activeforeground="white")
        self.load_button = tk.Button(self.button_frame, text="Load Image", command=self.load_image, **btn_cfg)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.button_frame, text="Save (Ctrl+S)", command=self.save_cropped_image, **btn_cfg)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.undo_button = tk.Button(self.button_frame, text="Undo (Ctrl+Z)", command=self.undo_crop, **btn_cfg)
        self.undo_button.pack(side=tk.LEFT, padx=5)

        self.redo_button = tk.Button(self.button_frame, text="Redo (Ctrl+Y)", command=self.redo_crop, **btn_cfg)
        self.redo_button.pack(side=tk.LEFT, padx=5)

        self.grayscale_button = tk.Button(self.button_frame, text="Grayscale (Ctrl+G)", command=self.toggle_grayscale, **btn_cfg)
        self.grayscale_button.pack(side=tk.LEFT, padx=5)

        self.restart_button = tk.Button(self.button_frame, text="Restart (Ctrl+R)", command=self.restart_to_original, **btn_cfg)
        self.restart_button.pack(side=tk.LEFT, padx=5)

        self.slider_frame = tk.Frame(master, bg="#D9F2D0")
        self.slider_frame.pack(pady=5)

        self.slider_label = tk.Label(self.slider_frame, text="Resize to %:", font=("Arial", 10), bg="#D9F2D0")
        self.slider_label.pack(side=tk.LEFT)

        self.resize_slider = tk.Scale(self.slider_frame, from_=10, to=500, orient=tk.HORIZONTAL,
                                      command=self.apply_resize, bg="#e6e6e6", length=300)
        self.resize_slider.set(100)
        self.resize_slider.pack(side=tk.LEFT)

        self.image_frame = tk.Frame(master)
        self.image_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = CustomCanvas(self.image_frame, bg="#d9d9d9")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.cropped_frame = tk.Frame(self.image_frame, bg="#f0f0f0")
        self.cropped_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.cropped_label = tk.Label(self.cropped_frame, bg="#f0f0f0", text="Cropped image will appear here", font=("Arial", 10))
        self.cropped_label.pack(pady=10)

        self.scroll_y = Scrollbar(self.image_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.reset_state()

        self.canvas.bind("<ButtonPress-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.do_crop)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)

        self.master.bind('<Control-s>', self.save_cropped_image)
        self.master.bind('<Control-z>', self.undo_crop)
        self.master.bind('<Control-y>', self.redo_crop)
        self.master.bind('<Control-g>', self.toggle_grayscale)
        self.master.bind('<Control-r>', self.restart_to_original)
        self.master.bind('<Control-l>', self.load_image)

    def reset_state(self):
        self.cv_image = None
        self.tk_image = None
        self.original_image = None
        self.display_scale = 1.0
        self.cropped_cv_image = None
        self.cropped_tk_image = None
        self.display_image = None
        self.is_grayscale = False
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.crop_history = []
        self.redo_stack = []
        self.canvas.delete("all")
        self.cropped_label.config(image="", text="Cropped image will appear here")
        self.resize_slider.set(100)

    def load_image(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if file_path:
            self.reset_state()
            self.cv_image = cv2.imread(file_path)
            self.original_image = self.cv_image.copy()
            self.show_full_image(resize=True)

    def restart_to_original(self, event=None):
        if self.original_image is not None:
            self.cv_image = self.original_image.copy()
            self.cropped_cv_image = None
            self.crop_history.clear()
            self.redo_stack.clear()
            self.resize_slider.set(100)
            self.is_grayscale = False
            self.show_full_image(resize=True)
            self.cropped_label.config(image="", text="Cropped image will appear here")

    def show_full_image(self, resize=True):
        if self.cv_image is not None:
            display = self.cv_image.copy()
            h, w = display.shape[:2]
            self.display_scale = 1.0
            if resize and w > 600:
                self.display_scale = 600 / w
                display = cv2.resize(display, (int(w * self.display_scale), int(h * self.display_scale)))
            rgb_image = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            self.tk_image = ImageTk.PhotoImage(Image.fromarray(rgb_image))
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

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
        scale = 1 / self.display_scale if self.display_scale != 0 else 1
        x1, y1 = int(min(self.start_x, end_x) * scale), int(min(self.start_y, end_y) * scale)
        x2, y2 = int(max(self.start_x, end_x) * scale), int(max(self.start_y, end_y) * scale)
        if self.cv_image is not None:
            cropped = self.cv_image[y1:y2, x1:x2]
            if cropped.size > 0:
                self.crop_history.append((self.cropped_cv_image.copy() if self.cropped_cv_image is not None else None,
                                          self.resize_slider.get(), self.is_grayscale))
                self.redo_stack.clear()
                self.cropped_cv_image = cropped
                self.show_cropped_image()

    def resize_image(self, image, scale):
        width = int(image.shape[1] * scale / 100)
        height = int(image.shape[0] * scale / 100)
        return cv2.resize(image, (width, height))

    def show_cropped_image(self, event=None):
        scale = self.resize_slider.get()
        img = self.cropped_cv_image if self.cropped_cv_image is not None else self.cv_image
        if img is None:
            return
        resized = self.resize_image(img, scale)
        image_data = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY) if self.is_grayscale else cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        self.display_image = Image.fromarray(image_data)
        self.cropped_tk_image = ImageTk.PhotoImage(self.display_image)
        self.cropped_label.config(image=self.cropped_tk_image, text="")

    def apply_resize(self, value=None):
        self.show_cropped_image()

    def toggle_grayscale(self, event=None):
        self.is_grayscale = not self.is_grayscale
        self.show_cropped_image()

    def save_cropped_image(self, event=None):
        scale = self.resize_slider.get()
        img = self.cropped_cv_image if self.cropped_cv_image is not None else self.cv_image
        if img is None:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
        if file_path:
            resized = self.resize_image(img, scale)
            if self.is_grayscale:
                resized = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(file_path, resized)
            print(f"Image saved to {file_path}")

    def undo_crop(self, event=None):
        if self.crop_history:
            current_state = (self.cropped_cv_image.copy() if self.cropped_cv_image is not None else None,
                             self.resize_slider.get(), self.is_grayscale)
            self.redo_stack.append(current_state)
            prev_img, prev_scale, prev_gray = self.crop_history.pop()
            self.cropped_cv_image = prev_img
            self.resize_slider.set(prev_scale)
            self.is_grayscale = prev_gray
            self.show_cropped_image()
        else:
            self.cropped_label.config(image="", text="No previous crop to undo.")
            self.cropped_cv_image = None

    def redo_crop(self, event=None):
        if self.redo_stack:
            current_state = (self.cropped_cv_image.copy() if self.cropped_cv_image is not None else None,
                             self.resize_slider.get(), self.is_grayscale)
            self.crop_history.append(current_state)
            redo_img, redo_scale, redo_gray = self.redo_stack.pop()
            self.cropped_cv_image = redo_img
            self.resize_slider.set(redo_scale)
            self.is_grayscale = redo_gray
            self.show_cropped_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
