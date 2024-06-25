import tkinter as tk
from tkinter import filedialog, messagebox
from flask import Flask, send_from_directory
import threading
import os


class ZWebGLRunner:
    def __init__(self, root):
        self.root = root
        self.root.title("ZWebGLRunner")
        self.file_path = None

        self.label = tk.Label(root, text="Select index.html file for Flask endpoint")
        self.label.pack(pady=10)

        self.select_button = tk.Button(root, text="Select File", command=self.select_file)
        self.select_button.pack(pady=5)

        self.run_button = tk.Button(root, text="Run Flask Server", command=self.run_server, state=tk.DISABLED)
        self.run_button.pack(pady=5)

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("HTML files", "*.html")])
        if self.file_path:
            self.run_button.config(state=tk.NORMAL)
            messagebox.showinfo("Selected File", f"Selected file: {self.file_path}")

    def run_server(self):
        if self.file_path:
            threading.Thread(target=self.start_flask_server, daemon=True).start()
            messagebox.showinfo("Server Running", "Flask server is running...")

    def start_flask_server(self):
        app = Flask(__name__)

        @app.route('/')
        def serve_index():
            directory = os.path.dirname(self.file_path)
            return send_from_directory(directory, 'index.html')

        @app.route('/<path:filename>')
        def serve_static(filename):
            directory = os.path.dirname(self.file_path)
            return send_from_directory(directory, filename)

        app.run(host="0.0.0.0", port=50000)


if __name__ == '__main__':
    root = tk.Tk()
    app = ZWebGLRunner(root)
    root.mainloop()
