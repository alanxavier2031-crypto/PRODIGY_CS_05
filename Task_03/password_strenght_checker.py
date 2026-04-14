import tkinter as tk
from tkinter import ttk, messagebox
import re
import math
from collections import Counter

class PasswordComplexityChecker:
    def __init__(self):
        self.criteria = {
            'length': {'weight': 2, 'threshold': 12},
            'uppercase': {'weight': 1, 'min_count': 1},
            'lowercase': {'weight': 1, 'min_count': 1},
            'digits': {'weight': 1, 'min_count': 1},
            'special': {'weight': 2, 'min_count': 1},
            'no_repeating': {'weight': 1, 'max_repeating': 3},
            'no_sequential': {'weight': 1, 'max_sequential': 3},
            'no_common': {'weight': 2, 'penalty': True}
        }
        
        self.common_passwords = self.load_common_passwords()
        self.common_patterns = [
            r'password', r'123456', r'qwerty', r'abc123', r'admin',
            r'welcome', r'letmein', r'monkey', r'dragon', r'master'
        ]
        
    def load_common_passwords(self):
        """Load list of common passwords"""
        # Common weak passwords
        common = {
            'password', '123456', '123456789', 'qwerty', 'abc123', 'password123',
            'admin', 'letmein', 'welcome', 'monkey', 'dragon', 'master', 'football',
            'baseball', 'login', 'shadow', 'sunshine', 'iloveyou', 'princess',
            'rockyou', '1234567', '12345678', 'abc123', '111111', '123123'
        }
        return common
    
    def calculate_entropy(self, password):
        """Calculate password entropy (bits)"""
        charset_size = 0
        if re.search(r'[a-z]', password):
            charset_size += 26
        if re.search(r'[A-Z]', password):
            charset_size += 26
        if re.search(r'\d', password):
            charset_size += 10
        if re.search(r'[^a-zA-Z0-9]', password):
            charset_size += 32  # Common special characters
        
        if charset_size == 0:
            return 0
        
        entropy = len(password) * math.log2(charset_size)
        return entropy
    
    def check_length(self, password):
        """Check password length"""
        length = len(password)
        if length >= 16:
            return 10, "Excellent length (>15 characters)"
        elif length >= 12:
            return 8, "Good length (12-15 characters)"
        elif length >= 8:
            return 5, "Acceptable length (8-11 characters)"
        else:
            return 0, f"Poor length ({length}/8 minimum recommended)"
    
    def check_character_types(self, password):
        """Check presence of different character types"""
        score = 0
        details = []
        
        # Uppercase check
        if re.search(r'[A-Z]', password):
            uppercase_count = len(re.findall(r'[A-Z]', password))
            if uppercase_count >= 2:
                score += 2
                details.append(f"✓ Has {uppercase_count} uppercase letters")
            else:
                score += 1
                details.append(f"✓ Has uppercase letters")
        else:
            details.append("✗ Missing uppercase letters")
        
        # Lowercase check
        if re.search(r'[a-z]', password):
            lowercase_count = len(re.findall(r'[a-z]', password))
            if lowercase_count >= 2:
                score += 2
                details.append(f"✓ Has {lowercase_count} lowercase letters")
            else:
                score += 1
                details.append(f"✓ Has lowercase letters")
        else:
            details.append("✗ Missing lowercase letters")
        
        # Digits check
        if re.search(r'\d', password):
            digit_count = len(re.findall(r'\d', password))
            if digit_count >= 2:
                score += 2
                details.append(f"✓ Has {digit_count} digits")
            else:
                score += 1
                details.append(f"✓ Has digits")
        else:
            details.append("✗ Missing digits")
        
        # Special characters check
        if re.search(r'[^a-zA-Z0-9]', password):
            special_count = len(re.findall(r'[^a-zA-Z0-9]', password))
            if special_count >= 2:
                score += 3
                details.append(f"✓ Has {special_count} special characters")
            else:
                score += 2
                details.append(f"✓ Has special characters")
        else:
            details.append("✗ Missing special characters")
        
        return score, details
    
    def check_repeating_patterns(self, password):
        """Check for repeating characters or patterns"""
        score = 0
        details = []
        
        # Check for repeating characters
        repeating = re.findall(r'(.)\1{2,}', password)
        if repeating:
            penalty = len(repeating)
            score -= penalty
            details.append(f"✗ Contains repeating characters: {', '.join(set(repeating))}")
        else:
            score += 1
            details.append("✓ No repeating character patterns")
        
        # Check for sequential patterns
        sequential = 0
        for i in range(len(password) - 2):
            if ord(password[i+1]) - ord(password[i]) == 1 and ord(password[i+2]) - ord(password[i+1]) == 1:
                sequential += 1
        
        if sequential > 0:
            score -= sequential
            details.append(f"✗ Contains sequential patterns")
        else:
            score += 1
            details.append("✓ No sequential patterns")
        
        return score, details
    
    def check_common_patterns(self, password):
        """Check for common passwords and patterns"""
        score = 0
        details = []
        
        password_lower = password.lower()
        
        # Check against common password list
        if password_lower in self.common_passwords:
            score -= 5
            details.append("✗ Password is in common password list!")
            return score, details
        
        # Check for common patterns
        for pattern in self.common_patterns:
            if pattern in password_lower:
                score -= 2
                details.append(f"✗ Contains common pattern: '{pattern}'")
        
        # Check for keyboard patterns
        keyboard_patterns = ['qwerty', 'asdfgh', 'zxcvbn', '123456', 'qwertyuiop']
        for pattern in keyboard_patterns:
            if pattern in password_lower:
                score -= 3
                details.append(f"✗ Contains keyboard pattern: '{pattern}'")
        
        # Check for date patterns
        date_patterns = [r'\d{2}/\d{2}/\d{4}', r'\d{4}-\d{2}-\d{2}', r'\d{2}\.\d{2}\.\d{4}']
        for pattern in date_patterns:
            if re.search(pattern, password):
                score -= 2
                details.append("✗ Contains date pattern")
        
        if not details:
            score += 2
            details.append("✓ No common patterns detected")
        
        return score, details
    
    def check_variety(self, password):
        """Check character variety and uniqueness"""
        score = 0
        details = []
        
        unique_chars = len(set(password))
        total_chars = len(password)
        
        if total_chars > 0:
            uniqueness_ratio = unique_chars / total_chars
            if uniqueness_ratio > 0.8:
                score += 3
                details.append("✓ Excellent character variety")
            elif uniqueness_ratio > 0.6:
                score += 2
                details.append("✓ Good character variety")
            elif uniqueness_ratio > 0.4:
                score += 1
                details.append("✓ Acceptable character variety")
            else:
                details.append("✗ Low character variety (many repeated characters)")
        
        return score, details
    
    def calculate_strength(self, password):
        """Calculate overall password strength"""
        if not password:
            return {
                'score': 0,
                'strength': 'No Password',
                'color': 'gray',
                'details': ['Please enter a password to check'],
                'entropy': 0,
                'suggestions': []
            }
        
        total_score = 0
        all_details = []
        suggestions = []
        
        # Check length
        length_score, length_detail = self.check_length(password)
        total_score += length_score
        all_details.append(length_detail)
        if length_score < 5:
            suggestions.append("Increase password length to at least 12 characters")
        
        # Check character types
        type_score, type_details = self.check_character_types(password)
        total_score += type_score
        all_details.extend(type_details)
        
        # Check repeating patterns
        pattern_score, pattern_details = self.check_repeating_patterns(password)
        total_score += pattern_score
        all_details.extend(pattern_details)
        
        # Check common patterns
        common_score, common_details = self.check_common_patterns(password)
        total_score += common_score
        all_details.extend(common_details)
        
        # Check variety
        variety_score, variety_details = self.check_variety(password)
        total_score += variety_score
        all_details.extend(variety_details)
        
        # Calculate entropy
        entropy = self.calculate_entropy(password)
        
        # Add entropy-based suggestions
        if entropy < 30:
            suggestions.append("Password entropy is low - add more variety of characters")
        elif entropy < 50:
            suggestions.append("Consider increasing password length for better security")
        
        # Determine strength level (max possible score ~30)
        if total_score >= 25:
            strength = "Very Strong"
            color = "#2ecc71"  # Green
        elif total_score >= 20:
            strength = "Strong"
            color = "#27ae60"  # Dark Green
        elif total_score >= 15:
            strength = "Moderate"
            color = "#f39c12"  # Orange
        elif total_score >= 10:
            strength = "Weak"
            color = "#e67e22"  # Dark Orange
        else:
            strength = "Very Weak"
            color = "#e74c3c"  # Red
            suggestions.append("Completely rewrite your password with better practices")
        
        return {
            'score': total_score,
            'max_score': 30,
            'strength': strength,
            'color': color,
            'details': all_details,
            'entropy': entropy,
            'suggestions': suggestions[:3]  # Top 3 suggestions
        }

class PasswordCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Complexity Checker")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Initialize checker
        self.checker = PasswordComplexityChecker()
        
        # Colors
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#3498db"
        self.input_bg = "#2d2d2d"
        
        self.root.configure(bg=self.bg_color)
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="🔐 Password Complexity Checker", 
                               font=("Arial", 24, "bold"), 
                               bg=self.bg_color, fg=self.accent_color)
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(main_frame, text="Check your password strength with advanced analysis", 
                                  font=("Arial", 11), 
                                  bg=self.bg_color, fg=self.fg_color)
        subtitle_label.pack(pady=(0, 20))
        
        # Password input frame
        input_frame = tk.LabelFrame(main_frame, text="Enter Password", 
                                    font=("Arial", 12, "bold"),
                                    bg=self.bg_color, fg=self.fg_color)
        input_frame.pack(fill=tk.X, pady=10)
        
        # Password entry with show/hide functionality
        self.show_password = tk.BooleanVar(value=False)
        
        password_entry_frame = tk.Frame(input_frame, bg=self.bg_color)
        password_entry_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.password_entry = tk.Entry(password_entry_frame, 
                                       font=("Consolas", 14),
                                       bg=self.input_bg, 
                                       fg=self.fg_color,
                                       insertbackground=self.fg_color,
                                       show="*")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.toggle_btn = tk.Button(password_entry_frame, 
                                    text="👁 Show", 
                                    command=self.toggle_password_visibility,
                                    bg=self.input_bg, 
                                    fg=self.fg_color,
                                    cursor="hand2")
        self.toggle_btn.pack(side=tk.RIGHT)
        
        # Bind key release event for real-time checking
        self.password_entry.bind('<KeyRelease>', self.check_password)
        
        # Strength meter frame
        meter_frame = tk.Frame(main_frame, bg=self.bg_color)
        meter_frame.pack(fill=tk.X, pady=10)
        
        # Strength label
        self.strength_label = tk.Label(meter_frame, text="Password Strength: ", 
                                       font=("Arial", 14, "bold"),
                                       bg=self.bg_color, fg=self.fg_color)
        self.strength_label.pack()
        
        # Progress bar for strength
        self.strength_progress = ttk.Progressbar(meter_frame, length=400, mode='determinate')
        self.strength_progress.pack(pady=10)
        
        # Entropy display
        self.entropy_label = tk.Label(meter_frame, text="Entropy: 0 bits", 
                                      font=("Arial", 10),
                                      bg=self.bg_color, fg="#888888")
        self.entropy_label.pack()
        
        # Results frame (scrollable)
        results_frame = tk.LabelFrame(main_frame, text="Analysis Results", 
                                      font=("Arial", 12, "bold"),
                                      bg=self.bg_color, fg=self.fg_color)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Text widget for results
        self.results_text = tk.Text(results_frame, 
                                    height=15, 
                                    bg=self.input_bg,
                                    fg=self.fg_color,
                                    font=("Consolas", 10),
                                    wrap=tk.WORD)
        
        scrollbar = tk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Suggestions frame
        suggestions_frame = tk.LabelFrame(main_frame, text="Security Suggestions", 
                                          font=("Arial", 12, "bold"),
                                          bg=self.bg_color, fg=self.fg_color)
        suggestions_frame.pack(fill=tk.X, pady=10)
        
        self.suggestions_text = tk.Text(suggestions_frame, 
                                        height=4, 
                                        bg=self.input_bg,
                                        fg="#f39c12",
                                        font=("Arial", 10),
                                        wrap=tk.WORD)
        self.suggestions_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tips frame
        tips_frame = tk.LabelFrame(main_frame, text="Password Tips", 
                                   font=("Arial", 11, "bold"),
                                   bg=self.bg_color, fg=self.fg_color)
        tips_frame.pack(fill=tk.X, pady=10)
        
        tips = [
            "• Use at least 12 characters, preferably 16 or more",
            "• Combine uppercase, lowercase, numbers, and special characters",
            "• Avoid common words, names, or personal information",
            "• Don't use sequential characters (abc, 123) or repeated patterns",
            "• Use a password manager to generate and store complex passwords",
            "• Enable 2-factor authentication whenever possible"
        ]
        
        for tip in tips:
            tk.Label(tips_frame, text=tip, 
                    bg=self.bg_color, fg="#888888",
                    font=("Arial", 9), anchor=tk.W).pack(fill=tk.X, padx=10, pady=2)
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Generate strong password button
        self.generate_btn = tk.Button(button_frame, 
                                      text="🔒 Generate Strong Password", 
                                      command=self.generate_strong_password,
                                      bg="#27ae60", 
                                      fg="white",
                                      font=("Arial", 11, "bold"),
                                      cursor="hand2",
                                      height=2)
        self.generate_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Clear button
        self.clear_btn = tk.Button(button_frame, 
                                   text="🗑 Clear", 
                                   command=self.clear_all,
                                   bg="#e74c3c", 
                                   fg="white",
                                   font=("Arial", 11, "bold"),
                                   cursor="hand2",
                                   height=2)
        self.clear_btn.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)
        
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password.get():
            self.password_entry.config(show="*")
            self.toggle_btn.config(text="👁 Show")
            self.show_password.set(False)
        else:
            self.password_entry.config(show="")
            self.toggle_btn.config(text="🔒 Hide")
            self.show_password.set(True)
    
    def check_password(self, event=None):
        """Check password strength and update display"""
        password = self.password_entry.get()
        
        if not password:
            self.results_text.delete(1.0, tk.END)
            self.suggestions_text.delete(1.0, tk.END)
            self.strength_progress['value'] = 0
            self.strength_label.config(text="Password Strength: Enter a password")
            self.entropy_label.config(text="Entropy: 0 bits")
            return
        
        # Get strength analysis
        analysis = self.checker.calculate_strength(password)
        
        # Update strength meter
        score_percentage = (analysis['score'] / analysis['max_score']) * 100
        self.strength_progress['value'] = score_percentage
        self.strength_progress['style'] = 'green.Horizontal.TProgressbar'
        
        # Update strength label
        self.strength_label.config(text=f"Password Strength: {analysis['strength']}", 
                                  fg=analysis['color'])
        
        # Update entropy label
        self.entropy_label.config(text=f"Entropy: {analysis['entropy']:.1f} bits")
        
        # Update results text
        self.results_text.delete(1.0, tk.END)
        
        # Add header
        self.results_text.insert(tk.END, "=" * 60 + "\n")
        self.results_text.insert(tk.END, "PASSWORD ANALYSIS REPORT\n", "header")
        self.results_text.insert(tk.END, "=" * 60 + "\n\n")
        
        # Add score
        self.results_text.insert(tk.END, f"Overall Score: {analysis['score']}/{analysis['max_score']}\n")
        self.results_text.insert(tk.END, f"Strength Level: ", "label")
        self.results_text.insert(tk.END, f"{analysis['strength']}\n\n", analysis['strength'].lower().replace(' ', '_'))
        
        # Add details
        self.results_text.insert(tk.END, "DETAILED ANALYSIS:\n", "subheader")
        self.results_text.insert(tk.END, "-" * 40 + "\n")
        
        for detail in analysis['details']:
            if detail.startswith('✓'):
                self.results_text.insert(tk.END, f"  {detail}\n", "positive")
            elif detail.startswith('✗'):
                self.results_text.insert(tk.END, f"  {detail}\n", "negative")
            else:
                self.results_text.insert(tk.END, f"  {detail}\n")
        
        # Add entropy interpretation
        self.results_text.insert(tk.END, "\n" + "-" * 40 + "\n")
        self.results_text.insert(tk.END, "ENTROPY INTERPRETATION:\n", "subheader")
        
        if analysis['entropy'] < 30:
            self.results_text.insert(tk.END, "  Very low entropy - Easily guessable\n", "negative")
        elif analysis['entropy'] < 50:
            self.results_text.insert(tk.END, "  Low entropy - Could be cracked quickly\n", "negative")
        elif analysis['entropy'] < 70:
            self.results_text.insert(tk.END, "  Moderate entropy - Reasonably secure\n", "positive")
        elif analysis['entropy'] < 90:
            self.results_text.insert(tk.END, "  High entropy - Very secure\n", "positive")
        else:
            self.results_text.insert(tk.END, "  Excellent entropy - Extremely secure\n", "positive")
        
        # Configure text tags
        self.results_text.tag_config("header", font=("Arial", 12, "bold"), foreground=self.accent_color)
        self.results_text.tag_config("subheader", font=("Arial", 10, "bold"), foreground="#f39c12")
        self.results_text.tag_config("label", font=("Arial", 10, "bold"))
        self.results_text.tag_config("positive", foreground="#2ecc71")
        self.results_text.tag_config("negative", foreground="#e74c3c")
        self.results_text.tag_config("Very Strong", foreground="#2ecc71", font=("Arial", 10, "bold"))
        self.results_text.tag_config("Strong", foreground="#27ae60", font=("Arial", 10, "bold"))
        self.results_text.tag_config("Moderate", foreground="#f39c12", font=("Arial", 10, "bold"))
        self.results_text.tag_config("Weak", foreground="#e67e22", font=("Arial", 10, "bold"))
        self.results_text.tag_config("Very Weak", foreground="#e74c3c", font=("Arial", 10, "bold"))
        
        # Update suggestions
        self.suggestions_text.delete(1.0, tk.END)
        if analysis['suggestions']:
            self.suggestions_text.insert(tk.END, "💡 Recommendations to improve your password:\n\n")
            for i, suggestion in enumerate(analysis['suggestions'], 1):
                self.suggestions_text.insert(tk.END, f"{i}. {suggestion}\n")
        else:
            self.suggestions_text.insert(tk.END, "🎉 Excellent password! Keep up the good security practices!")
    
    def generate_strong_password(self):
        """Generate a strong random password"""
        import random
        import string
        
        # Define character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Ensure at least 2 of each type
        password_chars = [
            random.choice(lowercase),
            random.choice(lowercase),
            random.choice(uppercase),
            random.choice(uppercase),
            random.choice(digits),
            random.choice(digits),
            random.choice(special),
            random.choice(special)
        ]
        
        # Add more random characters to reach length 16
        all_chars = lowercase + uppercase + digits + special
        for _ in range(8):
            password_chars.append(random.choice(all_chars))
        
        # Shuffle the characters
        random.shuffle(password_chars)
        
        # Create password
        password = ''.join(password_chars)
        
        # Insert into entry and trigger check
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
        self.check_password()
        
        # Show success message
        messagebox.showinfo("Password Generated", 
                           "A strong password has been generated and inserted.\n"
                           "Make sure to save it securely!")
    
    def clear_all(self):
        """Clear all fields"""
        self.password_entry.delete(0, tk.END)
        self.results_text.delete(1.0, tk.END)
        self.suggestions_text.delete(1.0, tk.END)
        self.strength_progress['value'] = 0
        self.strength_label.config(text="Password Strength: ")
        self.entropy_label.config(text="Entropy: 0 bits")

def command_line_version():
    """Command-line version of the password checker"""
    checker = PasswordComplexityChecker()
    
    print("=" * 60)
    print("🔐 PASSWORD COMPLEXITY CHECKER - Command Line Version")
    print("=" * 60)
    
    while True:
        print("\nOptions:")
        print("1. Check password strength")
        print("2. Generate strong password")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            password = input("Enter password to check: ")
            analysis = checker.calculate_strength(password)
            
            print("\n" + "=" * 60)
            print("PASSWORD ANALYSIS RESULTS")
            print("=" * 60)
            print(f"\nStrength: {analysis['strength']}")
            print(f"Score: {analysis['score']}/{analysis['max_score']}")
            print(f"Entropy: {analysis['entropy']:.1f} bits")
            
            print("\nDetailed Analysis:")
            for detail in analysis['details']:
                print(f"  {detail}")
            
            if analysis['suggestions']:
                print("\nSuggestions:")
                for suggestion in analysis['suggestions']:
                    print(f"  • {suggestion}")
        
        elif choice == '2':
            import random
            import string
            
            lowercase = string.ascii_lowercase
            uppercase = string.ascii_uppercase
            digits = string.digits
            special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            
            password_chars = [
                random.choice(lowercase), random.choice(lowercase),
                random.choice(uppercase), random.choice(uppercase),
                random.choice(digits), random.choice(digits),
                random.choice(special), random.choice(special)
            ]
            
            all_chars = lowercase + uppercase + digits + special
            for _ in range(8):
                password_chars.append(random.choice(all_chars))
            
            random.shuffle(password_chars)
            password = ''.join(password_chars)
            
            print(f"\nGenerated Strong Password: {password}")
            print("\n⚠️  Save this password securely!")
        
        elif choice == '3':
            print("\n👋 Goodbye! Stay secure!")
            break
        
        else:
            print("Invalid choice. Please try again.")

def main():
    """Main function to run the application"""
    import sys
    
    print("=" * 60)
    print("🔐 PASSWORD COMPLEXITY CHECKER")
    print("=" * 60)
    print("\nChoose interface:")
    print("1. Graphical User Interface (GUI)")
    print("2. Command Line Interface (CLI)")
    
    choice = input("\nEnter choice (1-2): ").strip()
    
    if choice == '1':
        try:
            root = tk.Tk()
            
            # Configure ttk style for progress bar
            style = ttk.Style()
            style.theme_use('clam')
            style.configure("green.Horizontal.TProgressbar", 
                          background='#2ecc71',
                          troughcolor='#2d2d2d',
                          bordercolor='#1e1e1e',
                          lightcolor='#2ecc71',
                          darkcolor='#27ae60')
            
            app = PasswordCheckerGUI(root)
            root.mainloop()
        except Exception as e:
            print(f"Error starting GUI: {e}")
            print("Falling back to CLI version...")
            command_line_version()
    elif choice == '2':
        command_line_version()
    else:
        print("Invalid choice. Running CLI version...")
        command_line_version()

if __name__ == "__main__":
    main()
