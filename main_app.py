import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import cv2
from auth_system import KnuckleAuthSystem

class KnuckleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Knuckle Biometric System")
        self.root.geometry("600x500")
        
        # Initialize backend
        self.auth = KnuckleAuthSystem()
        
        # Variable to store selected file path
        self.selected_image_path = None

        # --- UI Elements ---
        
        # Title
        title_label = tk.Label(root, text="Knuckle Authentication", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        # User ID Frame
        frame_user = tk.Frame(root)
        frame_user.pack(pady=5)
        tk.Label(frame_user, text="User ID:", font=("Arial", 12)).pack(side=tk.LEFT)
        self.entry_user = tk.Entry(frame_user, font=("Arial", 12), width=20)
        self.entry_user.pack(side=tk.LEFT, padx=10)

        # Image Selection Frame
        frame_img = tk.Frame(root)
        frame_img.pack(pady=10)
        
        btn_browse = tk.Button(frame_img, text="1. Select Knuckle Image", command=self.browse_image, bg="#e1e1e1")
        btn_browse.pack(side=tk.LEFT, padx=5)
        
        self.lbl_image_status = tk.Label(frame_img, text="No image selected", fg="blue")
        self.lbl_image_status.pack(side=tk.LEFT)

        # Image Preview
        self.lbl_preview = tk.Label(root, text="(Image Preview)", bg="#f0f0f0", width=200, height=200)
        self.lbl_preview.pack(pady=10)

        # Action Buttons
        frame_actions = tk.Frame(root)
        frame_actions.pack(pady=20)
        
        btn_register = tk.Button(frame_actions, text="Register User", command=self.register, bg="#4CAF50", fg="white", font=("Arial", 11), width=15)
        btn_register.pack(side=tk.LEFT, padx=5)
        
        btn_login = tk.Button(frame_actions, text="Verify Login", command=self.verify, bg="#2196F3", fg="white", font=("Arial", 11), width=15)
        btn_login.pack(side=tk.LEFT, padx=5)

        btn_admin = tk.Button(frame_actions, text="Admin Visualize", command=self.admin_visualize, bg="#9C27B0", fg="white", font=("Arial", 11), width=15)
        btn_admin.pack(side=tk.LEFT, padx=5)

        # Log / Status Area
        self.text_log = tk.Text(root, height=5, width=60, state=tk.DISABLED, font=("Courier", 10))
        self.text_log.pack(pady=10)

    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.selected_image_path = file_path
            self.lbl_image_status.config(text=os.path.basename(file_path))
            
            # Show Preview
            img = Image.open(file_path)
            img.thumbnail((250, 250)) # Resize for preview
            img_tk = ImageTk.PhotoImage(img)
            
            self.lbl_preview.config(image=img_tk, text="")
            self.lbl_preview.image = img_tk # Keep reference
            
            self.log(f"Image loaded: {os.path.basename(file_path)}")

    def register(self):
        user_id = self.entry_user.get().strip()
        if not user_id:
            messagebox.showwarning("Input Error", "Please enter a User ID.")
            return
        if not self.selected_image_path:
            messagebox.showwarning("Input Error", "Please select an image first.")
            return

        success, message = self.auth.register_user(user_id, self.selected_image_path)
        self.log(message)
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def verify(self):
        user_id = self.entry_user.get().strip()
        if not user_id:
            messagebox.showwarning("Input Error", "Please enter a User ID.")
            return
        if not self.selected_image_path:
            messagebox.showwarning("Input Error", "Please select an image to verify.")
            return

        success, score, message = self.auth.verify_user(user_id, self.selected_image_path)
        
        self.log(message)
        
        if success:
            messagebox.showinfo("ACCESS GRANTED", message)
        else:
            messagebox.showerror("ACCESS DENIED", message)

    def admin_visualize(self):
        user_id = self.entry_user.get().strip()
        if not user_id:
            messagebox.showwarning("Input Error", "Please enter a User ID.")
            return
        if not self.selected_image_path:
            messagebox.showwarning("Input Error", "Please select an image to verify against.")
            return

        self.log("Launching Admin Visualization...")
        success, message = self.auth.visualize_match(user_id, self.selected_image_path)
        
        self.log(message)
        if not success:
            messagebox.showerror("Visualization Error", message)

    def log(self, message):
        self.text_log.config(state=tk.NORMAL)
        self.text_log.insert(tk.END, message + "\n")
        self.text_log.see(tk.END)
        self.text_log.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = KnuckleApp(root)
    root.mainloop()
