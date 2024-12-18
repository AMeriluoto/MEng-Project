import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import spatializer

def process_file(file_path):
    """
    Function to process the selected file.
    Replace this with your custom logic.
    """
    # Example: Just print the file path for now
    print(f"Processing file: {file_path}")
    spatializer.spatialize_over_time(file_path, "output.wav", spatializer.circular_orbit)
    messagebox.showinfo("File Processed", f"File processed successfully:\n{file_path}")

def select_file():
    """
    Opens a file dialog for the user to select a file and validates it as a .wav file.
    """
    file_path = filedialog.askopenfilename(title="Select a file", filetypes=[("WAV files", "*.wav")])
    if file_path:
        # Check if the file has a .wav extension
        if os.path.splitext(file_path)[1].lower() == ".wav":
            process_file(file_path)
        else:
            messagebox.showerror("Invalid File", "Please select a .wav file.")
    else:
        messagebox.showwarning("No File Selected", "Please select a file to process.")

def create_gui():
    """
    Creates the GUI for file selection and processing.
    """
    # Create the main window
    root = tk.Tk()
    root.title("File Selector")
    root.geometry("300x150")

    # Create and place a button for file selection
    select_button = tk.Button(root, text="Select File", command=select_file, width=20)
    select_button.pack(pady=20)

    # Create and place an exit button
    exit_button = tk.Button(root, text="Exit", command=root.quit, width=20)
    exit_button.pack(pady=10)

    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    create_gui()
