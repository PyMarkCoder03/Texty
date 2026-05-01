"""
SimpleNotes è un semplice editor di testo creato
con il linguaggio Python e la libreria Tkinter.

SimpleNotes
Versione 1.0.0
Autore: Marco Mazzo
"""

# Importazione delle librerie e dei moduli opportuni
import tkinter as tk
from tkinter import filedialog, font, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
from webbrowser import open as browse

class SimpleNotes:
    """
    Classe principale per la gestione del software.
    
    Coordina l'interfaccia grafica, la persistenza dei dati su file
    e la logica di editing, inclusi il monitoraggio delle modifiche,
    la gestione dei temi e le scorciatoie da tastiera.
    """
    def __init__(self, master):
        # Finestra principale
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.geometry("1100x500")
        self.master.grid_rowconfigure(0, weight = 1)
        self.master.grid_rowconfigure(1, weight = 0)
        self.master.grid_columnconfigure(0, weight = 1)

        self.file_path = None
        self.update_window_title()

        try:
            self.master.iconbitmap("icon.ico")
        except tk.TclError:
            pass

        # Area di testo con barra di scorrimento
        self.text_area = ScrolledText(self.master, undo = True, \
                                      autoseparators = True, \
                                      maxundo = -1, wrap = tk.WORD)
        self.text_area.grid(row = 0, column = 0, sticky = "nsew")
        self.text_area.config(font = ("Consolas", 11))
        self.text_area.focus_set()
        self.text_area.bind("<<Modified>>", self.on_modified)

        # Barra di scorrimento orizzontale (nascosta)
        self.xscrollbar = tk.Scrollbar(self.master, orient = "horizontal", \
                                       command = self.text_area.xview)
        self.text_area.config(xscrollcommand = self.xscrollbar.set)

        # Frame divisorio
        self.divider = tk.Frame(self.master, bg = "light gray")
        self.divider.grid(row = 2, column = 0, sticky = "ew")

        # Barra di stato
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.master, textvariable = self.status_var, \
                                    anchor = tk.W, font = ("Arial", 10))
        self.status_bar.grid(row = 3, column = 0, sticky = "ew", \
                             padx = 5, pady = 2)

        # Valori booleani per tema, word wrap e barra di stato
        self.light_theme = tk.BooleanVar(value = True)
        self.dark_theme = tk.BooleanVar(value = False)
        self.word_wrap = tk.BooleanVar(value = True)
        self.status_bar_visible = tk.BooleanVar(value = True)

        # Creazione di menu, barra di stato ed eventi
        self.create_menus()
        self.update_status_bar()
        self.bind_events()

    def on_modified(self, event = None):
        """
        Aggiunge un "*" prima del titolo della finestra per indicare
        modifiche non salvate o lo rimuove se non sono presenti modifiche.
        """
        if self.text_area.edit_modified():
            if not self.master.title().startswith("*"):
                self.master.title(f"*{self.master.title()}")
        else:
            if self.master.title().startswith("*"):
                self.master.title(self.master.title()[1:])

    def get_filename(self):
        """
        Imposta il nome del file.

        Se eiste un percorso, ottiene il nome del file da esso,
        altrimenti vi associa il nome del file di default.
        Ritorna infine il nome del file.
        """
        if self.file_path:
            filename = self.file_path.split('/')[-1]
        else:
            filename = "Senza nome"
        return filename

    def ask_for_save(self):
        """
        Mostra una finestra di dialogo per chiedere all'utente
        se desidera salvare le modifiche apportate ad un file.
        """
        filename = self.get_filename()
        box_title = "SimpleNotes"
        box_message = f"Salvare le modifiche apportate a '{filename}'?"
        self.msg = messagebox.askyesnocancel(box_title, box_message)

    def update_window_title(self):
        """
        Aggiorna il titolo della finestra principale con il nome
        del file ottenuto dal relativo metodo.
        """
        filename = self.get_filename()
        self.master.title(f"{filename} - SimpleNotes")

    def update_status_bar(self, event = None):
        """
        Aggiorna la barra di stato con gli indici di riga e colonna ed
        il conteggio di parole e caratteri (testo totale e selezionato).
        """
        # Indici di riga e colonna
        row, col = self.text_area.index(tk.INSERT).split('.')
        col = str(int(col) + 1)

        # Conteggio testo totale
        full_text = self.text_area.get("1.0", "end-1c")
        total_chars = len(full_text)
        total_words = len(full_text.split())

        # Conteggio testo selezionato
        selection_range = self.text_area.tag_ranges("sel")

        if selection_range:
            selected_text = self.text_area.get("sel.first", "sel.last")
            sel_chars = len(selected_text)
            sel_words = len(selected_text.split())
            
            words_display = f"{sel_words} di {total_words} parole"
            chars_display = f"{sel_chars} di {total_chars} caratteri"
        else:
            words_display = f"{total_words} parole"
            chars_display = f"{total_chars} caratteri"

        self.status_var.set(f"Riga {row}, colonna {col} | {words_display} ({chars_display})")

    def create_menus(self):
        """
        Configura la barra dei menu principale e vi associa
        i relativi metodi e scorciatoie da tastiera.
        """
        # Barra dei menu principale
        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu = self.menu_bar)

        # Menu File
        file_menu = tk.Menu(self.menu_bar, tearoff = 0)
        self.menu_bar.add_cascade(label = "File", menu = file_menu)
        file_menu.add_command(label = "Nuovo", \
                              command = self.new_file_with_prompt, \
                              accelerator = 'CTRL+N')
        file_menu.add_command(label = "Nuova finestra", \
                              command = self.new_window, \
                              accelerator = 'CTRL+MAIUSC+N')
        file_menu.add_command(label = "Apri...", \
                              command = self.open_file_with_prompt, \
                              accelerator = 'CTRL+O')
        file_menu.add_command(label = "Salva", command = self.save_file, \
                              accelerator = 'CTRL+S')
        file_menu.add_command(label = "Salva con nome...", \
                              command = self.save_file_as, \
                              accelerator = 'CTRL+MAIUSC+S')
        file_menu.add_separator()
        file_menu.add_command(label = "Esci", command = self.on_close, \
                              accelerator = 'CTRL+W')

        # Menu Modifica
        edit_menu = tk.Menu(self.menu_bar, tearoff = 0)
        self.menu_bar.add_cascade(label = "Modifica", menu = edit_menu)
        edit_menu.add_command(label = "Annulla", command = self.undo, \
                              accelerator = 'CTRL+Z')
        edit_menu.add_command(label = "Ripeti", command = self.redo, \
                              accelerator = 'CTRL+MAIUSC+Z')
        edit_menu.add_separator()
        edit_menu.add_command(label = "Taglia", command = self.cut, \
                              accelerator = 'CTRL+X')
        edit_menu.add_command(label = "Copia", command = self.copy, \
                              accelerator = 'CTRL+C')
        edit_menu.add_command(label = "Incolla", command = self.paste, \
                              accelerator = 'CTRL+V')
        edit_menu.add_command(label = "Elimina", command = self.delete_text, \
                              accelerator = 'CANC')
        edit_menu.add_separator()
        edit_menu.add_command(label = "Ora e data", \
                              command = self.insert_timestamp, \
                              accelerator = 'F5')
        edit_menu.add_command(label = "Trova...", \
                              command = self.open_find_window, \
                              accelerator = 'CTRL+F')
        edit_menu.add_command(label = "Sostituisci...", \
                              command = self.open_replace_window, \
                              accelerator = 'CTRL+MAIUSC+F')
        edit_menu.add_command(label = "Seleziona tutto", \
                              command = self.select_all, \
                              accelerator = 'CTRL+A')

        # Menu Visualizza
        view_menu = tk.Menu(self.menu_bar, tearoff = 0)
        self.menu_bar.add_cascade(label = "Visualizza", menu = view_menu)
        theme_menu = tk.Menu(view_menu, tearoff = 0)
        theme_menu.add_checkbutton(label = "Chiaro", \
                                   variable = self.light_theme, \
                                   command = self.set_light_theme)
        theme_menu.add_checkbutton(label = "Scuro", \
                                   variable = self.dark_theme, \
                                   command = self.set_dark_theme)
        view_menu.add_cascade(label = "Tema", menu = theme_menu)
        view_menu.add_command(label = "Carattere...", \
                              command = self.open_font_window)
        view_menu.add_separator()
        view_menu.add_checkbutton(label = "Barra di stato", \
                                  variable = self.status_bar_visible, \
                                  command = self.toggle_status_bar)
        view_menu.add_checkbutton(label = "A capo automatico", \
                                  variable = self.word_wrap, \
                                  command = self.toggle_word_wrap)

        # Menu Aiuto
        help_menu = tk.Menu(self.menu_bar, tearoff = 0)
        self.menu_bar.add_cascade(label = "?", menu = help_menu)
        help_menu.add_command(label = "Guida", command = self.open_help_link)
        help_menu.add_command(label = "Informazioni su SimpleNotes...", \
                              command = self.open_info_window)

    def show_context_menu(self, event):
        """
        Configura il menu contestuale e lo visualizza alle coordinate
        del cursore (tasto destro).
        """
        context_menu = tk.Menu(self.master, tearoff = 0)
        context_menu.add_command(label = "Annulla", command = self.undo)
        context_menu.add_command(label = "Ripeti", command = self.redo)
        context_menu.add_separator()
        context_menu.add_command(label = "Taglia", command = self.cut)
        context_menu.add_command(label = "Copia", command = self.copy)
        context_menu.add_command(label = "Incolla", command = self.paste)
        context_menu.add_command(label = "Elimina", command = self.delete_text)
        context_menu.add_separator()
        context_menu.add_command(label = "Seleziona tutto", \
                                 command = self.select_all)
        context_menu.post(event.x_root, event.y_root)

    def bind_events(self):
        """
        Imposta gli eventi da tastiera e li associa ai rispettivi metodi.
        """
        # Eventi per i metodi del menu File
        self.master.bind('<Control-n>', lambda event: self.new_file_with_prompt())
        self.master.bind('<Control-N>', lambda event: self.new_file_with_prompt())
        self.master.bind('<Control-Shift-N>', lambda event: self.new_window())
        self.master.bind('<Control-Shift-n>', lambda event: self.new_window())
        self.master.bind('<Control-o>', lambda event: self.open_file_with_prompt())
        self.master.bind('<Control-O>', lambda event: self.open_file_with_prompt())
        self.master.bind('<Control-s>', lambda event: self.save_file())
        self.master.bind('<Control-S>', lambda event: self.save_file())
        self.master.bind('<Control-Shift-S>', lambda event: self.save_file_as())
        self.master.bind('<Control-Shift-s>', lambda event: self.save_file_as())
        self.master.bind('<Control-w>', lambda event: self.on_close())
        self.master.bind('<Control-W>', lambda event: self.on_close())

        # Eventi per i metodi del menu Modifica
        self.master.bind('<Control-Shift-Z>', lambda event: self.redo())
        self.master.bind('<Control-Shift-z>', lambda event: self.redo())
        self.master.bind('<Control-x>', lambda event: self.cut())
        self.master.bind('<Control-X>', lambda event: self.cut())
        self.master.bind('<Control-c>', lambda event: self.copy())
        self.master.bind('<Control-C>', lambda event: self.copy())
        self.master.bind('<F5>', lambda event: self.insert_timestamp())
        self.master.bind('<Control-f>', lambda event: self.open_find_window())
        self.master.bind('<Control-F>', lambda event: self.open_find_window())
        self.master.bind('<Control-Shift-F>', lambda event: self.open_replace_window())
        self.master.bind('<Control-Shift-f>', lambda event: self.open_replace_window())

        # Evento del tasto destro del mouse per il menu contestuale
        self.text_area.bind("<Button-3>", self.show_context_menu)

        # Eventi di movimento del cursore per la barra di stato
        self.text_area.bind("<KeyRelease>", self.update_status_bar)
        self.text_area.bind("<ButtonRelease>", self.update_status_bar)

    # METODI DEL MENU FILE
    # ====================
    def new_file(self):
        """
        Crea un nuovo file.

        Svuota l'area di testo, resetta il percorso del file e
        aggiorna l'interfaccia utente (titolo e barra di stato).
        Resetta inoltre lo stato di modifica dell'area di testo.
        """
        self.text_area.delete(1.0, tk.END)
        self.file_path = None
        self.update_window_title()
        self.update_status_bar()
        self.text_area.edit_modified(False)
        self.text_area.edit_reset()

    def new_file_with_prompt(self):
        """
        Crea un nuovo file gestendo eventuali modifiche non salvate.

        Se il file corrente è stato modificato, chiede all'utente
        se desidera salvare prima di procedere.
        """
        if self.text_area.edit_modified():
            self.ask_for_save()
            if self.msg is True:
                self.save_file()
                if self.file_path:
                    self.new_file()
                else:
                    return
            elif self.msg is False:
                self.new_file()
            else:
                return
        else:
            self.new_file()

    def new_window(self):
        """
        Apre una nuova istanza indipendente dell'applicazione.
        """
        new_window = tk.Toplevel(self.master)
        app = SimpleNotes(new_window)

    def open_file(self):
        """
        Mostra una finestra di dialogo per selezionare ed aprire
        un file esistente.

        Se l'apertura ha successo, il contenuto viene
        caricato nell'area di testo; in caso di errore,
        mostra un avviso.
        """
        selected_path = filedialog.askopenfilename(
            title = "Apri",
            filetypes = [
                ("File di testo", "*.txt"),
                ("File Markdown", "*.md"),
                ("HTML", "*.html *.htm"),
                ("CSS", "*.css"),
                ("Script JavaScript", "*.js"),
                ("Script Python", "*.py *.pyw"),
                ("Tutti i file", "*.*")
            ]
        )
        if selected_path:
            self.file_path = selected_path
            self.text_area.delete(1.0, tk.END)
            
            try:
                with open(selected_path, "r", encoding = "utf-8") as file:
                    self.text_area.insert(1.0, file.read())
                    self.text_area.mark_set(tk.INSERT, 1.0)
                    self.text_area.see(1.0)

                self.text_area.edit_modified(False)
                self.text_area.edit_reset()
                self.update_window_title()
                self.update_status_bar()

            except Exception:
                filename = self.get_filename()
                self.new_file()
                box_title = "SimpleNotes"
                box_message = (
                    f"Si è verificato un errore durante l'apertura di '{filename}'.\n"
                    "Il file potrebbe essere danneggiato o il formato non supportato."
                )
                messagebox.showwarning(box_title, box_message)

    def open_file_with_prompt(self):
        """
        Apre un file gestendo eventuali modifiche non salvate.

        Se il file corrente è stato modificato, chiede all'utente
        se desidera salvare prima di procedere.
        """
        if self.text_area.edit_modified():
            self.ask_for_save()
            if self.msg is True:
                self.save_file()
                if self.file_path:
                    self.open_file()
                else:
                    return
            elif self.msg is False:
                self.open_file()
            else:
                return
        else:
            self.open_file()

    def save_file(self):
        """
        Salva il contenuto corrente nel file associato.

        Se non esiste un percorso file, richiama il
        metodo per salvare il file in un percorso.
        """
        if self.file_path:
            file_content = self.text_area.get(1.0, tk.END)
            with open(self.file_path, "w", encoding = "utf-8") as file:
                file.write(file_content.rstrip("\n"))
                self.text_area.edit_modified(False)
        else:
            self.save_file_as()
            return

    def save_file_as(self):
        """
        Apre una finestra di dialogo per salvare il file
        con un nuovo nome o percorso.

        Terminato il salvataggio, aggiorna il percorso
        del file associato e il titolo della finestra.
        """
        selected_path = filedialog.asksaveasfilename(
            title = "Salva con nome",
            initialfile = self.get_filename(),
            defaultextension = ".txt",
            filetypes = [
                ("File di testo", "*.txt"),
                ("File Markdown", "*.md"),
                ("HTML", "*.html"),
                ("CSS", "*.css"),
                ("Script JavaScript", "*.js"),
                ("Script Python", "*.py"),
                ("Tutti i file", "*.*")
            ]
        )
        if selected_path:
            self.file_path = selected_path
            file_content = self.text_area.get(1.0, tk.END)

            with open(selected_path, "w", encoding = "utf-8") as file:
                file.write(file_content.rstrip("\n"))

            self.update_window_title()
            self.text_area.edit_modified(False)
            self.text_area.edit_reset()

    def on_close(self):
        """
        Gestisce la chiusura della finestra dell'applicazione.

        Se il file corrente è stato modificato, chiede all'utente
        se desidera salvare prima di procedere.
        """
        if self.text_area.edit_modified():
            self.ask_for_save()
            if self.msg is True:
                self.save_file()
                if self.file_path:
                    self.master.destroy()
                else:
                    return
            elif self.msg is False:
                self.master.destroy()
            else:
                return
        else:
            self.master.destroy()

    # METODI DEL MENU MODIFICA
    # ========================
    def undo(self):
        """
        Annulla l'ultima operazione effettuata nell'area di testo.

        Sfrutta il meccanismo di undo nativo di Tkinter. Se non ci 
        sono più azioni da annullare, emette un segnale acustico.
        """
        try:
            self.text_area.edit_undo()
            self.update_status_bar()
        except tk.TclError:
            self.master.bell()

    def redo(self):
        """
        Ripristina l'ultima operazione annullata.

        Se non ci sono azioni da ripristinare, emette
        un segnale acustico.
        """
        try:
            self.text_area.edit_redo()
            self.update_status_bar()
        except tk.TclError:
            self.master.bell()

    def cut(self):
        """
        Cancella il testo selezionato e lo copia negli appunti.
        """
        self.text_area.event_generate("<<Cut>>")
        self.update_status_bar()

    def copy(self):
        """
        Copia il testo selezionato negli appunti.
        """
        self.text_area.event_generate("<<Copy>>")

    def paste(self):
        """
        Incolla il testo dagli appunti alla posizione corrente del cursore.

        Dopo l'inserimento, assicura che il cursore rimanga
        visibile e aggiorna la barra di stato.
        """
        self.text_area.event_generate("<<Paste>>")
        self.text_area.after(10, lambda: self.text_area.see(tk.INSERT))
        self.update_status_bar()

    def delete_text(self):
        """
        Elimina il testo attualmente selezionato.

        Se non è presente alcuna selezione, emette un segnale acustico.
        """
        try:
            self.text_area.delete("sel.first", "sel.last")
            self.update_status_bar()
        except tk.TclError:
            self.master.bell()

    def select_all(self):
        """
        Seleziona tutto il contenuto dell'area di testo.
        """
        self.text_area.tag_add("sel", 1.0, tk.END)

    def insert_timestamp(self):
        """
        Inserisce la data e l'ora corrente (formato HH:MM GG/MM/AAAA)
        nella posizione corrente del cursore.
        """
        now = datetime.now()
        time_and_date = now.strftime("%H:%M %d/%m/%Y")
        self.text_area.insert(tk.INSERT, time_and_date)
        self.update_status_bar()

    def find_next(self):
        """
        Cerca e seleziona l'occorrenza successiva
        del testo inserito nel campo di ricerca.

        Gestisce ciclicamente il testo: se arriva alla
        fine del documento, ricomincia dall'inizio.
        Mostra un avviso se il campo è vuoto o se il 
        testo non viene trovato.
        """
        find_text = self.find_entry.get().strip()

        if not find_text:
            title = "SimpleNotes"
            message = "Campo vuoto: inserire una parola o una frase da trovare"
            messagebox.showinfo(title, message)
            return

        if not hasattr(self, 'last_position'):
            self.last_position = "1.0"

        start_pos = self.text_area.search(find_text, self.last_position, \
                                          tk.END, nocase = True)

        if not start_pos:
            self.last_position = "1.0"
            start_pos = self.text_area.search(find_text, self.last_position, \
                                              tk.END, nocase = True)

        if not start_pos:
            title = "SimpleNotes"
            message = f"Impossibile trovare \"{find_text}\""
            messagebox.showinfo(title, message)
            return

        end_pos = f"{start_pos}+{len(find_text)}c"
        self.text_area.tag_remove("sel", "1.0", tk.END)
        self.text_area.tag_add("sel", start_pos, end_pos)
        self.text_area.see(start_pos)
        self.text_area.focus_set()
        self.last_position = end_pos

    def replace(self):
        """
        Sostituisce la prima occorrenza trovata del testo
        cercato con il nuovo testo.
        
        Una volta sostituito, seleziona il nuovo
        testo inserito e sposta il focus.
        """
        find_text = self.find_entry.get().strip()
        replace_text = self.replace_entry.get().strip()

        if not find_text:
            title = "SimpleNotes"
            message = "Campo vuoto: inserire una parola o una frase da trovare"
            messagebox.showinfo(title, message)
            return

        start_pos = self.text_area.search(find_text, "1.0", tk.END, \
                                          nocase = True)

        if not start_pos:
            title = "SimpleNotes"
            message = f"Impossibile trovare \"{find_text}\""
            messagebox.showinfo(title, message)
            return

        end_pos = f"{start_pos}+{len(find_text)}c"
        self.text_area.delete(start_pos, end_pos)
        self.text_area.insert(start_pos, replace_text)
        self.text_area.tag_remove("sel", "1.0", tk.END)
        self.text_area.tag_add("sel", start_pos, f"{start_pos}+{len(replace_text)}c")
        self.text_area.see(start_pos)
        self.text_area.focus_set()

    def replace_all(self):
        """
        Sostituisce globalmente ogni occorrenza del
        testo cercato in tutto il files.
        
        Al termine dell'operazione, mostra un messaggio
        con il numero totale di sostituzioni effettuate.
        """
        find_text = self.find_entry.get().strip()
        replace_text = self.replace_entry.get().strip()

        if not find_text:
            title = "SimpleNotes"
            message = "Campo vuoto: inserire una parola o una frase da trovare"
            messagebox.showinfo(title, message)
            return

        pos = "1.0"
        counter = 0 

        while True:
            pos = self.text_area.search(find_text, pos, tk.END, \
                                        nocase = True)

            if not pos:
                break

            end_pos = f"{pos}+{len(find_text)}c"

            self.text_area.delete(pos, end_pos)
            self.text_area.insert(pos, replace_text)

            pos = f"{pos}+{len(replace_text)}c"
            counter += 1

        if counter == 0:
            title = "SimpleNotes"
            message = f"Impossibile trovare \"{find_text}\""
            messagebox.showinfo(title, message)
            return
        else:
            title = "SimpleNotes"
            message = f"Sostituite {counter} occorrenze"
            messagebox.showinfo(title, message)
            return
   
    def open_find_window(self):
        """
        Crea e visualizza la finestra di dialogo "Trova".
        
        Configura i widget necessari (campo di inserimento e pulsanti)
        e imposta i binding per facilitare la ricerca rapida.
        """
        # Crea una finestra per cercare un'occorrenza
        find_window = tk.Toplevel(self.master)
        find_window.transient(self.master)
        find_window.title("Trova")
        find_window.geometry("400x100")
        find_window.resizable(False, False)

        # Imposta l'icona della finestra
        try:
            find_window.iconbitmap("icon.ico")
        except tk.TclError:
            pass

        # Crea un Frame per contenere i widget
        find_frame = ttk.Frame(find_window)
        find_frame.pack(fill = tk.X, padx = 10, pady = 15)

        # Crea una Label e un Entry per trovare l'occorrenza
        find_label = ttk.Label(find_frame, text = "Trova:")
        find_label.pack(side = tk.LEFT, padx = 5)

        self.find_entry = ttk.Entry(find_frame)
        self.find_entry.pack(fill = tk.X, padx = 5)
        self.find_entry.focus_set()
        self.find_entry.bind("<Return>", lambda event: self.find_next())

        # Crea un Frame per contenere i Button
        button_frame = ttk.Frame(find_window)
        button_frame.pack(side = tk.BOTTOM, anchor = tk.E, \
                          padx = 10, pady = 10)

        # Crea un Button per trovare l'occorrenza e uno per annullare
        find_button = ttk.Button(button_frame, text = "Trova successivo", \
                                 width = 18, command = self.find_next)
        find_button.pack(side = tk.LEFT, padx = 5)
        
        cancel_button = ttk.Button(button_frame, text = "Annulla", \
                                   width = 18, command = find_window.destroy)
        cancel_button.pack(side = tk.LEFT, padx = 5)

    def open_replace_window(self):
        """
        Crea e visualizza la finestra di dialogo "Sostituisci".
        
        Include opzioni per la ricerca singola, la sostituzione singola 
        e la sostituzione globale (Sostituisci tutto).
        """
        replace_window = tk.Toplevel(self.master)
        replace_window.transient(self.master)
        replace_window.title("Sostituisci")
        replace_window.geometry("570x150")
        replace_window.resizable(False, False)

        try:
            replace_window.iconbitmap("icon.ico")
        except tk.TclError:
            pass

        find_frame = ttk.Frame(replace_window)
        find_frame.pack(fill = tk.X, padx = 10, pady = 15)

        find_label = ttk.Label(find_frame, text = "Trova:")
        find_label.pack(side = tk.LEFT, padx = 5)

        self.find_entry = ttk.Entry(find_frame, width = 70)
        self.find_entry.pack(side = tk.RIGHT, padx = 5)
        self.find_entry.focus_set()
        self.find_entry.bind("<Return>", lambda event: self.find_next())

        replace_frame = ttk.Frame(replace_window)
        replace_frame.pack(fill = tk.X, padx = 10, pady = 10)
        
        replace_label = ttk.Label(replace_frame, text = "Sostituisci con:")
        replace_label.pack(side = tk.LEFT, padx = 5)
        
        self.replace_entry = ttk.Entry(replace_frame, width = 70)
        self.replace_entry.pack(side = tk.RIGHT, padx = 5)

        button_frame = ttk.Frame(replace_window)
        button_frame.pack(side = tk.BOTTOM, pady = 10)

        find_button = ttk.Button(button_frame, text = "Trova successivo", \
                                 width = 20, command = self.find_next)

        replace_button = ttk.Button(button_frame, text = "Sostituisci", \
                                    width = 20, command = self.replace)

        replace_all_button = ttk.Button(button_frame, width = 20, \
                                        text = "Sostituisci tutto", \
                                        command = self.replace_all)

        cancel_button = ttk.Button(button_frame, text = "Annulla", \
                                   width = 20, command = replace_window.destroy)

        find_button.pack(side = tk.LEFT, padx = 3)
        replace_button.pack(side = tk.LEFT, padx = 3)
        replace_all_button.pack(side = tk.LEFT, padx = 3)
        cancel_button.pack(side = tk.LEFT, padx = 3)

    # METODI DEL MENU VISUALIZZA
    # ==========================
    def set_light_theme(self):
        """
        Attiva il tema chiaro.
        
        Aggiorna le variabili di stato del tema e richiama "apply_theme()"
        per aggiornare il tema dell'interfaccia.
        """
        self.light_theme.set(True)
        self.dark_theme.set(False)
        self.apply_theme()

    def set_dark_theme(self):
        """
        Attiva il tema scuro.
        
        Aggiorna le variabili di stato del tema e richiama "apply_theme()"
        per applicare una palette di colori riposante per gli occhi.
        """
        self.light_theme.set(False)
        self.dark_theme.set(True)
        self.apply_theme()

    def apply_theme(self):
        """
        Applica i colori configurati all'area di testo.
        
        Modifica sfondo (bg), colore del testo (fg) e colore del cursore 
        (insertbackground) in base al tema attualmente impostato.
        """
        if self.light_theme.get():
            self.text_area.config(bg = "white", fg = "black", \
                                  insertbackground = "black")
        else:
            self.text_area.config(bg = "#2D2D2D", fg = "white", \
                                  insertbackground = "white")

    def apply_font(self):
        """
        Valida e applica le impostazioni del carattere all'area di testo.
        
        Verifica che la famiglia, lo stile e la dimensione (tra 1 e 1000) 
        siano validi. In caso di errore, mostra un messaggio informativo. 
        Una volta applicato il font, chiude la finestra delle impostazioni.
        """
        # Controlla la validità della famiglia
        if self.selected_font_family.get() not in self.font_families:
            title = "SimpleNotes"
            message = "La famiglia di carattere selezionata non è valida"
            messagebox.showinfo(title, message)
            return

        # Controlla la validità dello stile
        if self.selected_font_style.get() not in self.font_styles:
            title = "SimpleNotes"
            message = "Lo stile selezionato non è valido"
            messagebox.showinfo(title, message)
            return

        # Controlla la validità della dimensione
        try:
            font_size = int(self.selected_font_size.get())
            if font_size < 1 or font_size > 1000:
                title = "SimpleNotes"
                message = "La dimensione deve essere compresa tra 1 e 1000"
                messagebox.showinfo(title, message)
                return

        # Gestisce l'eccezione tk.TclError con un messaggio
        except tk.TclError:
            title = "SimpleNotes"
            message = "La dimensione deve essere un numero"
            messagebox.showinfo(title, message)
            return

        # Crea una mappa per gli stili
        style_map = {
            "Normale": "normal",
            "Grassetto": "bold",
            "Corsivo": "italic",
            "Sottolineato": "underline",
        }

        # Imposta il font dell'area di testo con quello selezionato
        new_font = (self.selected_font_family.get(), font_size, \
                    style_map[self.selected_font_style.get()])
        self.text_area.config(font = new_font)

        # Chiude la relativa finestra
        self.font_window.destroy()

    def open_font_window(self):
        """
        Inizializza e visualizza la finestra di configurazione del carattere.
        
        Rileva automaticamente le impostazioni correnti del font
        (famiglia, stile, dimensione), popola i menu a tendina
        con i font di sistema disponibili e gestisce l'interazione 
        modale con l'utente.
        """
        # Crea una finestra per le impostazioni del font
        self.font_window = tk.Toplevel(self.master)
        self.font_window.transient(self.master)
        self.font_window.grab_set()
        self.font_window.focus_set()
        self.font_window.title("Carattere")
        self.font_window.geometry("500x130")
        self.font_window.resizable(False, False)

        # Imposta l'icona della finestra
        try:
            self.font_window.iconbitmap("icon.ico")
        except tk.TclError:
            pass

        # Ottiene le impostazioni correnti del font dell'area di testo
        current_font = font.Font(font = self.text_area['font'])
        current_family = current_font.actual()['family']
        current_weight = current_font.actual()['weight']
        current_slant = current_font.actual()['slant']
        current_underline = current_font.actual()['underline']
        current_size = current_font.actual()['size']

        # Converte gli stili in italiano
        weight_map = {"normal": "Normale", "bold": "Grassetto"}
        slant_map = {"roman": "Normale", "italic": "Corsivo"}
        underline_map = {0: "", 1: "Sottolineato"}

        # Determina lo stile corrente
        current_style = []
        if not current_style:
            current_style.append("Normale")
        if current_weight == "bold":
            current_style.append("Grassetto")
        elif current_slant == "italic":
            current_style.append("Corsivo")
        elif current_underline == 1:
            current_style.append("Sottolineato")
        current_style = " ".join(current_style)

        # Crea una lista di famiglie di font disponibili
        self.font_families = list(font.families())
        self.font_families.sort()

        # Crea degli attributi per il font selezionato
        self.selected_font_family = tk.StringVar(value = current_family)
        self.selected_font_style = tk.StringVar(value = current_style.strip())
        self.selected_font_size = tk.IntVar(value = str(current_size))

        # Crea un Frame per le Label
        label_frame = ttk.Frame(self.font_window)
        label_frame.pack(padx = 15, pady = (20, 0), fill = tk.X)

        # Crea un Frame per i Combobox
        combo_frame = ttk.Frame(self.font_window)
        combo_frame.pack(padx = 15, pady = (0, 10), fill = tk.X)
  
        # Crea una Label e un Combobox per la famiglia
        family_label = ttk.Label(label_frame, text = "Famiglia:")
        family_label.pack(side = tk.LEFT)
        family_combobox = ttk.Combobox(combo_frame, width = 30, \
                                       values = self.font_families, \
                                       textvariable = self.selected_font_family)
        family_combobox.pack(side = tk.LEFT)

        # Crea una Label e un Combobox per lo stile
        self.font_styles = ["Normale", "Grassetto", "Corsivo", "Sottolineato"]
        style_label = ttk.Label(label_frame, text = "Stile:")
        style_label.pack(padx = (160, 153), side = tk.LEFT)
        style_combobox = ttk.Combobox(combo_frame, width = 25, \
                                      values = self.font_styles, \
                                      textvariable = self.selected_font_style)
        style_combobox.pack(padx = 10, side = tk.LEFT)

        # Crea una Label e un Combobox per la dimensione
        font_sizes = ["8", "9", "10", "11", "12", "14", "16", "18", \
                      "20", "22", "24", "26", "28", "36", "48", "72"]
        size_label = ttk.Label(label_frame, text = "Dimensione:")
        size_label.pack(side = tk.LEFT)
        size_combobox = ttk.Combobox(combo_frame, width = 10, \
                                     values = font_sizes, \
                                     textvariable = self.selected_font_size)
        size_combobox.pack(side = tk.LEFT)

        # Crea un Frame per contenere i Button
        button_frame = ttk.Frame(self.font_window)
        button_frame.pack(padx = 15, pady = 10, \
                          anchor = tk.E, side = tk.BOTTOM)

        # Crea un Button per applicare il font e uno per annullare
        apply_button = ttk.Button(button_frame, text = "Applica", \
                                  width = 15, command = self.apply_font)
        apply_button.pack(side = tk.LEFT, padx = 10)

        cancel_button = ttk.Button(button_frame, text = "Annulla", width = 15, \
                                   command = self.font_window.destroy)
        cancel_button.pack(side = tk.LEFT)

        # Associa l'Invio alla finestra
        self.font_window.bind("<Return>", lambda event: self.apply_font())

    def toggle_status_bar(self):
        """
        Mostra o nasconde la barra di stato.
        
        Utilizza i metodi "grid_remove()" e "grid()" per gestire
        dinamicamente lo spazio occupato dal widget.
        """
        if self.status_bar.winfo_viewable():
            self.status_bar.grid_remove()
        else:
            self.status_bar.grid(row = 3, column = 0, sticky = "ew", \
                                 padx = 5, pady = 2)

    def toggle_word_wrap(self):
        """
        Attiva o disattiva il ritorno a capo automatico (Word Wrap).
        
        Quando attivo, il testo si adatta alla larghezza della finestra e la 
        barra di scorrimento orizzontale viene nascosta. Quando disattivato, 
        il testo prosegue sulla stessa riga e viene mostrata la scrollbar.
        """
        if self.word_wrap.get():
            self.text_area.config(wrap = tk.WORD)
            self.xscrollbar.grid_remove()
        else:
            self.text_area.config(wrap = tk.NONE)
            self.xscrollbar.grid(row = 1, column = 0, sticky = "ew", \
                                 padx = (0, 16))

    # METODI DEL MENU AIUTO
    # =====================
    def open_help_link(self):
        """
        Apre la documentazione di supporto dell'applicazione.
        
        Utilizza il browser predefinito del sistema per visualizzare il file 
        HTML locale contenente la guida e le istruzioni per l'utente.
        """
        browse("https://github.com/PyMarkCode03/SimpleNotes.py/blob/main/GuidaUtenteSimpleNotes/index.html")

    def open_info_window(self):
        """
        Crea e visualizza la finestra modale delle informazioni.
        
        Questa finestra mostra i dettagli del software, inclusi il nome, 
        la versione corrente, il copyright e il nome dell'autore.
        La finestra è impostata come modale (grab_set) per focalizzare 
        l'attenzione dell'utente.
        """
        # Crea una finestra per le informazioni
        info_window = tk.Toplevel(self.master)
        info_window.transient(self.master)
        info_window.grab_set()
        info_window.title("Informazioni su SimpleNotes")
        info_window.geometry("450x220")
        info_window.resizable(False, False)

        # Imposta l'icona della finestra
        try:
            info_window.iconbitmap("icon.ico")
        except tk.TclError:
            pass
        
        # Crea delle Label per mostrare le informazioni
        icon_img = tk.PhotoImage(file = "icon.png").subsample(12, 12)
        label_title = ttk.Label(info_window, text = "SimpleNotes", \
                                font = ("Arial", 20), image = icon_img, \
                                compound = tk.LEFT)
        label_version = ttk.Label(info_window, text = "Versione 1.0.0", \
                                  font = ("Arial", 10))
        label_copy = ttk.Label(info_window, \
                               text = "© 2024-2026 SimpleNotes. Tutti i diritti riservati.", \
                               font = ("Arial", 10))
        label_author = ttk.Label(info_window, text = "Autore: Marco Mazzo", \
                                 font = ("Arial", 10))

        label_title.image = icon_img
        label_title.pack(anchor = tk.W, padx = 40, pady = 20)
        label_version.pack(anchor = tk.W, padx = 40)
        label_copy.pack(anchor = tk.W, padx = 40, pady = 10)
        label_author.pack(anchor = tk.W, padx = 40)

        # Crea un Button per chiudere la finestra
        ok_button = ttk.Button(info_window, text = "OK", \
                               command = info_window.destroy)
        ok_button.pack(side = tk.BOTTOM, anchor = tk.E, \
                       padx = 5, pady = 5)
        ok_button.focus_set()
        ok_button.bind("<Return>", lambda event: info_window.destroy())

# Esecuzione dell'applicazione
if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleNotes(root)
    root.mainloop()
