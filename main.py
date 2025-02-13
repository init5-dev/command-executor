#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
from config_handlers import load_commands
import command_handlers as handlers

# Asegúrate de que la variable TERM esté configurada
if 'TERM' not in os.environ:
    os.environ['TERM'] = 'xterm'

def main():
    # Configurar ventana principal
    root = tk.Tk()
    root.title("Terminal Manager")
    root.geometry("1000x600")
    
    # Configurar paneles principales
    left_frame = tk.Frame(root, width=400, bg="lightgray")
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    right_frame = tk.Frame(root, width=600)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    # Configurar terminal
    terminal = tk.Text(right_frame, wrap=tk.WORD, font=("Courier", 10), 
                      bg="black", fg="white", insertbackground="white")
    terminal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Botones de control de terminal
    button_frame = tk.Frame(right_frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    tk.Button(button_frame, text="Cancelar", command=handlers.cancel_command).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Limpiar", command=handlers.clear_terminal).pack(side=tk.RIGHT, padx=10)
    
    # Configurar lista de comandos
    canvas = tk.Canvas(left_frame, bg="white")
    scroll_v = tk.Scrollbar(left_frame, orient=tk.VERTICAL, command=canvas.yview)
    scroll_h = tk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=canvas.xview)
    inner_frame = tk.Frame(canvas, bg="white")
    
    canvas.configure(yscrollcommand=scroll_v.set, xscrollcommand=scroll_h.set)
    canvas.create_window((0,0), window=inner_frame, anchor="nw")
    
    # Empaquetado de elementos
    scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
    scroll_h.pack(side=tk.BOTTOM, fill=tk.X)
    canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    tk.Button(left_frame, text="Añadir Comando", command=handlers.add_command).pack(pady=10)
    
    inner_frame.bind("<Configure>", lambda e: canvas.configure(
        scrollregion=canvas.bbox("all"))
    )
    
    # Inicializar componentes
    handlers.set_components(root, terminal, inner_frame)
    handlers.commands = load_commands()
    handlers.refresh_command_list()
    
    root.mainloop()

if __name__ == "__main__":
    main()