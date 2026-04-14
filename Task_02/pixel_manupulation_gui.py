import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import numpy as np
import os
import random
from datetime import datetime
import threading

class ImageEncryptionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Encryption Tool - Pixel Manipulation")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        # Variables
        self.current_image = None
        self.current_image_path = None
        self.encrypted_image = None
        self.image_display = None
        self.original_preview = None
        self.processed_preview = None
        
        # Colors and styling
        self.bg_color = "#2b2b2b"
        self.fg_color = "#ffffff"
        self.accent_color = "#4CAF50"
        self.button_color = "#3c3c3c"
        
        self.root.configure(bg=self.bg_color)
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_frame, bg=self.bg_color, width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Right panel - Image Display
        right_panel = tk.Frame(main_frame, bg=self.bg_color)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Setup left panel content
        self.setup_controls(left_panel)
        
        # Setup right panel content
        self.setup_image_display(right_panel)
        
    def setup_controls(self, parent):
        # Title
        title_label = tk.Label(parent, text="Image Encryption Tool", 
                               font=("Arial", 18, "bold"), 
                               bg=self.bg_color, fg=self.accent_color)
        title_label.pack(pady=10)
        
        # File selection frame
        file_frame = tk.LabelFrame(parent, text="File Selection", 
                                   bg=self.bg_color, fg=self.fg_color,
                                   font=("Arial", 10, "bold"))
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(file_frame, text="Load Image", command=self.load_image,
                 bg=self.button_color, fg=self.fg_color, 
                 font=("Arial", 10), cursor="hand2").pack(fill=tk.X, padx=5, pady=5)
        
        self.file_label = tk.Label(file_frame, text="No image loaded", 
                                   bg=self.bg_color, fg=self.fg_color,
                                   wraplength=300)
        self.file_label.pack(padx=5, pady=5)
        
        # Encryption method selection
        method_frame = tk.LabelFrame(parent, text="Encryption Method", 
                                     bg=self.bg_color, fg=self.fg_color,
                                     font=("Arial", 10, "bold"))
        method_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.method_var = tk.StringVar(value="xor")
        methods = [
            ("XOR Encryption", "xor"),
            ("Additive Encryption", "additive"),
            ("Multiplicative Encryption", "multiplicative"),
            ("Pixel Swapping", "swap"),
            ("Channel Mixing", "channel"),
            ("Advanced Multi-Layer", "advanced")
        ]
        
        for text, value in methods:
            tk.Radiobutton(method_frame, text=text, variable=self.method_var,
                          value=value, bg=self.bg_color, fg=self.fg_color,
                          selectcolor=self.bg_color, font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=2)
        
        # Key/Value input
        key_frame = tk.LabelFrame(parent, text="Encryption Parameters", 
                                  bg=self.bg_color, fg=self.fg_color,
                                  font=("Arial", 10, "bold"))
        key_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(key_frame, text="Key/Shift Value:", 
                bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W, padx=5, pady=2)
        self.key_entry = tk.Entry(key_frame, bg=self.button_color, fg=self.fg_color,
                                  insertbackground=self.fg_color)
        self.key_entry.pack(fill=tk.X, padx=5, pady=5)
        self.key_entry.insert(0, "42")
        
        # Operation buttons
        button_frame = tk.Frame(parent, bg=self.bg_color)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.encrypt_btn = tk.Button(button_frame, text="Encrypt", 
                                     command=self.encrypt_image,
                                     bg="#4CAF50", fg="white", 
                                     font=("Arial", 11, "bold"),
                                     cursor="hand2", height=2)
        self.encrypt_btn.pack(fill=tk.X, pady=5)
        
        self.decrypt_btn = tk.Button(button_frame, text="Decrypt", 
                                     command=self.decrypt_image,
                                     bg="#f44336", fg="white", 
                                     font=("Arial", 11, "bold"),
                                     cursor="hand2", height=2)
        self.decrypt_btn.pack(fill=tk.X, pady=5)
        
        # Save button
        self.save_btn = tk.Button(button_frame, text="Save Image", 
                                  command=self.save_image,
                                  bg="#2196F3", fg="white", 
                                  font=("Arial", 11, "bold"),
                                  cursor="hand2", height=2,
                                  state=tk.DISABLED)
        self.save_btn.pack(fill=tk.X, pady=5)
        
        # Status frame
        status_frame = tk.LabelFrame(parent, text="Status", 
                                     bg=self.bg_color, fg=self.fg_color,
                                     font=("Arial", 10, "bold"))
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=8,
                                                      bg=self.button_color,
                                                      fg=self.fg_color,
                                                      font=("Consolas", 9))
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Clear status button
        tk.Button(status_frame, text="Clear Status", 
                 command=self.clear_status,
                 bg=self.button_color, fg=self.fg_color,
                 cursor="hand2").pack(pady=5)
        
    def setup_image_display(self, parent):
        # Original image frame
        original_frame = tk.LabelFrame(parent, text="Original Image", 
                                       bg=self.bg_color, fg=self.fg_color,
                                       font=("Arial", 11, "bold"))
        original_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.original_canvas = tk.Canvas(original_frame, bg=self.button_color,
                                         highlightthickness=0)
        self.original_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Processed image frame
        processed_frame = tk.LabelFrame(parent, text="Processed Image", 
                                        bg=self.bg_color, fg=self.fg_color,
                                        font=("Arial", 11, "bold"))
        processed_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.processed_canvas = tk.Canvas(processed_frame, bg=self.button_color,
                                          highlightthickness=0)
        self.processed_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def log_message(self, message, is_error=False):
        """Add message to status log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = "red" if is_error else "green"
        self.status_text.insert(tk.END, f"[{timestamp}] ", "time")
        self.status_text.insert(tk.END, f"{message}\n", color)
        self.status_text.see(tk.END)
        
        # Configure tags
        self.status_text.tag_config("time", foreground="#888888")
        self.status_text.tag_config("green", foreground="#4CAF50")
        self.status_text.tag_config("red", foreground="#f44336")
        
    def clear_status(self):
        """Clear status text"""
        self.status_text.delete(1.0, tk.END)
        
    def load_image(self):
        """Load image from file"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.current_image = Image.open(file_path)
                self.current_image_path = file_path
                
                # Update file label
                filename = os.path.basename(file_path)
                size = f"{self.current_image.size[0]}x{self.current_image.size[1]}"
                mode = self.current_image.mode
                self.file_label.config(text=f"{filename}\n{size} | {mode}")
                
                # Display original image
                self.display_image(self.current_image, self.original_canvas, "original")
                
                # Reset processed image
                self.processed_canvas.delete("all")
                self.processed_preview = None
                self.save_btn.config(state=tk.DISABLED)
                
                self.log_message(f"✅ Loaded image: {filename}")
                self.log_message(f"   Dimensions: {size}, Mode: {mode}")
                
            except Exception as e:
                self.log_message(f"❌ Error loading image: {str(e)}", is_error=True)
                
    def display_image(self, image, canvas, image_type):
        """Display image on canvas with proper scaling"""
        try:
            # Get canvas dimensions
            canvas.update_idletasks()
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 400
                canvas_height = 300
            
            # Calculate scaling factor
            img_width, img_height = image.size
            scale = min(canvas_width / img_width, canvas_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize image
            resized_image = image.copy()
            resized_image.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(resized_image)
            
            # Store reference to prevent garbage collection
            if image_type == "original":
                self.original_preview = photo
            else:
                self.processed_preview = photo
            
            # Clear canvas and display image
            canvas.delete("all")
            canvas.create_image(canvas_width // 2, canvas_height // 2, 
                               anchor=tk.CENTER, image=photo)
            
        except Exception as e:
            self.log_message(f"❌ Error displaying image: {str(e)}", is_error=True)
    
    def encrypt_image(self):
        """Encrypt the loaded image"""
        if self.current_image is None:
            messagebox.showwarning("No Image", "Please load an image first!")
            return
        
        try:
            method = self.method_var.get()
            key_str = self.key_entry.get().strip()
            
            if not key_str:
                messagebox.showwarning("Missing Parameter", "Please enter a key/value!")
                return
            
            key = int(key_str)
            
            self.log_message(f"🔐 Starting encryption using {method.upper()} method...")
            
            # Run encryption in separate thread to prevent GUI freezing
            thread = threading.Thread(target=self.process_encryption, args=(method, key))
            thread.start()
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Key must be an integer!")
        except Exception as e:
            self.log_message(f"❌ Encryption error: {str(e)}", is_error=True)
    
    def process_encryption(self, method, key):
        """Process encryption in background"""
        try:
            if method == "xor":
                result_image = self.encrypt_xor(self.current_image, key)
            elif method == "additive":
                result_image = self.encrypt_additive(self.current_image, key)
            elif method == "multiplicative":
                result_image = self.encrypt_multiplicative(self.current_image, key)
            elif method == "swap":
                result_image = self.swap_pixels(self.current_image, key)
            elif method == "channel":
                result_image = self.channel_mix(self.current_image)
            elif method == "advanced":
                result_image = self.encrypt_advanced(self.current_image, key)
            else:
                self.log_message("❌ Unknown encryption method!", is_error=True)
                return
            
            self.encrypted_image = result_image
            
            # Update GUI in main thread
            self.root.after(0, self.update_processed_display, result_image)
            self.root.after(0, lambda: self.save_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.log_message("✅ Encryption completed successfully!"))
            
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"❌ Encryption failed: {str(e)}", is_error=True))
    
    def decrypt_image(self):
        """Decrypt the processed image"""
        if self.encrypted_image is None:
            messagebox.showwarning("No Encrypted Image", "Please encrypt an image first!")
            return
        
        try:
            method = self.method_var.get()
            key_str = self.key_entry.get().strip()
            
            if not key_str:
                messagebox.showwarning("Missing Parameter", "Please enter a key/value!")
                return
            
            key = int(key_str)
            
            self.log_message(f"🔓 Starting decryption using {method.upper()} method...")
            
            # Run decryption in separate thread
            thread = threading.Thread(target=self.process_decryption, args=(method, key))
            thread.start()
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Key must be an integer!")
        except Exception as e:
            self.log_message(f"❌ Decryption error: {str(e)}", is_error=True)
    
    def process_decryption(self, method, key):
        """Process decryption in background"""
        try:
            if method == "xor":
                result_image = self.encrypt_xor(self.encrypted_image, key)
            elif method == "additive":
                result_image = self.encrypt_additive(self.encrypted_image, -key % 256)
            elif method == "multiplicative":
                # Find modular inverse for decryption
                inv_key = pow(key, -1, 256)
                result_image = self.encrypt_multiplicative(self.encrypted_image, inv_key)
            elif method == "swap":
                result_image = self.decrypt_swap(self.encrypted_image, key)
            elif method == "channel":
                result_image = self.channel_mix(self.encrypted_image)
            elif method == "advanced":
                result_image = self.decrypt_advanced(self.encrypted_image, key)
            else:
                self.log_message("❌ Unknown decryption method!", is_error=True)
                return
            
            # Update GUI in main thread
            self.root.after(0, lambda: self.update_processed_display(result_image))
            self.root.after(0, lambda: self.log_message("✅ Decryption completed successfully!"))
            
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"❌ Decryption failed: {str(e)}", is_error=True))
    
    def update_processed_display(self, image):
        """Update the processed image display"""
        self.display_image(image, self.processed_canvas, "processed")
    
    def save_image(self):
        """Save the processed image"""
        if self.encrypted_image is None:
            messagebox.showwarning("No Image", "No processed image to save!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.encrypted_image.save(file_path)
                self.log_message(f"💾 Image saved to: {file_path}")
                messagebox.showinfo("Success", f"Image saved successfully!\n{file_path}")
            except Exception as e:
                self.log_message(f"❌ Error saving image: {str(e)}", is_error=True)
    
    # Encryption Algorithms
    
    def encrypt_xor(self, image, key):
        """XOR encryption/decryption"""
        img_array = np.array(image)
        np.random.seed(key)
        key_array = np.random.randint(0, 256, img_array.shape, dtype=np.uint8)
        encrypted_array = img_array ^ key_array
        return Image.fromarray(encrypted_array)
    
    def encrypt_additive(self, image, shift):
        """Additive encryption"""
        img_array = np.array(image, dtype=np.int16)
        encrypted_array = (img_array + shift) % 256
        encrypted_array = encrypted_array.astype(np.uint8)
        return Image.fromarray(encrypted_array)
    
    def encrypt_multiplicative(self, image, factor):
        """Multiplicative encryption"""
        img_array = np.array(image, dtype=np.int16)
        encrypted_array = (img_array * factor) % 256
        encrypted_array = encrypted_array.astype(np.uint8)
        return Image.fromarray(encrypted_array)
    
    def swap_pixels(self, image, seed):
        """Pixel swapping encryption"""
        img_array = np.array(image)
        original_shape = img_array.shape
        flat_array = img_array.flatten()
        pixels = list(flat_array)
        
        random.seed(seed)
        for i in range(len(pixels) - 1, 0, -1):
            j = random.randint(0, i)
            pixels[i], pixels[j] = pixels[j], pixels[i]
        
        shuffled_array = np.array(pixels).reshape(original_shape)
        return Image.fromarray(shuffled_array)
    
    def decrypt_swap(self, image, seed):
        """Pixel swapping decryption"""
        img_array = np.array(image)
        original_shape = img_array.shape
        flat_array = img_array.flatten()
        pixels = list(flat_array)
        
        random.seed(seed)
        indices = list(range(len(pixels)))
        for i in range(len(indices) - 1, 0, -1):
            j = random.randint(0, i)
            indices[i], indices[j] = indices[j], indices[i]
        
        reversed_pixels = [0] * len(pixels)
        for original_pos, new_pos in enumerate(indices):
            reversed_pixels[new_pos] = pixels[original_pos]
        
        restored_array = np.array(reversed_pixels).reshape(original_shape)
        return Image.fromarray(restored_array)
    
    def channel_mix(self, image):
        """Channel mixing for RGB images"""
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        img_array = np.array(image)
        mixed_array = img_array.copy()
        mixed_array[:, :, 0] = img_array[:, :, 1]  # R = G
        mixed_array[:, :, 1] = img_array[:, :, 2]  # G = B
        mixed_array[:, :, 2] = img_array[:, :, 0]  # B = R
        
        return Image.fromarray(mixed_array)
    
    def encrypt_advanced(self, image, key):
        """Multi-layer encryption"""
        # Step 1: XOR encryption
        img1 = self.encrypt_xor(image, key)
        # Step 2: Pixel swapping
        img2 = self.swap_pixels(img1, key)
        # Step 3: Channel mixing
        if img2.mode == 'RGB':
            img3 = self.channel_mix(img2)
        else:
            img3 = img2
        return img3
    
    def decrypt_advanced(self, image, key):
        """Multi-layer decryption"""
        # Reverse order
        if image.mode == 'RGB':
            img1 = self.channel_mix(image)
        else:
            img1 = image
        img2 = self.decrypt_swap(img1, key)
        img3 = self.encrypt_xor(img2, key)
        return img3

def main():
    root = tk.Tk()
    app = ImageEncryptionGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    # Check for required libraries
    try:
        from PIL import Image, ImageTk
        import numpy as np
    except ImportError as e:
        print(f"❌ Missing required library: {e}")
        print("Please install required packages:")
        print("pip install Pillow numpy")
        exit(1)
    
    main()
