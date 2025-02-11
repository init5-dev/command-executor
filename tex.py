#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import os
import sys

# Asegúrate de que la variable TERM esté configurada
if 'TERM' not in os.environ:
    os.environ['TERM'] = 'xterm'

# Función para cargar los comandos desde el archivo commands.cfg
def load_commands():
    try:
        with open("commands.cfg", "r") as file:
            commands = []
            for line in file:
                line = line.strip()
                if line and "::" in line:  # Verificar que la línea tenga el separador ::
                    name, cmd = line.split("::", 1)  # Separar nombre y comando
                    commands.append((name.strip(), cmd.strip()))
                elif line:  # Si la línea no tiene el formato correcto, mostrar una advertencia
                    messagebox.showwarning("Advertencia", f"Línea mal formada ignorada: {line}")
        return commands
    except FileNotFoundError:
        messagebox.showinfo("Información", "El archivo commands.cfg no existe.")
        return []

# Función para guardar los comandos en el archivo commands.cfg
def save_commands(commands):
    try:
        with open("commands.cfg", "w") as file:
            for name, cmd in commands:
                file.write(f"{name}::{cmd}\n")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el archivo commands.cfg: {e}")

# Función para ejecutar un comando en la terminal
def run_command(command):
    global process
    try:
        # Forzar el modo no búferizado usando stdbuf (si está disponible)
        if sys.platform.startswith("linux"):
            command = f"stdbuf -oL -eL {command}"
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Forzar el modo no búferizado
        )
        # Leer la salida en tiempo real
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                terminal_output.insert(tk.END, output)
                terminal_output.see(tk.END)  # Auto-scroll al final
        # Capturar cualquier salida restante después de que el proceso termine
        remaining_output, _ = process.communicate()
        if remaining_output:
            terminal_output.insert(tk.END, remaining_output)
        process = None
    except Exception as e:
        messagebox.showerror("Error", f"Error al ejecutar el comando: {e}")

# Función para manejar la selección de un comando (doble clic)
def on_double_click(command):
    terminal_output.delete(1.0, tk.END)  # Limpiar la salida anterior
    threading.Thread(target=run_command, args=(command,), daemon=True).start()

# Función para cancelar la ejecución del comando
def cancel_command():
    global process
    if process:
        process.terminate()
        terminal_output.insert(tk.END, "\nEjecución cancelada por el usuario.\n")
        process = None

# Función para limpiar la terminal
def clear_terminal():
    terminal_output.delete(1.0, tk.END)

# Función para copiar un comando al portapapeles
def copy_to_clipboard(command):
    root.clipboard_clear()
    root.clipboard_append(command)
    root.update()  # Actualizar el portapapeles
    messagebox.showinfo("Información", "Comando copiado al portapapeles.")

# Clase para implementar tooltips
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="lightyellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# Diálogo personalizado para editar o añadir comandos
class CommandDialog:
    def __init__(self, parent, title, initial_name="", initial_cmd=""):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x300")  # Tamaño amplio para comandos largos
        self.dialog.resizable(True, True)

        # Etiqueta para el nombre
        tk.Label(self.dialog, text="Nombre:", font=("Arial", 10)).pack(pady=5)
        self.name_entry = tk.Entry(self.dialog, font=("Arial", 10), width=50)
        self.name_entry.insert(0, initial_name)
        self.name_entry.pack(padx=10, pady=5)

        # Etiqueta para el comando
        tk.Label(self.dialog, text="Comando:", font=("Arial", 10)).pack(pady=5)
        self.cmd_text = tk.Text(self.dialog, wrap=tk.WORD, width=70, height=10, font=("Courier", 10))
        self.cmd_text.insert(tk.END, initial_cmd)
        self.cmd_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Botones
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=10)
        ok_button = tk.Button(button_frame, text="Aceptar", command=self.on_ok, font=("Arial", 10))
        ok_button.pack(side=tk.LEFT, padx=10)
        cancel_button = tk.Button(button_frame, text="Cancelar", command=self.on_cancel, font=("Arial", 10))
        cancel_button.pack(side=tk.RIGHT, padx=10)

        # Enfocar el área de texto
        self.name_entry.focus_set()

        # Esperar a que el diálogo se cierre
        self.dialog.transient(parent)
        self.dialog.grab_set()
        parent.wait_window(self.dialog)

    def on_ok(self):
        name = self.name_entry.get().strip()
        cmd = self.cmd_text.get(1.0, tk.END).strip()
        if not name or not cmd:
            messagebox.showerror("Error", "El nombre y el comando no pueden estar vacíos.")
            return
        self.result = (name, cmd)
        self.dialog.destroy()

    def on_cancel(self):
        self.result = None
        self.dialog.destroy()

# Función para eliminar un comando
def delete_command(index, name, cmd):
    confirm = messagebox.askyesno("Confirmar eliminación", f"¿Estás seguro de que deseas eliminar el comando '{name}'?")
    if confirm:
        commands.pop(index)
        save_commands(commands)
        refresh_command_list()

# Función para editar un comando
def edit_command(index, name, cmd):
    dialog = CommandDialog(root, "Editar Comando", initial_name=name, initial_cmd=cmd)
    if dialog.result is not None:
        commands[index] = dialog.result
        save_commands(commands)
        refresh_command_list()

# Función para añadir un comando
def add_command():
    dialog = CommandDialog(root, "Añadir Comando")
    if dialog.result is not None:
        commands.append(dialog.result)
        save_commands(commands)
        refresh_command_list()

# Función para mover un comando hacia arriba
def move_up(index):
    if index > 0:
        commands[index], commands[index - 1] = commands[index - 1], commands[index]
        save_commands(commands)
        refresh_command_list()

# Función para mover un comando hacia abajo
def move_down(index):
    if index < len(commands) - 1:
        commands[index], commands[index + 1] = commands[index + 1], commands[index]
        save_commands(commands)
        refresh_command_list()

# Función para refrescar la lista de comandos
def refresh_command_list():
    for widget in inner_frame.winfo_children():
        widget.destroy()
    for i, (name, cmd) in enumerate(commands):
        create_command_row(i, name, cmd)

# Función para obtener la ruta correcta de los recursos
def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, funciona tanto en desarrollo como en el ejecutable."""
    try:
        # PyInstaller crea un directorio temporal y almacena los recursos en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Función para crear una fila de comando
def create_command_row(index, name, cmd):
    row_frame = tk.Frame(inner_frame, bg="white")
    row_frame.grid(row=index, column=0, sticky="w", padx=5, pady=2)

    # Cargar imágenes para los íconos
    up_icon = tk.PhotoImage(file=resource_path("icons/up.png"))
    down_icon = tk.PhotoImage(file=resource_path("icons/down.png"))
    edit_icon = tk.PhotoImage(file=resource_path("icons/edit.png"))  # Ícono de edición
    delete_icon = tk.PhotoImage(file=resource_path("icons/delete.png"))  # Ícono de eliminación
    copy_icon = tk.PhotoImage(file=resource_path("icons/copy.png"))  # Ícono de copia

    # Botón "<" para mover hacia arriba
    up_button = tk.Button(row_frame, image=up_icon, relief="flat",
                          command=lambda i=index: move_up(i))
    up_button.image = up_icon
    up_button.pack(side=tk.LEFT, padx=0)


    # Botón ">" para mover hacia abajo
    down_button = tk.Button(row_frame, image=down_icon, font=("Arial", 10), relief="flat",
                            command=lambda i=index: move_down(i))
    down_button.image = down_icon
    down_button.pack(side=tk.LEFT, padx=0)

    # Botón Editar con ícono
    edit_button = tk.Button(row_frame, image=edit_icon, relief="flat",
                            command=lambda i=index, n=name, c=cmd: edit_command(i, n, c))
    edit_button.image = edit_icon  # Mantener una referencia para evitar que la imagen sea eliminada por el recolector de basura
    edit_button.pack(side=tk.LEFT, padx=0)

    # Botón Copiar con ícono
    copy_button = tk.Button(row_frame, image=copy_icon, relief="flat",
                            command=lambda c=cmd: copy_to_clipboard(c))
    copy_button.image = copy_icon  # Mantener una referencia
    copy_button.pack(side=tk.LEFT, padx=0)

    # Botón Eliminar con ícono
    delete_button = tk.Button(row_frame, image=delete_icon, relief="flat",
                              command=lambda i=index, n=name, c=cmd: delete_command(i, n, c))
    delete_button.image = delete_icon  # Mantener una referencia
    delete_button.pack(side=tk.LEFT, padx=0)

    # Label para mostrar el nombre del comando
    label = tk.Label(row_frame, text=name, font=("Arial", 10), width=60, anchor="w", cursor="hand2",
                     bg="white", fg="black", relief="flat", padx=5, pady=3)
    label.pack(side=tk.LEFT, padx=0)

    # Tooltip para mostrar el comando completo
    ToolTip(label, cmd)

    # Efecto de botón al hacer clic
    def on_label_click(event, lbl=label):
        lbl.config(bg="lightblue", relief="raised")

    def on_label_release(event, lbl=label, c=cmd):
        lbl.config(bg="white", relief="flat")
        on_double_click(c)

    label.bind("<ButtonPress-1>", on_label_click)
    label.bind("<ButtonRelease-1>", on_label_release)

# Crear la ventana principal
root = tk.Tk()
root.title("Tex")
root.geometry("1000x600")

# Panel izquierdo: Lista de comandos con scroll horizontal
left_frame = tk.Frame(root, width=400, height=600, bg="lightgray")
left_frame.pack(side=tk.LEFT, fill=tk.Y)

label_commands = tk.Label(left_frame, text="Comandos disponibles", font=("Arial", 12), bg="lightgray")
label_commands.pack(pady=10)

# Canvas para el scroll horizontal
canvas = tk.Canvas(left_frame, bg="white", width=400, height=400)
canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Scrollbar horizontal
h_scrollbar = tk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=canvas.xview)
h_scrollbar.pack(fill=tk.X)

# Configurar el canvas para usar el scrollbar
canvas.configure(xscrollcommand=h_scrollbar.set)

# Frame interno dentro del canvas para contener la lista
inner_frame = tk.Frame(canvas, bg="white")
canvas.create_window((0, 0), window=inner_frame, anchor="nw")

# Ajustar el scroll cuando cambia el tamaño del contenido
def update_scroll_region(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

inner_frame.bind("<Configure>", update_scroll_region)

# Cargar los comandos iniciales
commands = load_commands()

# Crear las filas de comandos
for i, (name, cmd) in enumerate(commands):
    create_command_row(i, name, cmd)

# Botón para añadir un comando
add_button = tk.Button(left_frame, text="Añadir Comando", font=("Arial", 10), command=add_command)
add_button.pack(pady=10)

# Panel derecho: Ventana de terminal
right_frame = tk.Frame(root, width=600, height=600)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Configuración de la terminal con estilo de terminal real
terminal_output = tk.Text(right_frame, wrap=tk.WORD, font=("Courier", 10), bg="black", fg="white", insertbackground="white")
terminal_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Botones debajo de la terminal
button_frame = tk.Frame(right_frame)
button_frame.pack(fill=tk.X, pady=10)

cancel_button = tk.Button(button_frame, text="Cancelar Ejecución", command=cancel_command, font=("Arial", 10))
cancel_button.pack(side=tk.LEFT, padx=10)

clear_button = tk.Button(button_frame, text="Limpiar Terminal", command=clear_terminal, font=("Arial", 10))
clear_button.pack(side=tk.RIGHT, padx=10)

# Variable global para el proceso
process = None

# Iniciar la aplicación
root.mainloop()