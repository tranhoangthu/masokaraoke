import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

def repack_files(output_filename):
    # Get all .pop files in the current directory
    pop_files = [f for f in os.listdir() if re.match(r'\d+_[0-9a-fA-F]{8}\.pop', f)]
    
    if not pop_files:
        messagebox.showerror("Error", "No .pop files found in the current directory.")
        return

    # Sort files by their numeric prefix
    pop_files.sort(key=lambda x: int(x.split('_')[0]))

    try:
        with open(output_filename, 'wb') as output_file:
            for pop_file in pop_files:
                with open(pop_file, 'rb') as file:
                    data = file.read()
                    output_file.write(data)

        messagebox.showinfo("Success", f"Files successfully repacked into {output_filename}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while repacking: {e}")

def select_output_file():
    output_filename = filedialog.asksaveasfilename(defaultextension=".megmid", filetypes=[("MEGMID files", "*.megmid"), ("All files", "*.*")])
    if output_filename:
        repack_files(output_filename)

def create_gui():
    root = tk.Tk()
    root.title("MEGMID Repack Tool")

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(padx=10, pady=10)

    label = tk.Label(frame, text="Repack extracted .pop files into a MEGMID archive")
    label.pack(pady=10)

    button = tk.Button(frame, text="Select Output File and Repack", command=select_output_file)
    button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()