import os
from tkinter import messagebox

def load_commands():
    try:
        with open("commands.cfg", "r") as file:
            commands = []
            for line in file:
                line = line.strip()
                if line and "::" in line:
                    name, cmd = line.split("::", 1)
                    commands.append((name.strip(), cmd.strip()))
                elif line:
                    messagebox.showwarning("Advertencia", f"Línea mal formada ignorada: {line}")
            return commands
    except FileNotFoundError:
        messagebox.showinfo("Información", "El archivo commands.cfg no existe.")
        return []

def save_commands(commands):
    try:
        with open("commands.cfg", "w") as file:
            for name, cmd in commands:
                file.write(f"{name}::{cmd}\n")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")