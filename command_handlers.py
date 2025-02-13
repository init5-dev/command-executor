import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import os
import sys
from config_handlers import save_commands
from tooltip import ToolTip
from command_dialog import CommandDialog

# Variables globales
root = None
terminal_output = None
inner_frame = None
commands = []
process = None
GLOBAL_ICONS = {}

def set_components(main_root, terminal, frame):
    global root, terminal_output, inner_frame
    root = main_root
    terminal_output = terminal
    inner_frame = frame

def run_command(command):
    global process
    terminal_output.delete(1.0, tk.END)
    try:
        if sys.platform.startswith("linux"):
            command = f"stdbuf -oL -eL {command}"
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        threading.Thread(target=read_output, daemon=True).start()
    except Exception as e:
        messagebox.showerror("Error", f"Error al ejecutar: {e}")

def read_output():
    global process
    while True:
        if process.stdout:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                terminal_output.insert(tk.END, output)
                terminal_output.see(tk.END)
    process = None

def cancel_command():
    global process
    if process:
        process.terminate()
        terminal_output.insert(tk.END, "\nComando cancelado\n")
        process = None

def clear_terminal():
    terminal_output.delete(1.0, tk.END)

def copy_to_clipboard(command):
    root.clipboard_clear()
    root.clipboard_append(command)
    messagebox.showinfo("Info", "Comando copiado")

def delete_command(index, name, cmd):
    if messagebox.askyesno("Confirmar", f"¿Eliminar {name}?"):
        commands.pop(index)
        save_commands(commands)
        refresh_command_list()

def edit_command(index, name, cmd):
    dialog = CommandDialog(root, "Editar Comando", name, cmd)
    if dialog.result:
        commands[index] = dialog.result
        save_commands(commands)
        refresh_command_list()

def add_command():
    dialog = CommandDialog(root, "Nuevo Comando")
    if dialog.result:
        commands.append(dialog.result)
        save_commands(commands)
        refresh_command_list()

def move_up(index):
    if index > 0:
        commands[index], commands[index-1] = commands[index-1], commands[index]
        save_commands(commands)
        refresh_command_list()

def move_down(index):
    if index < len(commands)-1:
        commands[index], commands[index+1] = commands[index+1], commands[index]
        save_commands(commands)
        refresh_command_list()

def refresh_command_list():
    for widget in inner_frame.winfo_children():
        widget.destroy()
    for i, (name, cmd) in enumerate(commands):
        create_command_row(i, name, cmd)

def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, funciona en desarrollo y en el ejecutable."""
    try:
        # PyInstaller crea un directorio temporal y almacena los recursos en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    full_path = os.path.join(base_path, relative_path)
    return full_path

def create_command_row(index, name, cmd):
    row_frame = tk.Frame(inner_frame, bg="white")
    row_frame.grid(row=index, column=0, sticky="w", padx=5, pady=2)

    # Cargar íconos (con caché global)
    icon_names = ['up', 'down', 'edit', 'delete', 'copy']
    for icon_name in icon_names:
        if icon_name not in GLOBAL_ICONS:
            try:
                GLOBAL_ICONS[icon_name] = tk.PhotoImage(
                    file=resource_path(f"icons/{icon_name}.png")
                )
            except Exception as e:
                print(f"Error cargando ícono {icon_name}: {e}")
                return

    # Botones con íconos (usar referencias globales)

    tk.Button(row_frame, image=GLOBAL_ICONS['up'], command=lambda i=index: move_up(i)).pack(side=tk.LEFT)
    tk.Button(row_frame, image=GLOBAL_ICONS['down'], command=lambda i=index: move_down(i)).pack(side=tk.LEFT)
    tk.Button(row_frame, image=GLOBAL_ICONS['edit'], command=lambda i=index: edit_command(i, name, cmd)).pack(side=tk.LEFT)
    tk.Button(row_frame, image=GLOBAL_ICONS['copy'], command=lambda c=cmd: copy_to_clipboard(c)).pack(side=tk.LEFT)
    tk.Button(row_frame, image=GLOBAL_ICONS['delete'], command=lambda i=index: delete_command(i, name, cmd)).pack(side=tk.LEFT)

    label = tk.Label(row_frame, text=name, font=("Arial", 10), width=50, anchor="w", 
                    bg="white", cursor="hand2")
    label.pack(side=tk.LEFT, padx=5)
    
    ToolTip(label, cmd)
    
    label.bind("<Button-1>", lambda e, c=cmd: run_command(c))