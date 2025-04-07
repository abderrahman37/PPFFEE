import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import os
import pandas as pd
from database import get_table_names, get_table_data
from anonymization import detect_pii_columns, anonymize_pii, generate_anonymized_file

# Interface principale
class DatabaseViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sélecteur de Tables")
        
        # Dropdown pour la sélection des tables
        self.table_selector = ttk.Combobox(root, state="readonly")
        self.table_selector.pack(pady=10)
        
        # Bouton de chargement des tables
        self.load_button = tk.Button(root, text="Charger Table", command=self.show_table_data)
        self.load_button.pack()
        
        # Cadre pour afficher la table
        self.table_frame = tk.Frame(root)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bouton pour télécharger le fichier anonymisé
        self.download_button = tk.Button(root, text="Télécharger le fichier anonymisé", command=self.download_anonymized_file)
        self.download_button.pack(pady=20)  # Ajout du bouton avec un peu de marge
        
        self.load_table_names()

    def load_table_names(self):
        try:
            tables = get_table_names()
            self.table_selector["values"] = tables
            if tables:
                self.table_selector.current(0)  # Sélection par défaut
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de récupérer les tables : {e}")

    def show_table_data(self):
        table_name = self.table_selector.get()
        if not table_name:
            return
        try:
            df = get_table_data(table_name)
            pii_columns = detect_pii_columns(df)
            df = anonymize_pii(df, pii_columns)
            
            for widget in self.table_frame.winfo_children():
                widget.destroy()
            
            if df.empty:
                lbl = tk.Label(self.table_frame, text=f"La table {table_name} est vide.")
                lbl.pack()
            else:
                tree = ttk.Treeview(self.table_frame, columns=list(df.columns), show='headings')
                for col in df.columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=100)
                for _, row in df.iterrows():
                    tree.insert("", "end", values=list(row))
                tree.pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'afficher la table {table_name} : {e}")
    
    def download_anonymized_file(self):
        """
        Cette fonction génère un fichier anonymisé et permet à l'utilisateur de le télécharger.
        """
        try:
            # Exemple de récupération des données (cela pourrait être une sélection de table dans ton interface)
            table_name = self.table_selector.get()  # Utilisation du nom de la table sélectionnée
            if not table_name:
                messagebox.showwarning("Avertissement", "Veuillez sélectionner une table d'abord.")
                return
            
            df = get_table_data(table_name)  # Récupérer les données de la table
            
            # Générer le fichier anonymisé
            file_path = "anonymized_data.csv"  # Chemin par défaut pour le fichier généré
            anonymized_file_path = generate_anonymized_file(df, file_path)
            
            # Demander à l'utilisateur où enregistrer le fichier
            save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if save_path:
                # Copier le fichier anonymisé à l'emplacement choisi
                os.rename(anonymized_file_path, save_path)  # Déplacer le fichier
                messagebox.showinfo("Succès", f"Le fichier a été téléchargé avec succès à : {save_path}")
            else:
                messagebox.showwarning("Avertissement", "Aucun emplacement n'a été sélectionné pour le fichier.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseViewerApp(root)
    root.mainloop()



