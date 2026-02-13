import sys
import argparse
import os
from afis_console.core.sorter import process_folder

def run_gui():
    try:
        import customtkinter as ctk
        from afis_console.gui.app import App
        
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        app = App()
        app.mainloop()
    except ImportError as e:
        print(f"Erreur lors du chargement de l'interface graphique : {e}")
        sys.exit(1)

def run_cli(args):
    source_dir = args.directory
    if not os.path.isdir(source_dir):
        print(f"Erreur : '{source_dir}' n'est pas un dossier valide.")
        sys.exit(1)
        
    print(f"Démarrage du tri en mode CLI pour : {source_dir}")
    process_folder(source_dir)

def main():
    parser = argparse.ArgumentParser(description="Tri Automatique des Rapports FAED")
    parser.add_argument("directory", nargs="?", help="Chemin du dossier à trier (Mode CLI). Si omis, lance l'interface graphique.")
    
    args = parser.parse_args()

    if args.directory:
        run_cli(args)
    else:
        run_gui()

if __name__ == "__main__":
    main()
