import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, font
from tkinter import ttk
import os
import json
import re

class DarkNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title('Dark Notepad Pro')
        self.root.geometry('1000x700')
        self.root.minsize(500, 400)
        
        # Settings
        self.current_file = None
        self.font_family = 'Consolas'
        self.font_size = 11
        self.word_wrap = True
        self.show_status_bar = True
        self.zoom_level = 100
        self.recent_files = []
        
        # Find/Replace variables
        self.find_window = None
        self.last_find = ""
        
        self.create_widgets()
        self.apply_dark_theme()
        self.update_status_bar()
        self.load_settings()

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill='both')
        
        # Text area with scrollbars
        text_frame = tk.Frame(main_frame)
        text_frame.pack(expand=True, fill='both', padx=2, pady=2)
        
        self.text_area = tk.Text(
            text_frame,
            wrap='word' if self.word_wrap else 'none',
            undo=True,
            font=(self.font_family, self.font_size),
            padx=10,
            pady=10,
            tabs='4c'
        )
        
        # Scrollbars
        self.v_scrollbar = tk.Scrollbar(text_frame, command=self.text_area.yview)
        self.h_scrollbar = tk.Scrollbar(text_frame, orient='horizontal', command=self.text_area.xview)
        
        self.text_area.config(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Pack scrollbars and text area
        self.text_area.grid(row=0, column=0, sticky='nsew')
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')
        if not self.word_wrap:
            self.h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Status bar
        self.status_frame = tk.Frame(main_frame, height=25)
        if self.show_status_bar:
            self.status_frame.pack(side='bottom', fill='x')
        
        self.status_label = tk.Label(
            self.status_frame, 
            text="Line 1, Column 1 | Zoom: 100%", 
            anchor='w', 
            padx=5
        )
        self.status_label.pack(side='left', fill='x', expand=True)
        
        self.word_count_label = tk.Label(
            self.status_frame, 
            text="Words: 0 | Chars: 0", 
            anchor='e', 
            padx=5
        )
        self.word_count_label.pack(side='right')
        
        # Menu bar
        self.create_menu()
        self.bind_shortcuts()
        
        # Bind text area events
        self.text_area.bind('<KeyRelease>', self.on_text_change)
        self.text_area.bind('<Button-1>', self.on_text_change)
        self.text_area.bind('<Control-MouseWheel>', self.on_mouse_wheel)

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
        
        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label='Recent Files', menu=self.recent_menu)
        self.update_recent_menu()
        
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
        edit_menu.add_separator()
        edit_menu.add_command(label='Find...', command=self.show_find_dialog, accelerator='Ctrl+F')
        edit_menu.add_command(label='Replace...', command=self.show_replace_dialog, accelerator='Ctrl+H')
        edit_menu.add_command(label='Go To Line...', command=self.go_to_line, accelerator='Ctrl+G')
        
        # Format menu
        format_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='Format', menu=format_menu)
        format_menu.add_command(label='Font...', command=self.choose_font)
        format_menu.add_separator()
        format_menu.add_checkbutton(label='Word Wrap', command=self.toggle_word_wrap, variable=tk.BooleanVar(value=self.word_wrap))
        
        # View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='View', menu=view_menu)
        view_menu.add_command(label='Zoom In', command=self.zoom_in, accelerator='Ctrl++')
        view_menu.add_command(label='Zoom Out', command=self.zoom_out, accelerator='Ctrl+-')
        view_menu.add_command(label='Reset Zoom', command=self.reset_zoom, accelerator='Ctrl+0')
        view_menu.add_separator()
        view_menu.add_checkbutton(label='Status Bar', command=self.toggle_status_bar, variable=tk.BooleanVar(value=self.show_status_bar))

    def bind_shortcuts(self):
        shortcuts = {
            '<Control-n>': lambda e: self.new_file(),
            '<Control-o>': lambda e: self.open_file(),
            '<Control-s>': lambda e: self.save_file(),
            '<Control-Shift-S>': lambda e: self.save_as_file(),
            '<Control-z>': lambda e: self.undo(),
            '<Control-y>': lambda e: self.redo(),
            '<Control-a>': lambda e: self.select_all(),
            '<Control-f>': lambda e: self.show_find_dialog(),
            '<Control-h>': lambda e: self.show_replace_dialog(),
            '<Control-g>': lambda e: self.go_to_line(),
            '<Control-plus>': lambda e: self.zoom_in(),
            '<Control-minus>': lambda e: self.zoom_out(),
            '<Control-0>': lambda e: self.reset_zoom(),
            '<Alt-F4>': lambda e: self.exit_app(),
            '<F3>': lambda e: self.find_next()
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
            'cursor': '#ffffff',
            'status_bg': '#2d2d2d',
            'status_fg': '#cccccc'
        }
        
        # Apply to text area
        self.text_area.config(
            bg=colors['bg'],
            fg=colors['fg'],
            insertbackground=colors['cursor'],
            selectbackground=colors['select_bg'],
            selectforeground=colors['select_fg'],
            relief='flat',
            borderwidth=1
        )
        
        # Apply to window and frames
        self.root.config(bg=colors['bg'])
        
        # Apply to status bar
        if hasattr(self, 'status_frame'):
            self.status_frame.config(bg=colors['status_bg'])
            self.status_label.config(bg=colors['status_bg'], fg=colors['status_fg'])
            self.word_count_label.config(bg=colors['status_bg'], fg=colors['status_fg'])
        
        # Apply to menus
        self.menu_bar.config(
            bg=colors['menu_bg'],
            fg=colors['menu_fg'],
            activebackground=colors['select_bg'],
            activeforeground=colors['select_fg']
        )

    def on_text_change(self, event=None):
        self.update_status_bar()

    def on_mouse_wheel(self, event):
        # Zoom with Ctrl+Mouse Wheel
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def update_status_bar(self):
        if not self.show_status_bar:
            return
            
        # Get cursor position
        cursor_pos = self.text_area.index(tk.INSERT)
        line, column = cursor_pos.split('.')
        
        # Get text stats
        text_content = self.text_area.get(1.0, tk.END + '-1c')
        char_count = len(text_content)
        word_count = len(text_content.split()) if text_content.strip() else 0
        
        # Update status labels
        self.status_label.config(text=f"Line {line}, Column {int(column)+1} | Zoom: {self.zoom_level}%")
        self.word_count_label.config(text=f"Words: {word_count} | Chars: {char_count}")

    def choose_font(self):
        current_font = font.Font(font=self.text_area['font'])
        font_dialog = tk.Toplevel(self.root)
        font_dialog.title('Choose Font')
        font_dialog.geometry('400x300')
        font_dialog.transient(self.root)
        font_dialog.grab_set()
        
        # Font family
        tk.Label(font_dialog, text='Font Family:').pack(anchor='w', padx=10, pady=(10,0))
        font_families = list(font.families())
        font_families.sort()
        
        family_var = tk.StringVar(value=self.font_family)
        family_combo = ttk.Combobox(font_dialog, textvariable=family_var, values=font_families, state='readonly')
        family_combo.pack(fill='x', padx=10, pady=5)
        
        # Font size
        tk.Label(font_dialog, text='Font Size:').pack(anchor='w', padx=10, pady=(10,0))
        size_var = tk.IntVar(value=self.font_size)
        size_combo = ttk.Combobox(font_dialog, textvariable=size_var, values=list(range(8, 73)), state='readonly')
        size_combo.pack(fill='x', padx=10, pady=5)
        
        # Buttons
        button_frame = tk.Frame(font_dialog)
        button_frame.pack(pady=20)
        
        def apply_font():
            self.font_family = family_var.get()
            self.font_size = size_var.get()
            self.text_area.config(font=(self.font_family, self.font_size))
            self.save_settings()
            font_dialog.destroy()
        
        tk.Button(button_frame, text='OK', command=apply_font, width=10).pack(side='left', padx=5)
        tk.Button(button_frame, text='Cancel', command=font_dialog.destroy, width=10).pack(side='left', padx=5)

    def toggle_word_wrap(self):
        self.word_wrap = not self.word_wrap
        self.text_area.config(wrap='word' if self.word_wrap else 'none')
        
        if self.word_wrap:
            self.h_scrollbar.grid_remove()
        else:
            self.h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        self.save_settings()

    def toggle_status_bar(self):
        self.show_status_bar = not self.show_status_bar
        
        if self.show_status_bar:
            self.status_frame.pack(side='bottom', fill='x')
            self.update_status_bar()
        else:
            self.status_frame.pack_forget()
        
        self.save_settings()

    def zoom_in(self):
        if self.zoom_level < 500:
            self.zoom_level += 10
            new_size = int(self.font_size * (self.zoom_level / 100))
            self.text_area.config(font=(self.font_family, new_size))
            self.update_status_bar()

    def zoom_out(self):
        if self.zoom_level > 50:
            self.zoom_level -= 10
            new_size = int(self.font_size * (self.zoom_level / 100))
            self.text_area.config(font=(self.font_family, new_size))
            self.update_status_bar()

    def reset_zoom(self):
        self.zoom_level = 100
        self.text_area.config(font=(self.font_family, self.font_size))
        self.update_status_bar()

    def show_find_dialog(self):
        if self.find_window:
            self.find_window.lift()
            return
            
        self.find_window = tk.Toplevel(self.root)
        self.find_window.title('Find')
        self.find_window.geometry('350x100')
        self.find_window.transient(self.root)
        
        tk.Label(self.find_window, text='Find:').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.find_entry = tk.Entry(self.find_window, width=25)
        self.find_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.find_entry.insert(0, self.last_find)
        self.find_entry.focus()
        
        button_frame = tk.Frame(self.find_window)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        tk.Button(button_frame, text='Find Next', command=self.find_next, width=10).pack(side='left', padx=5)
        tk.Button(button_frame, text='Close', command=self.close_find_dialog, width=10).pack(side='left', padx=5)
        
        self.find_window.protocol('WM_DELETE_WINDOW', self.close_find_dialog)
        self.find_entry.bind('<Return>', lambda e: self.find_next())
        self.find_window.columnconfigure(1, weight=1)

    def show_replace_dialog(self):
        if self.find_window:
            self.find_window.destroy()
            
        self.find_window = tk.Toplevel(self.root)
        self.find_window.title('Replace')
        self.find_window.geometry('350x150')
        self.find_window.transient(self.root)
        
        tk.Label(self.find_window, text='Find:').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.find_entry = tk.Entry(self.find_window, width=25)
        self.find_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        tk.Label(self.find_window, text='Replace:').grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.replace_entry = tk.Entry(self.find_window, width=25)
        self.replace_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        button_frame = tk.Frame(self.find_window)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        tk.Button(button_frame, text='Find Next', command=self.find_next, width=10).pack(side='left', padx=2)
        tk.Button(button_frame, text='Replace', command=self.replace_current, width=10).pack(side='left', padx=2)
        tk.Button(button_frame, text='Replace All', command=self.replace_all, width=10).pack(side='left', padx=2)
        tk.Button(button_frame, text='Close', command=self.close_find_dialog, width=10).pack(side='left', padx=2)
        
        self.find_window.protocol('WM_DELETE_WINDOW', self.close_find_dialog)
        self.find_window.columnconfigure(1, weight=1)

    def find_next(self):
        if not hasattr(self, 'find_entry') or not self.find_entry:
            return
            
        search_text = self.find_entry.get()
        if not search_text:
            return
            
        self.last_find = search_text
        
        # Start search from current cursor position
        start_pos = self.text_area.index(tk.INSERT)
        pos = self.text_area.search(search_text, start_pos, tk.END)
        
        if pos:
            # Select found text
            end_pos = f"{pos}+{len(search_text)}c"
            self.text_area.tag_remove('sel', 1.0, tk.END)
            self.text_area.tag_add('sel', pos, end_pos)
            self.text_area.mark_set(tk.INSERT, end_pos)
            self.text_area.see(pos)
        else:
            # Search from beginning
            pos = self.text_area.search(search_text, 1.0, start_pos)
            if pos:
                end_pos = f"{pos}+{len(search_text)}c"
                self.text_area.tag_remove('sel', 1.0, tk.END)
                self.text_area.tag_add('sel', pos, end_pos)
                self.text_area.mark_set(tk.INSERT, end_pos)
                self.text_area.see(pos)
            else:
                messagebox.showinfo('Find', f'Cannot find "{search_text}"')

    def replace_current(self):
        if not hasattr(self, 'find_entry') or not hasattr(self, 'replace_entry'):
            return
            
        if self.text_area.tag_ranges('sel'):
            self.text_area.delete('sel.first', 'sel.last')
            self.text_area.insert(tk.INSERT, self.replace_entry.get())
        
        self.find_next()

    def replace_all(self):
        if not hasattr(self, 'find_entry') or not hasattr(self, 'replace_entry'):
            return
            
        search_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        
        if not search_text:
            return
            
        content = self.text_area.get(1.0, tk.END + '-1c')
        new_content = content.replace(search_text, replace_text)
        
        if content != new_content:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, new_content)
            count = content.count(search_text)
            messagebox.showinfo('Replace All', f'Replaced {count} occurrences')
        else:
            messagebox.showinfo('Replace All', f'No occurrences of "{search_text}" found')

    def close_find_dialog(self):
        if self.find_window:
            self.find_window.destroy()
            self.find_window = None

    def go_to_line(self):
        line = simpledialog.askinteger('Go To Line', 'Line number:', minvalue=1)
        if line:
            self.text_area.mark_set(tk.INSERT, f'{line}.0')
            self.text_area.see(f'{line}.0')

    def add_recent_file(self, filepath):
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        self.recent_files.insert(0, filepath)
        self.recent_files = self.recent_files[:10]  # Keep only 10 recent files
        self.update_recent_menu()
        self.save_settings()

    def update_recent_menu(self):
        self.recent_menu.delete(0, tk.END)
        for filepath in self.recent_files:
            filename = os.path.basename(filepath)
            self.recent_menu.add_command(
                label=filename, 
                command=lambda f=filepath: self.open_recent_file(f)
            )

    def open_recent_file(self, filepath):
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, content)
                self.current_file = filepath
                self.root.title(f'Dark Notepad Pro - {os.path.basename(filepath)}')
            except Exception as e:
                messagebox.showerror('Error', f'Could not open file:\n{str(e)}')
        else:
            messagebox.showerror('Error', 'File not found')
            self.recent_files.remove(filepath)
            self.update_recent_menu()
            self.save_settings()

    def save_settings(self):
        settings = {
            'font_family': self.font_family,
            'font_size': self.font_size,
            'word_wrap': self.word_wrap,
            'show_status_bar': self.show_status_bar,
            'recent_files': self.recent_files,
            'window_geometry': self.root.geometry()
        }
        
        try:
            with open('dark_notepad_settings.json', 'w') as f:
                json.dump(settings, f)
        except:
            pass

    def load_settings(self):
        try:
            with open('dark_notepad_settings.json', 'r') as f:
                settings = json.load(f)
                
            self.font_family = settings.get('font_family', 'Consolas')
            self.font_size = settings.get('font_size', 11)
            self.word_wrap = settings.get('word_wrap', True)
            self.show_status_bar = settings.get('show_status_bar', True)
            self.recent_files = settings.get('recent_files', [])
            
            # Apply loaded settings
            self.text_area.config(font=(self.font_family, self.font_size))
            self.text_area.config(wrap='word' if self.word_wrap else 'none')
            
            if not self.word_wrap:
                self.h_scrollbar.grid(row=1, column=0, sticky='ew')
            
            if not self.show_status_bar:
                self.status_frame.pack_forget()
                
            self.update_recent_menu()
            
            # Restore window size
            geometry = settings.get('window_geometry')
            if geometry:
                self.root.geometry(geometry)
                
        except:
            pass

    # Standard file operations (same as before but with recent files support)
    def new_file(self):
        if self.text_area.get(1.0, tk.END).strip():
            if messagebox.askyesno('New File', 'Do you want to save changes?'):
                self.save_file()
        
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.root.title('Dark Notepad Pro - Untitled')

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title='Open Text File',
            defaultextension='.txt',
            filetypes=[
                ('Text Files', '*.txt'),
                ('Python Files', '*.py'),
                ('HTML Files', '*.html'),
                ('CSS Files', '*.css'),
                ('JavaScript Files', '*.js'),
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
                self.root.title(f'Dark Notepad Pro - {os.path.basename(file_path)}')
                self.add_recent_file(file_path)
            except Exception as e:
                messagebox.showerror('Error', f'Could not open file:\n{str(e)}')

    def save_file(self):
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END + '-1c')
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.root.title(f'Dark Notepad Pro - {os.path.basename(self.current_file)}')
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
                ('Python Files', '*.py'),
                ('HTML Files', '*.html'),
                ('CSS Files', '*.css'),
                ('JavaScript Files', '*.js'),
                ('All Files', '*.*')
            ]
        )
        if file_path:
            try:
                content = self.text_area.get(1.0, tk.END + '-1c')
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.current_file = file_path
                self.root.title(f'Dark Notepad Pro - {os.path.basename(file_path)}')
                self.add_recent_file(file_path)
                return True
            except Exception as e:
                messagebox.showerror('Error', f'Could not save file:\n{str(e)}')
                return False
        return False

    # Standard edit operations (same as before)
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
                    self.save_settings()
                    self.root.quit()
            else:
                self.save_settings()
                self.root.quit()
        else:
            self.save_settings()
            self.root.quit()

if __name__ == '__main__':
    root = tk.Tk()
    app = DarkNotepad(root)
    root.mainloop()
