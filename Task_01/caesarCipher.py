def caesar_cipher(text, shift, mode='encrypt'):
    """
    Perform Caesar cipher encryption or decryption on the given text.
    
    Args:
        text (str): The input text to process
        shift (int): The shift value for the cipher
        mode (str): Either 'encrypt' or 'decrypt'
    
    Returns:
        str: The processed text
    """
    result = ""
    
    # For decryption, we use the negative shift
    if mode == 'decrypt':
        shift = -shift
    
    # Process each character in the text
    for char in text:
        # Check if character is uppercase
        if char.isupper():
            # Convert to ASCII value, apply shift, and convert back to character
            shifted_char = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            result += shifted_char
        
        # Check if character is lowercase
        elif char.islower():
            shifted_char = chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
            result += shifted_char
        
        # If character is not a letter, leave it unchanged
        else:
            result += char
    
    return result


def main():
    """Main program loop with user interface."""
    print("=" * 50)
    print("CAESAR CIPHER PROGRAM")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Encrypt a message")
        print("2. Decrypt a message")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1/2/3): ").strip()
        
        if choice == '1':
            # Encryption mode
            message = input("Enter the message to encrypt: ")
            
            # Validate shift value
            while True:
                try:
                    shift = int(input("Enter shift value (1-25): "))
                    if 1 <= shift <= 25:
                        break
                    else:
                        print("Shift value must be between 1 and 25. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number between 1 and 25.")
            
            encrypted = caesar_cipher(message, shift, 'encrypt')
            print(f"\nOriginal message: {message}")
            print(f"Encrypted message: {encrypted}")
        
        elif choice == '2':
            # Decryption mode
            message = input("Enter the message to decrypt: ")
            
            # Validate shift value
            while True:
                try:
                    shift = int(input("Enter shift value (1-25): "))
                    if 1 <= shift <= 25:
                        break
                    else:
                        print("Shift value must be between 1 and 25. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number between 1 and 25.")
            
            decrypted = caesar_cipher(message, shift, 'decrypt')
            print(f"\nEncrypted message: {message}")
            print(f"Decrypted message: {decrypted}")
        
        elif choice == '3':
            print("\nThank you for using the Caesar Cipher program!")
            break
        
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def caesar_cipher_advanced(text, shift, mode='encrypt'):
    """
    Advanced version that handles negative shifts and larger shift values.
    Also provides brute-force decryption capability.
    """
    # Normalize shift to 0-25 range
    shift = shift % 26
    
    if mode == 'decrypt':
        shift = -shift
    
    result = ""
    
    for char in text:
        if char.isupper():
            shifted_char = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            result += shifted_char
        elif char.islower():
            shifted_char = chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
            result += shifted_char
        else:
            result += char
    
    return result


def brute_force_decrypt(encrypted_text):
    """
    Attempt to decrypt by trying all possible shift values (0-25).
    Useful when the shift value is unknown.
    """
    print("\n" + "=" * 50)
    print("BRUTE FORCE DECRYPTION RESULTS")
    print("=" * 50)
    
    for shift in range(26):
        decrypted = caesar_cipher_advanced(encrypted_text, shift, 'decrypt')
        print(f"Shift {shift:2d}: {decrypted}")


if __name__ == "__main__":
    # Run the main program
    main()
    
    # Optional: Example of using the advanced features
    print("\n" + "=" * 50)
    print("ADDITIONAL EXAMPLES")
    print("=" * 50)
    
    # Example 1: Encryption and decryption with the advanced function
    original = "Hello, World!"
    shift = 3
    
    encrypted = caesar_cipher_advanced(original, shift, 'encrypt')
    decrypted = caesar_cipher_advanced(encrypted, shift, 'decrypt')
    
    print(f"\nOriginal: {original}")
    print(f"Encrypted (shift={shift}): {encrypted}")
    print(f"Decrypted: {decrypted}")
    
    # Example 2: Brute force demonstration with a sample encrypted text
    sample_encrypted = "Khoor, Zruog!"  # This is "Hello, World!" with shift=3
    print(f"\nAttempting to brute force decrypt: '{sample_encrypted}'")
    brute_force_decrypt(sample_encrypted)
