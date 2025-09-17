import tkinter as tk
from tkinter import filedialog, messagebox
import os

class DarkNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title('Dark Notepad')
        self.root.geometry('900x650')
        self.root.minsize(400, 300)
        self.current_file = None
        self.create_widgets()
        self.apply_dark_theme()

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill='both')
        
        # Text area with scrollbars
        text_frame = tk.Frame(main_frame)
        text_frame.pack(expand=True, fill='both', padx=2, pady=2)
        
        self.text_area = tk.Text(
            text_frame,
            wrap='word',
            undo=True,
            font=('Consolas', 11),
            padx=10,
            pady=10
        )
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(text_frame, command=self.text_area.yview)
        h_scrollbar = tk.Scrollbar(text_frame, orient='horizontal', command=self.text_area.xview)
        
        self.text_area.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and text area
        self.text_area.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Menu bar
        self.create_menu()
        self.bind_shortcuts()

    def create_menu(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='New', command=self.new_file, accelerator='Ctrl+N')
        file_menu.add_command(label='Open...', command=self.open_file, accelerator='Ctrl+O')
        file_menu.add_separator()
        file_menu.add_command(label='Save', command=self.save_file, accelerator='Ctrl+S')
        file_menu.add_command(label='Save As...', command=self.save_as_file, accelerator='Ctrl+Shift+S')
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.exit_app, accelerator='Alt+F4')
        
        # Edit menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='Edit', menu=edit_menu)
        edit_menu.add_command(label='Undo', command=self.undo, accelerator='Ctrl+Z')
        edit_menu.add_command(label='Redo', command=self.redo, accelerator='Ctrl+Y')
        edit_menu.add_separator()
        edit_menu.add_command(label='Cut', command=self.cut, accelerator='Ctrl+X')
        edit_menu.add_command(label='Copy', command=self.copy, accelerator='Ctrl+C')
        edit_menu.add_command(label='Paste', command=self.paste, accelerator='Ctrl+V')
        edit_menu.add_separator()
        edit_menu.add_command(label='Select All', command=self.select_all, accelerator='Ctrl+A')

    def bind_shortcuts(self):
        shortcuts = {
            '<Control-n>': lambda e: self.new_file(),
            '<Control-o>': lambda e: self.open_file(),
            '<Control-s>': lambda e: self.save_file(),
            '<Control-Shift-S>': lambda e: self.save_as_file(),
            '<Control-z>': lambda e: self.undo(),
            '<Control-y>': lambda e: self.redo(),
            '<Control-a>': lambda e: self.select_all(),
            '<Alt-F4>': lambda e: self.exit_app()
        }
        
        for key, command in shortcuts.items():
            self.root.bind(key, command)

    def apply_dark_theme(self):
        colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'select_bg': '#0078d4',
            'select_fg': '#ffffff',
            'menu_bg': '#2d2d2d',
            'menu_fg': '#ffffff',
            'cursor': '#ffffff'
        }
        
        self.text_area.config(
            bg=colors['bg'],
            fg=colors['fg'],
            insertbackground=colors['cursor'],
            selectbackground=colors['select_bg'],
            selectforeground=colors['select_fg'],
            relief='flat',
            borderwidth=0
        )
        
        self.root.config(bg=colors['bg'])
        
        self.menu_bar.config(
            bg=colors['menu_bg'],
            fg=colors['menu_fg'],
            activebackground=colors['select_bg'],
            activeforeground=colors['select_fg']
        )

    def new_file(self):
        if self.text_area.get(1.0, tk.END).strip():
            if messagebox.askyesno('New File', 'Do you want to save changes?'):
                self.save_file()
        
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.root.title('Dark Notepad - Untitled')

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title='Open Text File',
            defaultextension='.txt',
            filetypes=[
                ('Text Files', '*.txt'),
                ('All Files', '*.*')
            ]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, content)
                self.current_file = file_path
                self.root.title(f'Dark Notepad - {os.path.basename(file_path)}')
            except Exception as e:
                messagebox.showerror('Error', f'Could not open file:\n{str(e)}')

    def save_file(self):
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END + '-1c')
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.root.title(f'Dark Notepad - {os.path.basename(self.current_file)}')
                return True
            except Exception as e:
                messagebox.showerror('Error', f'Could not save file:\n{str(e)}')
                return False
        else:
            return self.save_as_file()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            title='Save Text File',
            defaultextension='.txt',
            filetypes=[
                ('Text Files', '*.txt'),
                ('All Files', '*.*')
            ]
        )
        if file_path:
            try:
                content = self.text_area.get(1.0, tk.END + '-1c')
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.current_file = file_path
                self.root.title(f'Dark Notepad - {os.path.basename(file_path)}')
                return True
            except Exception as e:
                messagebox.showerror('Error', f'Could not save file:\n{str(e)}')
                return False
        return False

    def undo(self):
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass

    def cut(self):
        try:
            self.text_area.event_generate('<<Cut>>')
        except tk.TclError:
            pass

    def copy(self):
        try:
            self.text_area.event_generate('<<Copy>>')
        except tk.TclError:
            pass

    def paste(self):
        try:
            self.text_area.event_generate('<<Paste>>')
        except tk.TclError:
            pass

    def select_all(self):
        self.text_area.select_range(1.0, tk.END)
        return 'break'

    def exit_app(self):
        if self.text_area.get(1.0, tk.END).strip():
            if messagebox.askyesno('Exit', 'Do you want to save changes before exiting?'):
                if self.save_file():
                    self.root.quit()
            else:
                self.root.quit()
        else:
            self.root.quit()

if __name__ == '__main__':
    root = tk.Tk()
    app = DarkNotepad(root)
    root.mainloop()
