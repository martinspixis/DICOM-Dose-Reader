import os
import sys
import pydicom
import tkinter as tk
from tkinter import filedialog, messagebox
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

class DICOMRenamer:
    def __init__(self, root):
        self.root = root
        self.root.title("DICOM Failu Pārdēvētājs")
        self.root.geometry("600x400")
        self.setup_ui()
        
    def setup_ui(self):
        # Virsraksts
        title_label = tk.Label(self.root, text="DICOM Failu Pārdēvētājs", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        # Pamācība
        info_text = "Šī programma pārbauda visus failus izvēlētajā mapē, \n" + \
                    "identificē DICOM failus un pievieno tiem .dcm paplašinājumu."
        info_label = tk.Label(self.root, text=info_text, font=("Helvetica", 10))
        info_label.pack(pady=10)
        
        # Mapes izvēle
        frame = tk.Frame(self.root)
        frame.pack(pady=10, fill=tk.X, padx=20)
        
        self.folder_path = tk.StringVar()
        folder_label = tk.Label(frame, text="Izvēlētā mape:")
        folder_label.pack(side=tk.LEFT)
        
        folder_entry = tk.Entry(frame, textvariable=self.folder_path, width=40)
        folder_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_button = tk.Button(frame, text="Pārlūkot", command=self.browse_folder)
        browse_button.pack(side=tk.RIGHT)
        
        # Rekursīvās meklēšanas opcija
        self.recursive = tk.BooleanVar(value=True)
        recursive_check = tk.Checkbutton(self.root, text="Iekļaut apakšmapes", variable=self.recursive)
        recursive_check.pack(pady=5)
        
        # Opcija pārrakstīt esošos .dcm failus
        self.overwrite = tk.BooleanVar(value=False)
        overwrite_check = tk.Checkbutton(self.root, text="Pārrakstīt esošos .dcm failus", variable=self.overwrite)
        overwrite_check.pack(pady=5)
        
        # Progress
        self.progress_var = tk.StringVar(value="Gatavs darbam")
        progress_label = tk.Label(self.root, textvariable=self.progress_var)
        progress_label.pack(pady=10)
        
        # Protokols
        log_label = tk.Label(self.root, text="Darbību protokols:")
        log_label.pack(anchor=tk.W, padx=20)
        
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        self.log_text = tk.Text(log_frame, height=10, width=60)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Palaišanas poga
        start_button = tk.Button(self.root, text="Sākt pārdēvēšanu", command=self.start_renaming, 
                                width=20, bg="#4CAF50", fg="white")
        start_button.pack(pady=10)
    
    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.log("Izvēlēta mape: " + folder_selected)
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def is_dicom(self, file_path):
        """Pārbauda, vai fails ir DICOM formātā, lasot faila sākumu"""
        try:
            with open(file_path, 'rb') as f:
                # Pārlecat pirmos 128 baitus un pārbaudiet DICM marķieri
                f.seek(128)
                dicm_marker = f.read(4)
                if dicm_marker == b'DICM':
                    return True
                
                # Ja nav standarta DICM marķiera, mēģiniet nolasīt kā DICOM failu
                f.seek(0)
                try:
                    pydicom.dcmread(file_path, force=True, stop_before_pixels=True)
                    return True
                except:
                    return False
        except:
            return False
    
    def rename_file(self, file_path):
        """Pārdēvē vienu failu, pievienojot .dcm paplašinājumu, ja tas ir DICOM fails"""
        try:
            if self.is_dicom(file_path):
                base, ext = os.path.splitext(file_path)
                if ext.lower() != '.dcm':
                    new_path = base + '.dcm'
                    
                    # Pārbauda, vai jau eksistē fails ar .dcm paplašinājumu
                    if os.path.exists(new_path) and not self.overwrite.get():
                        return f"IZLAISTS (jau eksistē): {file_path}"
                    
                    os.rename(file_path, new_path)
                    return f"PĀRDĒVĒTS: {file_path} -> {new_path}"
                else:
                    return f"JAU DCM: {file_path}"
            else:
                return f"NAV DICOM: {file_path}"
        except Exception as e:
            return f"KĻŪDA pārdēvējot {file_path}: {str(e)}"

    def start_renaming(self):
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Kļūda", "Lūdzu, izvēlieties derīgu mapi!")
            return
        
        self.log("=== Sākam DICOM failu meklēšanu un pārdēvēšanu ===")
        self.progress_var.set("Darbojas: notiek failu meklēšana...")
        
        # Savākt visus failus
        all_files = []
        if self.recursive.get():
            for root, _, files in os.walk(folder):
                for filename in files:
                    all_files.append(os.path.join(root, filename))
        else:
            all_files = [os.path.join(folder, f) for f in os.listdir(folder) 
                        if os.path.isfile(os.path.join(folder, f))]
        
        total_files = len(all_files)
        self.log(f"Atrasti {total_files} faili pārbaudei")
        
        # Izmantojam vairākus pavedienus, lai paātrinātu procesu
        processed = 0
        dicom_files = 0
        renamed_files = 0
        
        with ThreadPoolExecutor(max_workers=min(10, os.cpu_count() + 4)) as executor:
            future_to_file = {executor.submit(self.rename_file, file): file for file in all_files}
            
            for future in as_completed(future_to_file):
                processed += 1
                result = future.result()
                self.log(result)
                
                if "PĀRDĒVĒTS" in result:
                    renamed_files += 1
                    dicom_files += 1
                elif "JAU DCM" in result:
                    dicom_files += 1
                
                self.progress_var.set(f"Apstrādāti {processed}/{total_files} faili")
        
        self.log(f"=== PABEIGTS ===")
        self.log(f"Kopā apstrādāti faili: {total_files}")
        self.log(f"Atrasti DICOM faili: {dicom_files}")
        self.log(f"Pārdēvēti faili: {renamed_files}")
        
        self.progress_var.set(f"Gatavs: pārdēvēti {renamed_files} faili")
        messagebox.showinfo("Pabeigts", f"Pārdēvēšana pabeigta!\nAtrasti {dicom_files} DICOM faili\nPārdēvēti {renamed_files} faili")

def main():
    root = tk.Tk()
    app = DICOMRenamer(root)
    root.mainloop()

if __name__ == "__main__":
    main()