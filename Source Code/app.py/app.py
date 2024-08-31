import tkinter as tk
from tkinter import ttk
import sqlite3

class TodoList:
    def __init__(self, master):
        self.master = master
        self.items = []  # List to keep track of items

        # Create database connection and table
        self.conn = sqlite3.connect('todolist.db')
        self.cursor = self.conn.cursor()
        self.create_table()

        # Create a canvas and a scrollbar
        self.canvas = tk.Canvas(master, bg='#1E1E1E', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=3, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas
        self.items_frame = tk.Frame(self.canvas, bg='#1E1E1E')
        self.canvas.create_window((0, 0), window=self.items_frame, anchor="nw")

        # Place canvas on the grid
        self.canvas.grid(row=3, column=0, columnspan=1, sticky="nsew", padx=20, pady=20)
        self.items_frame.bind("<Configure>", self.on_frame_configure)

        self.master.bind_all("<MouseWheel>", self._on_mousewheel)  # Bind mouse wheel

        # Load items after initialization
        self.load_items()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                               id INTEGER PRIMARY KEY,
                               text TEXT NOT NULL)''')
        self.conn.commit()

    def load_items(self):
        self.cursor.execute('SELECT id, text FROM tasks')
        items = self.cursor.fetchall()
        for item_id, text in items:
            self.items.append((item_id, text))
        self.refresh_ui()

    def add_item(self, entry_text):
        if entry_text.strip():
            self.cursor.execute('INSERT INTO tasks (text) VALUES (?)', (entry_text,))
            self.conn.commit()
            item_id = self.cursor.lastrowid
            self.items.append((item_id, entry_text))
            self.refresh_ui()
            main_entry.delete(0, tk.END)

    def add_item_to_ui(self, entry_text, item_id, index):
        item_frame = tk.Frame(self.items_frame, bg='#2C2C2C', padx=10, pady=5)
        item_frame.grid(sticky="ew", padx=5, pady=5)
        item_frame.grid_columnconfigure(1, weight=1)

        number_label = tk.Label(item_frame, text=f"{index + 1}.", font=("Helvetica", 16), bg='#2C2C2C',
                                fg='#4CAF50')
        number_label.grid(row=0, column=0, padx=(0, 10))

        text_label = tk.Label(item_frame, text=entry_text, font=("Helvetica", 16), bg='#2C2C2C', fg='white',
                              anchor="w")
        text_label.grid(row=0, column=1, sticky="ew")

        delete_button = ttk.Button(item_frame, text="X", width=3,
                                   command=lambda: self.delete_item(item_id))
        delete_button.grid(row=0, column=2, padx=(10, 0))

    def delete_item(self, item_id):
        self.cursor.execute('DELETE FROM tasks WHERE id = ?', (item_id,))
        self.conn.commit()
        self.items = [item for item in self.items if item[0] != item_id]
        self.refresh_ui()

    def refresh_ui(self):
        for child in self.items_frame.winfo_children():
            child.destroy()
        for index, (item_id, text) in enumerate(self.items):
            self.add_item_to_ui(text, item_id, index)

    def clear_all_items(self):
        self.cursor.execute('DELETE FROM tasks')
        self.conn.commit()
        self.items.clear()
        self.refresh_ui()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def __del__(self):
        self.conn.close()

def add_button_press():
    todo_list.add_item(main_entry.get())

def on_enter_key(event):
    todo_list.add_item(main_entry.get())

def set_resolution():
    main.geometry("800x600")
    main.resizable(False, False)

main = tk.Tk()
main.title("To Do List")
set_resolution()
main.config(bg='#1E1E1E')

style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', font=('Helvetica', 14), background='#4CAF50', foreground='white')
style.map('TButton', background=[('active', '#45a049')])

header_frame = tk.Frame(main, bg='#1E1E1E', pady=20)
header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
header_frame.grid_columnconfigure(0, weight=1)

todolist = tk.Label(header_frame, text="To Do List", font=("Helvetica", 36, "bold"), bg='#1E1E1E', fg='#4CAF50')
todolist.grid()

input_frame = tk.Frame(main, bg='#1E1E1E', pady=20)
input_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20)
input_frame.grid_columnconfigure(0, weight=1)

main_entry = tk.Entry(input_frame, font=("Helvetica", 18), bg='#2C2C2C', fg='white', insertbackground='white',
                      insertwidth=2)
main_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
main_entry.focus()
main_entry.bind('<Return>', on_enter_key)

add_button = ttk.Button(input_frame, text="Add Task", command=add_button_press, style='TButton')
add_button.grid(row=0, column=1)

# Add a "CLEAR ALL" button
clear_all_button = ttk.Button(main, text="CLEAR ALL", command=lambda: todo_list.clear_all_items(), style='TButton')
clear_all_button.grid(row=2, column=0, columnspan=2, pady=10)

todo_list = TodoList(main)

main.grid_rowconfigure(3, weight=1)
main.grid_columnconfigure(0, weight=1)

main.mainloop()