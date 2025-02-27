# drl_config_window.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from drl_config import DRLConfiguration
import traceback

class DRLConfigWindow:
    def __init__(self, parent):
        print("DEBUG: Initializing DRL Config Window")
        self.drl_config = DRLConfiguration()
        self.window = tk.Toplevel(parent)
        self.window.title("DRL Configuration")
        self.window.geometry("900x700")
        
        # Create main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Modality selection
        modality_frame = ttk.LabelFrame(main_frame, text="Modality", padding="5")
        modality_frame.pack(fill=tk.X, pady=5)
        
        self.modality = tk.StringVar(value="CT")
        ttk.Radiobutton(modality_frame, text="CT", 
                       variable=self.modality, value="CT",
                       command=self.on_modality_change).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(modality_frame, text="DX", 
                       variable=self.modality, value="DX",
                       command=self.on_modality_change).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(modality_frame, text="XA", 
                       variable=self.modality, value="XA",
                       command=self.on_modality_change).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(modality_frame, text="MG", 
                       variable=self.modality, value="MG",
                       command=self.on_modality_change).pack(side=tk.LEFT, padx=10)
        
        # Split frame for list and configuration
        split_frame = ttk.Frame(main_frame)
        split_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Protocol List Frame (Left Side)
        list_frame = ttk.LabelFrame(split_frame, text="Protocols", padding="5")
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Protocol listbox with scrollbar
        self.protocol_list = tk.Listbox(list_frame, width=30, height=20)
        self.protocol_list.pack(side=tk.LEFT, fill=tk.Y)
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                     command=self.protocol_list.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.protocol_list.config(yscrollcommand=list_scrollbar.set)
        self.protocol_list.bind('<<ListboxSelect>>', self.on_protocol_select)
        
        # Protocol Control Buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Add", 
                  command=self.add_protocol).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", 
                  command=self.delete_protocol).pack(side=tk.LEFT, padx=2)
        
        # Configuration Frame (Right Side)
        self.config_frame = ttk.LabelFrame(split_frame, text="Protocol Configuration", 
                                         padding="5")
        self.config_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Protocol Name
        ttk.Label(self.config_frame, text="Protocol Name:").pack(anchor=tk.W, pady=2)
        self.protocol_name = ttk.Entry(self.config_frame)
        self.protocol_name.pack(fill=tk.X, pady=2)
        
        # Protocol Match Patterns
        ttk.Label(self.config_frame, 
                 text="Match Patterns (comma separated):").pack(anchor=tk.W, pady=2)
        self.match_patterns = ttk.Entry(self.config_frame)
        self.match_patterns.pack(fill=tk.X, pady=2)
        
        # Create frames for different modality configurations
        self.ct_frame = self.create_ct_frame()
        self.xray_frame = self.create_xray_frame()
        self.xa_frame = self.create_xa_frame()
        self.mammo_frame = self.create_mammo_frame()
        
        # Bottom Buttons
        button_frame = ttk.Frame(self.config_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Save Changes", 
                  command=self.save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Import from Excel", 
                  command=self.import_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export to Excel", 
                  command=self.export_excel).pack(side=tk.LEFT, padx=5)
        
        # Load initial protocols
        self.on_modality_change()
        print("DEBUG: DRL Config Window initialized")
    
    def create_ct_frame(self):
        """Create frame for CT-specific configuration"""
        print("DEBUG: Creating CT frame")
        frame = ttk.Frame(self.config_frame)
        
        # Adult DRL Values
        adult_frame = ttk.LabelFrame(frame, text="Adult DRL Values", padding="5")
        adult_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(adult_frame, text="DLP:").grid(row=0, column=0, padx=5)
        self.adult_dlp = ttk.Entry(adult_frame, width=10)
        self.adult_dlp.grid(row=0, column=1, padx=5)
        
        ttk.Label(adult_frame, text="CTDIvol:").grid(row=0, column=2, padx=5)
        self.adult_ctdi = ttk.Entry(adult_frame, width=10)
        self.adult_ctdi.grid(row=0, column=3, padx=5)
        
        # Children DRL Values
        child_frame = ttk.LabelFrame(frame, text="Children DRL Values", padding="5")
        child_frame.pack(fill=tk.X, pady=5)
        
        age_ranges = ["0-1", "1-5", "5-10", "10-15"]
        self.child_entries = {}
        
        for i, age_range in enumerate(age_ranges):
            ttk.Label(child_frame, text=f"Age {age_range}:").grid(row=i, column=0, 
                                                                padx=5, pady=2)
            
            ttk.Label(child_frame, text="DLP:").grid(row=i, column=1, padx=5)
            dlp_entry = ttk.Entry(child_frame, width=10)
            dlp_entry.grid(row=i, column=2, padx=5)
            
            ttk.Label(child_frame, text="CTDIvol:").grid(row=i, column=3, padx=5)
            ctdi_entry = ttk.Entry(child_frame, width=10)
            ctdi_entry.grid(row=i, column=4, padx=5)
            
            self.child_entries[age_range] = {"DLP": dlp_entry, "CTDIvol": ctdi_entry}
        
        return frame
    
    def create_xray_frame(self):
        """Create frame for Digital X-Ray specific configuration"""
        print("DEBUG: Creating DX frame")
        frame = ttk.Frame(self.config_frame)
        
        # Adult values
        adult_frame = ttk.LabelFrame(frame, text="Adult DRL Values", padding="5")
        adult_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(adult_frame, text="DAP (Gy·cm²):").grid(row=0, column=0, padx=5)
        self.adult_dap = ttk.Entry(adult_frame, width=10)
        self.adult_dap.grid(row=0, column=1, padx=5)
        
        ttk.Label(adult_frame, text="ESD (mGy):").grid(row=0, column=2, padx=5)
        self.adult_esd = ttk.Entry(adult_frame, width=10)
        self.adult_esd.grid(row=0, column=3, padx=5)
        
        # Child values
        child_frame = ttk.LabelFrame(frame, text="Child DRL Values", padding="5")
        child_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(child_frame, text="DAP (Gy·cm²):").grid(row=0, column=0, padx=5)
        self.child_dap = ttk.Entry(child_frame, width=10)
        self.child_dap.grid(row=0, column=1, padx=5)
        
        ttk.Label(child_frame, text="ESD (mGy):").grid(row=0, column=2, padx=5)
        self.child_esd = ttk.Entry(child_frame, width=10)
        self.child_esd.grid(row=0, column=3, padx=5)
        
        return frame
    
    def create_xa_frame(self):
        """Create frame for X-Ray Angiography specific configuration"""
        print("DEBUG: Creating XA frame")
        frame = ttk.Frame(self.config_frame)
        
        # Adult values
        adult_frame = ttk.LabelFrame(frame, text="Adult DRL Values", padding="5")
        adult_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(adult_frame, text="DAP (Gy·cm²):").grid(row=0, column=0, padx=5)
        self.adult_dap = ttk.Entry(adult_frame, width=10)
        self.adult_dap.grid(row=0, column=1, padx=5)
        
        ttk.Label(adult_frame, text="Air Kerma (mGy):").grid(row=0, column=2, padx=5)
        self.adult_airkerma = ttk.Entry(adult_frame, width=10)
        self.adult_airkerma.grid(row=0, column=3, padx=5)
        
        ttk.Label(adult_frame, text="Fluoro Time (s):").grid(row=1, column=0, padx=5)
        self.adult_fluorotime = ttk.Entry(adult_frame, width=10)
        self.adult_fluorotime.grid(row=1, column=1, padx=5)
        
        # Child values
        child_frame = ttk.LabelFrame(frame, text="Child DRL Values", padding="5")
        child_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(child_frame, text="DAP (Gy·cm²):").grid(row=0, column=0, padx=5)
        self.child_dap = ttk.Entry(child_frame, width=10)
        self.child_dap.grid(row=0, column=1, padx=5)
        
        ttk.Label(child_frame, text="Air Kerma (mGy):").grid(row=0, column=2, padx=5)
        self.child_airkerma = ttk.Entry(child_frame, width=10)
        self.child_airkerma.grid(row=0, column=3, padx=5)
        
        ttk.Label(child_frame, text="Fluoro Time (s):").grid(row=1, column=0, padx=5)
        self.child_fluorotime = ttk.Entry(child_frame, width=10)
        self.child_fluorotime.grid(row=1, column=1, padx=5)
        
        return frame
    
    def create_mammo_frame(self):
        """Create frame for Mammography specific configuration"""
        print("DEBUG: Creating MG frame")
        frame = ttk.Frame(self.config_frame)
        
        # Base AGD value
        base_frame = ttk.LabelFrame(frame, text="Base AGD Value", padding="5")
        base_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(base_frame, text="AGD (mGy):").grid(row=0, column=0, padx=5)
        self.base_agd = ttk.Entry(base_frame, width=10)
        self.base_agd.grid(row=0, column=1, padx=5)
        
        # Thickness-based values
        thickness_frame = ttk.LabelFrame(frame, text="AGD Values by Thickness (mm)", 
                                       padding="5")
        thickness_frame.pack(fill=tk.X, pady=5)
        
        self.thickness_entries = {}
        ranges = ['20-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90']
        
        for i, range_ in enumerate(ranges):
            ttk.Label(thickness_frame, 
                     text=f"{range_} mm:").grid(row=i//2, column=i%2*2, padx=5, pady=2)
            entry = ttk.Entry(thickness_frame, width=10)
            entry.grid(row=i//2, column=i%2*2+1, padx=5, pady=2)
            self.thickness_entries[range_] = entry
        
        return frame
    
    def on_modality_change(self):
        """Handle modality change"""
        print(f"DEBUG: Modality changed to {self.modality.get()}")
        # Hide all frames
        self.ct_frame.pack_forget()
        self.xray_frame.pack_forget()
        self.xa_frame.pack_forget()
        self.mammo_frame.pack_forget()
        
        # Show appropriate frame
        if self.modality.get() == "CT":
            self.ct_frame.pack(fill=tk.BOTH, expand=True)
        elif self.modality.get() == "DX":
            self.xray_frame.pack(fill=tk.BOTH, expand=True)
        elif self.modality.get() == "XA":
            self.xa_frame.pack(fill=tk.BOTH, expand=True)
        elif self.modality.get() == "MG":
            self.mammo_frame.pack(fill=tk.BOTH, expand=True)
        
        # Reload protocols list
        self.load_protocols()
    
    def load_protocols(self):
        """Load protocols for current modality"""
        print(f"DEBUG: Loading protocols for {self.modality.get()}")
        self.protocol_list.delete(0, tk.END)
        protocols = self.drl_config.get_all_protocols(self.modality.get())
        for protocol in protocols:
            self.protocol_list.insert(tk.END, protocol)
        print(f"DEBUG: Loaded {len(protocols)} protocols")
    
    def clear_form(self):
        """Clear all form fields"""
        print("DEBUG: Clearing form")
        self.protocol_name.delete(0, tk.END)
        self.match_patterns.delete(0, tk.END)
        
        modality = self.modality.get()
        if modality == "CT":
            self.adult_dlp.delete(0, tk.END)
            self.adult_ctdi.delete(0, tk.END)
            for entries in self.child_entries.values():
                entries['DLP'].delete(0, tk.END)
                entries['CTDIvol'].delete(0, tk.END)
        
        elif modality == "DX":
            self.adult_dap.delete(0, tk.END)
            self.adult_esd.delete(0, tk.END)
            self.child_dap.delete(0, tk.END)
            self.child_esd.delete(0, tk.END)
        
        elif modality == "XA":
            self.adult_dap.delete(0, tk.END)
            self.adult_airkerma.delete(0, tk.END)
            self.adult_fluorotime.delete(0, tk.END)
            self.child_dap.delete(0, tk.END)
            self.child_airkerma.delete(0, tk.END)
            self.child_fluorotime.delete(0, tk.END)
        
        elif modality == "MG":
            self.base_agd.delete(0, tk.END)
            for entry in self.thickness_entries.values():
                entry.delete(0, tk.END)
    
    def save_changes(self):
        """Save protocol changes"""
        protocol_name = self.protocol_name.get().strip()
        if not protocol_name:
            messagebox.showerror("Kļūda", "Nav norādīts protokola nosaukums")
            return
        
        try:
            data = {
                'protocol_match': [x.strip() for x in self.match_patterns.get().split(',') if x.strip()]
            }
            
            if not data['protocol_match']:
                messagebox.showerror("Kļūda", "Nav norādīti protokola atbilstības nosacījumi")
                return
            
            if self.modality.get() == "CT":
                data.update(self.get_ct_data())
            elif self.modality.get() == "DX":
                data.update(self.get_xray_data())
            elif self.modality.get() == "XA":
                data.update(self.get_xray_data())
            elif self.modality.get() == "MG":
                data.update(self.get_mammo_data())
            
            self.drl_config.add_protocol(self.modality.get(), protocol_name, data)
            self.load_protocols()
            messagebox.showinfo("Info", "Protokols veiksmīgi saglabāts")
        
        except ValueError as e:
            messagebox.showerror("Kļūda", f"Nederīga skaitliska vērtība: {str(e)}")
        except Exception as e:
            messagebox.showerror("Kļūda", f"Kļūda saglabājot protokolu: {str(e)}")
    
    def get_ct_data(self):
        """Get CT specific data from form"""
        # Pārbaudām, vai obligātie lauki ir aizpildīti
        if not self.adult_dlp.get() or not self.adult_ctdi.get():
            raise ValueError("Obligātie pieaugušo DRL lauki nav aizpildīti")
            
        data = {
            'adult': {
                'DLP': float(self.adult_dlp.get()),
                'CTDIvol': float(self.adult_ctdi.get())
            },
            'child': {}
        }
        
        for age_range, entries in self.child_entries.items():
            dlp = entries['DLP'].get()
            ctdi = entries['CTDIvol'].get()
            
            # Pārbaudām, vai abi lauki ir aizpildīti vai abi ir tukši
            if dlp and ctdi:
                data['child'][age_range] = {
                    'DLP': float(dlp),
                    'CTDIvol': float(ctdi)
                }
            elif dlp or ctdi:
                # Ja tikai viens no laukiem ir aizpildīts
                raise ValueError(f"Bērnu vecuma grupai {age_range} jāaizpilda abi lauki vai neviens")
        
        return data
    
    def get_xray_data(self):
        """Get X-Ray specific data from form"""
        # Pārbaudām, vai obligātie lauki ir aizpildīti
        if not self.adult_dap.get():
            raise ValueError("Obligātais pieaugušo DAP lauks nav aizpildīts")
            
        data = {
            'adult': {
                'DAP': float(self.adult_dap.get())
            },
            'child': {}
        }
        
        # Pievienojam neobligātos laukus, ja tie ir aizpildīti
        if self.adult_esd.get():
            data['adult']['ESD'] = float(self.adult_esd.get())
            
        if self.child_dap.get():
            data['child']['DAP'] = float(self.child_dap.get())
            
        if self.child_esd.get():
            data['child']['ESD'] = float(self.child_esd.get())
        
        return data
    
    def get_mammo_data(self):
        """Get Mammography specific data from form"""
        # Pārbaudām, vai obligātie lauki ir aizpildīti
        if not self.base_agd.get():
            raise ValueError("Obligātais AGD lauks nav aizpildīts")
            
        data = {
            'AGD': float(self.base_agd.get()),
            'thickness_ranges': {}
        }
        
        # Pievienojam neobligātos biezuma laukus, ja tie ir aizpildīti
        for range_, entry in self.thickness_entries.items():
            if entry.get():
                data['thickness_ranges'][range_] = float(entry.get())
        
        return data
    
    def import_excel(self):
        """Import protocols from Excel"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx")]
        )
        if file_path:
            try:
                success, message = self.drl_config.import_from_excel(self.modality.get(), file_path)
                if success:
                    self.load_protocols()
                    messagebox.showinfo("Info", message)
                else:
                    messagebox.showerror("Kļūda", message)
            except Exception as e:
                messagebox.showerror("Kļūda", f"Kļūda importējot datus: {str(e)}")
    
    def export_excel(self):
        """Export protocols to Excel"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if file_path:
            try:
                success, message = self.drl_config.export_to_excel(self.modality.get(), file_path)
                if success:
                    messagebox.showinfo("Info", message)
                else:
                    messagebox.showerror("Kļūda", message)
            except Exception as e:
                messagebox.showerror("Kļūda", f"Kļūda eksportējot datus: {str(e)}")
    
    def add_protocol(self):
        """Add new protocol"""
        self.clear_form()
    
    def delete_protocol(self):
        """Delete selected protocol"""
        selection = self.protocol_list.curselection()
        if selection:
            protocol = self.protocol_list.get(selection[0])
            if messagebox.askyesno("Apstiprināt dzēšanu", 
                                 f"Vai tiešām vēlaties dzēst protokolu {protocol}?"):
                try:
                    self.drl_config.delete_protocol(self.modality.get(), protocol)
                    self.load_protocols()
                    self.clear_form()
                except Exception as e:
                    messagebox.showerror("Kļūda", f"Kļūda dzēšot protokolu: {str(e)}")
    
    def on_protocol_select(self, event):
        """Handle protocol selection"""
        selection = self.protocol_list.curselection()
        if not selection:  # Ja nav nekas izvēlēts, atgriežamies
            return
            
        protocol = self.protocol_list.get(selection[0])
        try:
            data = self.drl_config.get_protocol(self.modality.get(), protocol)
            if not data:  # Ja nav datu, atgriežamies
                print(f"ERROR: No data found for protocol {protocol}")
                return
                
            self.clear_form()
            self.protocol_name.insert(0, protocol)
            
            # Pārbaudām, vai ir protocol_match dati
            if 'protocol_match' in data and isinstance(data['protocol_match'], list):
                self.match_patterns.insert(0, ','.join(data['protocol_match']))
            
            if self.modality.get() == "CT":
                self.fill_ct_data(data)
            elif self.modality.get() == "DX":
                self.fill_xray_data(data)
            elif self.modality.get() == "XA":
                self.fill_xa_data(data)
            elif self.modality.get() == "MG":
                self.fill_mammo_data(data)
        except Exception as e:
            print(f"ERROR loading protocol: {str(e)}")
            print(traceback.format_exc())
    
    def fill_ct_data(self, data):
        """Fill CT form with data"""
        try:
            # Aizpildām pieaugušo datus
            if 'adult' in data:
                if 'DLP' in data['adult']:
                    self.adult_dlp.insert(0, str(data['adult']['DLP']))
                if 'CTDIvol' in data['adult']:
                    self.adult_ctdi.insert(0, str(data['adult']['CTDIvol']))
            
            # Aizpildām bērnu datus
            if 'child' in data:
                for age_range, values in data['child'].items():
                    if age_range in self.child_entries:
                        if 'DLP' in values:
                            self.child_entries[age_range]['DLP'].insert(0, str(values['DLP']))
                        if 'CTDIvol' in values:
                            self.child_entries[age_range]['CTDIvol'].insert(0, str(values['CTDIvol']))
        except Exception as e:
            print(f"ERROR filling CT data: {str(e)}")
    
    def fill_xray_data(self, data):
        """Fill X-Ray form with data"""
        try:
            # Aizpildām pieaugušo datus
            if 'adult' in data:
                if 'DAP' in data['adult']:
                    self.adult_dap.insert(0, str(data['adult']['DAP']))
                if 'ESD' in data['adult'] and data['adult']['ESD'] is not None:
                    self.adult_esd.insert(0, str(data['adult']['ESD']))
            
            # Aizpildām bērnu datus
            if 'child' in data:
                if 'DAP' in data['child']:
                    self.child_dap.insert(0, str(data['child']['DAP']))
                if 'ESD' in data['child'] and data['child']['ESD'] is not None:
                    self.child_esd.insert(0, str(data['child']['ESD']))
        except Exception as e:
            print(f"ERROR filling X-Ray data: {str(e)}")
    
    def fill_xa_data(self, data):
        """Fill X-Ray Angiography form with data"""
        try:
            # Aizpildām pieaugušo datus
            if 'adult' in data:
                if 'DAP' in data['adult']:
                    self.adult_dap.insert(0, str(data['adult']['DAP']))
                if 'AirKerma' in data['adult'] and data['adult']['AirKerma'] is not None:
                    self.adult_airkerma.insert(0, str(data['adult']['AirKerma']))
                if 'FluoroTime' in data['adult'] and data['adult']['FluoroTime'] is not None:
                    self.adult_fluorotime.insert(0, str(data['adult']['FluoroTime']))
            
            # Aizpildām bērnu datus
            if 'child' in data:
                if 'DAP' in data['child']:
                    self.child_dap.insert(0, str(data['child']['DAP']))
                if 'AirKerma' in data['child'] and data['child']['AirKerma'] is not None:
                    self.child_airkerma.insert(0, str(data['child']['AirKerma']))
                if 'FluoroTime' in data['child'] and data['child']['FluoroTime'] is not None:
                    self.child_fluorotime.insert(0, str(data['child']['FluoroTime']))
        except Exception as e:
            print(f"ERROR filling XA data: {str(e)}")
    
    def fill_mammo_data(self, data):
        """Fill Mammography form with data"""
        try:
            # Aizpildām bāzes AGD vērtību
            if 'AGD' in data:
                self.base_agd.insert(0, str(data['AGD']))
            
            # Aizpildām biezuma atkarīgās vērtības
            if 'thickness_ranges' in data:
                for range_, value in data['thickness_ranges'].items():
                    if range_ in self.thickness_entries:
                        self.thickness_entries[range_].insert(0, str(value))
        except Exception as e:
            print(f"ERROR filling mammography data: {str(e)}")
