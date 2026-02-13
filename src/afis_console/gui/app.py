import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import threading
import os
import sys

# Import the logic module
from afis_console.core import sorter as logic

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Trieur de Rapports FAED")
        self.geometry("700x500")
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        self.header_label = ctk.CTkLabel(self, text="Tri Automatique des Rapports", font=ctk.CTkFont(size=20, weight="bold"))
        self.header_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Selection Frame
        self.selection_frame = ctk.CTkFrame(self)
        self.selection_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.selection_frame.grid_columnconfigure(0, weight=1)

        self.folder_path = tk.StringVar()
        self.folder_entry = ctk.CTkEntry(self.selection_frame, textvariable=self.folder_path, placeholder_text="Dossier Source", state="readonly")
        self.folder_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.browse_button = ctk.CTkButton(self.selection_frame, text="Choisir Source", command=self.select_folder)
        self.browse_button.grid(row=0, column=1, padx=10, pady=10)

        # Destination Selection
        self.dest_path = tk.StringVar()
        self.dest_entry = ctk.CTkEntry(self.selection_frame, textvariable=self.dest_path, placeholder_text="Dossier Destination (Optionnel)", state="readonly")
        self.dest_entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.dest_button = ctk.CTkButton(self.selection_frame, text="Choisir Dest.", command=self.select_dest)
        self.dest_button.grid(row=1, column=1, padx=10, pady=10)

        # Action Button
        self.action_button = ctk.CTkButton(self.selection_frame, text="Lancer le Tri", command=self.start_process, state="disabled", fg_color="green")
        self.action_button.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        # Logs
        self.log_textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Courier", size=12))
        self.log_textbox.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.log_textbox.insert("0.0", "--- Journal d'exécution ---\n\n")

        # Footer
        self.footer_label = ctk.CTkLabel(self, text="Prêt", text_color="gray")
        self.footer_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")

    def select_folder(self):
        folder_selected = filedialog.askdirectory(title="Sélectionner le dossier contenant les rapports")
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.action_button.configure(state="normal")
            self.log_message(f"Source sélectionnée : {folder_selected}")

    def select_dest(self):
        folder_selected = filedialog.askdirectory(title="Sélectionner le dossier de destination (Optionnel)")
        if folder_selected:
            self.dest_path.set(folder_selected)
            self.log_message(f"Destination sélectionnée : {folder_selected}")

    def log_message(self, message):
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")

    def start_process(self):
        source_dir = self.folder_path.get()
        dest_dir = self.dest_path.get()
        if not source_dir or not os.path.exists(source_dir):
            self.log_message("Erreur : Dossier invalide.")
            return

        self.action_button.configure(state="disabled", text="En cours...")
        self.browse_button.configure(state="disabled")
        self.dest_button.configure(state="disabled") # Disable dest button too
        self.footer_label.configure(text="Traitement en cours...", text_color="orange")
        
        # Run in thread to not freeze UI
        thread = threading.Thread(target=self.run_logic, args=(source_dir, dest_dir))
        thread.start()

    def run_logic(self, source_dir, dest_dir):
        try:
            if logic:
                def safe_log(msg):
                    self.after(0, lambda: self.log_message(msg))

                stats = logic.process_folder(source_dir, log_callback=safe_log, destination_dir=dest_dir)
                
                self.after(0, lambda: self.finish_process(stats))
            else:
                self.after(0, lambda: self.log_message("Erreur critique : Module de logique introuvable."))
                self.after(0, lambda: self.finish_process(None))

        except Exception as e:
            self.after(0, lambda: self.log_message(f"Erreur inattendue : {e}"))
            self.after(0, lambda: self.finish_process(None))

    def finish_process(self, stats):
        self.action_button.configure(state="normal", text="Lancer le Tri")
        self.browse_button.configure(state="normal")
        self.dest_button.configure(state="normal")
        
        if stats:
             self.footer_label.configure(text=f"Terminé : {stats['ok']} OK, {stats['manual']} Manuels, {stats['error']} Erreurs", text_color="green")
        else:
             self.footer_label.configure(text="Terminé avec erreurs", text_color="red")
