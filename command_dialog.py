import tkinter as tk
from tkinter import messagebox

class CommandDialog:
    def __init__(self, parent, title, initial_name="", initial_cmd=""):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x300")
        
        tk.Label(self.dialog, text="Nombre:").pack()
        self.name_entry = tk.Entry(self.dialog, width=50)
        self.name_entry.insert(0, initial_name)
        self.name_entry.pack()
        
        tk.Label(self.dialog, text="Comando:").pack()
        self.cmd_text = tk.Text(self.dialog, wrap=tk.WORD, width=70, height=10)
        self.cmd_text.insert(tk.END, initial_cmd)
        self.cmd_text.pack()
        
        tk.Button(self.dialog, text="Aceptar", command=self.on_ok).pack(side=tk.LEFT)
        tk.Button(self.dialog, text="Cancelar", command=self.on_cancel).pack(side=tk.RIGHT)
        
        self.dialog.grab_set()
        parent.wait_window(self.dialog)

    def on_ok(self):
        name = self.name_entry.get().strip()
        cmd = self.cmd_text.get("1.0", tk.END).strip()
        if name and cmd:
            self.result = (name, cmd)
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Campos requeridos")

    def on_cancel(self):
        self.dialog.destroy()