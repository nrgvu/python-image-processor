import cv2
import numpy as np
from tkinter import filedialog, Tk, Label, Button, Canvas, PhotoImage, OptionMenu, StringVar
from PIL import Image, ImageTk
import tkinter as tk
import zlib
from io import BytesIO

# Image processing functions
def remove_noise(image):
    return cv2.medianBlur(image, 5)

def detect_objects(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

def smoothing(image):
    return cv2.bilateralFilter(image, 15, 75, 75)

def blur(image):
    return cv2.GaussianBlur(image, (11, 11), 0)

class ImageEditorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Image Editor")
        master.configure(bg="#f0f0f0")

        self.original_image = None
        self.processed_image = None
        self.image_tk = None
        self.compressed_data = None

        self.upload_button = Button(master, text="Upload Image", command=self.upload_image, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.upload_button.pack(pady=10)

        self.image_canvas = Canvas(master, width=400, height=300, bg="white")
        self.image_canvas.pack(pady=10)

        self.filter_frame = tk.Frame(master, bg="#f0f0f0")
        self.filter_frame.pack(pady=10)

        self.noise_button = Button(self.filter_frame, text="Remove Noise", command=self.apply_noise, bg="#2196F3", fg="white", font=("Arial", 10))
        self.noise_button.pack(side=tk.LEFT, padx=5)

        self.detect_button = Button(self.filter_frame, text="Detect Objects", command=self.apply_detect_objects, bg="#2196F3", fg="white", font=("Arial", 10))
        self.detect_button.pack(side=tk.LEFT, padx=5)

        self.smoothing_button = Button(self.filter_frame, text="Smoothing", command=self.apply_smoothing, bg="#2196F3", fg="white", font=("Arial", 10))
        self.smoothing_button.pack(side=tk.LEFT, padx=5)

        self.blur_button = Button(self.filter_frame, text="Blur", command=self.apply_blur, bg="#2196F3", fg="white", font=("Arial", 10))
        self.blur_button.pack(side=tk.LEFT, padx=5)

        self.grayscale_button = Button(self.filter_frame, text="Grayscale", command=self.apply_grayscale, bg="#2196F3", fg="white", font=("Arial", 10))
        self.grayscale_button.pack(side=tk.LEFT, padx=5)

        self.sharpen_button = Button(self.filter_frame, text="Sharpen", command=self.apply_sharpen, bg="#2196F3", fg="white", font=("Arial", 10))
        self.sharpen_button.pack(side=tk.LEFT, padx=5)

        self.invert_button = Button(self.filter_frame, text="Invert Colors", command=self.apply_invert, bg="#2196F3", fg="white", font=("Arial", 10))
        self.invert_button.pack(side=tk.LEFT, padx=5)

        self.sepia_button = Button(self.filter_frame, text="Sepia Tone", command=self.apply_sepia, bg="#2196F3", fg="white", font=("Arial", 10))
        self.sepia_button.pack(side=tk.LEFT, padx=5)

        self.emboss_button = Button(self.filter_frame, text="Emboss", command=self.apply_emboss, bg="#2196F3", fg="white", font=("Arial", 10))
        self.emboss_button.pack(side=tk.LEFT, padx=5)

        self.compress_label = Label(master, text="JPEG Compression Level:", bg="#f0f0f0", font=("Arial", 10))
        self.compress_label.pack(pady=5)

        self.compression_level = StringVar(master)
        self.compression_level.set("Medium Compression")  # Default value
        self.compress_options = ["High Compression", "Medium Compression", "Low Compression"]
        self.compress_dropdown = OptionMenu(master, self.compression_level, *self.compress_options)
        self.compress_dropdown.pack(pady=5)

        self.compress_button = Button(master, text="Compress Image (JPEG)", command=self.compress_image, bg="#FF9800", fg="white", font=("Arial", 12))
        self.compress_button.pack(pady=10)

        self.download_button = Button(master, text="Download Image", command=self.download_image, bg="#008CBA", fg="white", font=("Arial", 12), state=tk.DISABLED)
        self.download_button.pack(pady=10)

        self.message_label = Label(master, text="", fg="green", bg="#f0f0f0", font=("Arial", 10))
        self.message_label.pack(pady=5)

        self.error_label = Label(master, text="", fg="red", bg="#f0f0f0", font=("Arial", 10))
        self.error_label.pack(pady=5)

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image File",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.tif"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("BMP files", "*.bmp"),
                ("GIF files", "*.gif"),
                ("TIFF files", "*.tiff *.tif"),
                ("All files", "*.*"),
            ]
        )
        if file_path:
            try:
                img_pil = Image.open(file_path)
                self.original_image = np.array(img_pil)
                if len(self.original_image.shape) == 2:
                    self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_GRAY2RGB)
                elif self.original_image.shape[2] == 4:
                    pass
                else:
                    self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2BGR)
                    self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)

                self.processed_image = self.original_image.copy()
                self.display_image(self.processed_image)
                self.show_message("Image uploaded successfully.")
                self.clear_error()
                self.compressed_data = None
                self.download_button.config(state=tk.DISABLED)

            except Exception as e:
                self.show_error(f"Error loading image: {e}. Please ensure it's a valid image file.")
                self.original_image = None
                self.processed_image = None
                self.clear_canvas()
        else:
            self.show_message("No image selected.")

    def display_image(self, image):
        try:
            if image.shape[2] == 4:
                image_pil = Image.fromarray(image, 'RGBA')
            else:
                image_pil = Image.fromarray(image)
            image_pil = image_pil.resize((400, 300), Image.Resampling.LANCZOS)
            self.image_tk = ImageTk.PhotoImage(image_pil)
            self.image_canvas.config(width=self.image_tk.width(), height=self.image_tk.height())
            self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        except Exception as e:
            self.show_error(f"Error displaying image: {e}")

    def apply_filter_and_display(self, filter_func):
        if self.original_image is not None:
            try:
                if self.original_image.shape[2] == 4:
                    r, g, b, a = cv2.split(self.original_image)
                    bgr_image = cv2.cvtColor(self.original_image[:, :, :3], cv2.COLOR_RGB2BGR)
                    processed_bgr = filter_func(bgr_image)
                    processed_rgb = cv2.cvtColor(processed_bgr, cv2.COLOR_BGR2RGB)
                    self.processed_image = cv2.merge([processed_rgb[:, :, 0], processed_rgb[:, :, 1], processed_rgb[:, :, 2], a])
                else:
                    bgr_image = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2BGR)
                    processed_bgr = filter_func(bgr_image)
                    self.processed_image = cv2.cvtColor(processed_bgr, cv2.COLOR_BGR2RGB)

                self.display_image(self.processed_image)
                self.show_message(f"Filter applied successfully.")
                self.clear_error()
                self.compressed_data = None # Invalidate previous compression
                self.download_button.config(state=tk.DISABLED)
            except Exception as e:
                self.show_error(f"Error applying filter: {e}")
        else:
            self.show_error("Please upload an image first.")

    def apply_noise(self):
        self.apply_filter_and_display(remove_noise)

    def apply_detect_objects(self):
        self.apply_filter_and_display(detect_objects)

    def apply_smoothing(self):
        self.apply_filter_and_display(smoothing)

    def apply_blur(self):
        self.apply_filter_and_display(blur)

    def apply_grayscale(self):
        self.apply_filter_and_display(lambda img: cv2.cvtColor(img, cv2.COLOR_RGB2GRAY))

    def apply_sharpen(self):
        kernel = np.array([[-1, -1, -1],
                           [-1,  9, -1],
                           [-1, -1, -1]])
        self.apply_filter_and_display(lambda img: cv2.cvtColor(cv2.filter2D(cv2.cvtColor(img, cv2.COLOR_RGB2BGR), -1, kernel), cv2.COLOR_BGR2RGB))

    def apply_invert(self):
        self.apply_filter_and_display(lambda img: 255 - img)

    def apply_sepia(self):
        sepia_kernel = np.array([[0.272, 0.534, 0.131],
                                 [0.349, 0.686, 0.168],
                                 [0.393, 0.769, 0.189]])
        def sepia_filter(img):
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            sepia_image = cv2.transform(img_bgr, sepia_kernel)
            sepia_image = np.clip(sepia_image, 0, 255).astype(np.uint8)
            return cv2.cvtColor(sepia_image, cv2.COLOR_BGR2RGB)
        self.apply_filter_and_display(sepia_filter)

    def apply_emboss(self):
        kernel = np.array([[-2, -1, 0],
                           [-1,  1, 1],
                           [ 0,  1, 2]])
        self.apply_filter_and_display(lambda img: cv2.cvtColor(cv2.filter2D(cv2.cvtColor(img, cv2.COLOR_RGB2BGR), -1, kernel), cv2.COLOR_BGR2RGB))

    def compress_image(self):
        if self.processed_image is not None:
            try:
                img_pil = Image.fromarray(self.processed_image)
                buffer = BytesIO()
                quality = 0
                level = self.compression_level.get()
                if level == "High Compression":
                    quality = 30
                elif level == "Medium Compression":
                    quality = 70
                elif level == "Low Compression":
                    quality = 95

                img_pil.save(buffer, format="JPEG", quality=quality)
                self.compressed_data = buffer.getvalue()
                original_size = self.get_image_size_bytes(self.processed_image)
                compressed_size = len(self.compressed_data)
                compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
                self.show_message(f"Image compressed using JPEG ({level}). Original size: {original_size // 1024} KB, Compressed size: {compressed_size // 1024} KB (Compression Ratio: {compression_ratio:.2f}).")
                self.clear_error()
                self.download_button.config(state=tk.NORMAL)
            except Exception as e:
                self.show_error(f"Error compressing image: {e}")
                self.download_button.config(state=tk.DISABLED)
        else:
            self.show_error("Please upload and optionally edit an image before compressing.")
            self.download_button.config(state=tk.DISABLED)

    def get_image_size_bytes(self, image_np):
        img_pil = Image.fromarray(image_np)
        buffer = BytesIO()
        img_pil.save(buffer, format="PNG") # Use a lossless format to estimate original size
        return buffer.tell()

    def download_image(self):
        if self.processed_image is not None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG file", "*.png"), ("JPEG file", "*.jpg *.jpeg"), ("All files", "*.*")],
                title="Save Image As"
            )
            if file_path:
                try:
                    if file_path.lower().endswith(('.jpg', '.jpeg')):
                        if self.compressed_data:
                            with open(file_path, "wb") as f:
                                f.write(self.compressed_data)
                            self.show_message(f"Image saved as JPEG to {file_path}")
                        else:
                            img_pil = Image.fromarray(self.processed_image)
                            img_pil.save(file_path, format="JPEG", quality=95)
                            self.show_message(f"Image saved as JPEG to {file_path}")
                    else:
                        img_pil = Image.fromarray(self.processed_image)
                        img_pil.save(file_path, format="PNG")
                        self.show_message(f"Image saved as PNG to {file_path}")
                    self.clear_error()
                except Exception as e:
                    self.show_error(f"Error saving image: {e}")
        else:
            self.show_error("Please upload an image first.")

    def show_message(self, message):
        self.message_label.config(text=message, fg="green")
        self.error_label.config(text="")

    def show_error(self, message):
        self.error_label.config(text=f"Error: {message}", fg="red")
        self.message_label.config(text="")

    def clear_canvas(self):
        self.image_canvas.delete("all")
        self.image_tk = None

    def clear_error(self):
        self.error_label.config(text="")

if __name__ == "__main__":
    root = Tk()
    gui = ImageEditorGUI(root)
    root.mainloop()