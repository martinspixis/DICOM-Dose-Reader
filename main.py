# main.py
import os
import pydicom
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, date
import warnings
from tkcalendar import DateEntry
from xhtml2pdf import pisa
from jinja2 import Template
from drl_config import DRLConfiguration
from drl_config_window import DRLConfigWindow
import traceback

warnings.filterwarnings('ignore', category=UserWarning)
class DICOMDoseReader:
    def __init__(self, root):
        print("DEBUG: Initializing DICOMDoseReader")
        self.root = root
        self.root.title("DICOM Dose Data Reader")
        self.root.geometry("800x500")
        self.drl_config = DRLConfiguration()
        self.create_variables()
        self.setup_gui()
        print("DEBUG: Initialization complete")
        
    def create_variables(self):
        print("DEBUG: Creating variables")
        self.path_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.scan_subdirs = tk.BooleanVar(value=True)
        self.modality = tk.StringVar(value="CT")  # Default to CT
        self.data_source = tk.StringVar(value="RDSR")  # Default to RDSR
        self.debug_mode = tk.BooleanVar(value=True)  # DEBUG režīms pēc noklusējuma ieslēgts
        print("DEBUG: Variables created")
        
    def setup_gui(self):
        print("DEBUG: Setting up GUI")
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=20, pady=20)
        
        # Title section
        title_label = tk.Label(main_frame, 
                             text="DICOM Dose Reader\nPar šo visi PALDIES iet LRS medicīnas fiziķiem!",
                             font=("Helvetica", 16, "bold"),
                             fg="green")
        title_label.pack(pady=10)
        
        # Content frame
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Modality selection frame
        modality_frame = tk.LabelFrame(content_frame, text="Modality", padx=10, pady=5)
        modality_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(modality_frame, text="CT", 
                       variable=self.modality, value="CT",
                       command=self.update_status).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(modality_frame, text="DX", 
                       variable=self.modality, value="DX",
                       command=self.update_status).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(modality_frame, text="XA", 
                       variable=self.modality, value="XA",
                       command=self.update_status).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(modality_frame, text="MG", 
                       variable=self.modality, value="MG",
                       command=self.update_status).pack(side=tk.LEFT, padx=10)
        
        # Data source selection frame
        source_frame = tk.LabelFrame(content_frame, text="Data Source", padx=10, pady=5)
        source_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(source_frame, text="DICOM Image", 
                       variable=self.data_source, value="IMAGE",
                       command=self.update_status).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(source_frame, text="RDSR", 
                       variable=self.data_source, value="RDSR",
                       command=self.update_status).pack(side=tk.LEFT, padx=10)
        
        # Directory selection section
        tk.Label(content_frame, 
                text="Select DICOM directory",
                font=("Helvetica", 10)).pack(pady=10)
        
        browse_frame = tk.Frame(content_frame)
        browse_frame.pack(fill=tk.X)
        
        browse_btn = tk.Button(browse_frame, 
                             text="Browse", 
                             command=self.select_directory,
                             width=20,
                             relief=tk.GROOVE)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Label(browse_frame, 
                textvariable=self.path_var,
                wraplength=500).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Date range frame
        date_frame = tk.LabelFrame(content_frame, text="Date Range", padx=10, pady=5)
        date_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(date_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.date_from = DateEntry(date_frame, width=12,
                                 background='darkblue', foreground='white',
                                 date_pattern='dd.mm.yyyy')
        self.date_from.pack(side=tk.LEFT, padx=2)
        
        tk.Label(date_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.date_to = DateEntry(date_frame, width=12,
                               background='darkblue', foreground='white',
                               date_pattern='dd.mm.yyyy')
        self.date_to.pack(side=tk.LEFT, padx=2)
        
        clear_btn = tk.Button(date_frame, text="Clear", 
                            command=self.clear_dates,
                            relief=tk.GROOVE)
        clear_btn.pack(side=tk.LEFT, padx=10)
        
        # Options frame
        options_frame = tk.Frame(content_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        tk.Checkbutton(options_frame, 
                      text="Include subdirectories", 
                      variable=self.scan_subdirs,
                      font=("Helvetica", 10)).pack(side=tk.LEFT)
        
        # Debug mode checkbox
        debug_cb = tk.Checkbutton(options_frame, 
                                text="DEBUG mode", 
                                variable=self.debug_mode,
                                command=self.toggle_debug,
                                font=("Helvetica", 10))
        debug_cb.pack(side=tk.LEFT, padx=15)
        
        # DRL Configuration button
        drl_config_btn = tk.Button(options_frame, 
                                 text="DRL Config", 
                                 command=self.open_drl_config,
                                 relief=tk.GROOVE)
        drl_config_btn.pack(side=tk.RIGHT, padx=5)
        
        # Process button and status
        self.process_btn = tk.Button(content_frame, 
                                   text="Process Files", 
                                   command=self.process_files,
                                   state=tk.DISABLED,
                                   width=20,
                                   relief=tk.GROOVE)
        self.process_btn.pack(pady=10)
        
        # Status bar with modality and source info
        status_frame = tk.Frame(content_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(status_frame, 
                                   textvariable=self.status_var,
                                   font=("Helvetica", 10))
        self.status_label.pack(pady=5)
        print("DEBUG: GUI setup complete")
    def toggle_debug(self):
        """Ieslēgt vai izslēgt DEBUG režīmu"""
        debug_status = "ON" if self.debug_mode.get() else "OFF"
        print(f"DEBUG mode: {debug_status}")
        # Atjaunojam status bar ar informāciju par debug režīmu
        self.update_status()

    def update_status(self):
        """Update status bar with current modality and source"""
        modality = self.modality.get()
        source = "RDSR" if self.data_source.get() == "RDSR" else "Image"
        debug_info = " [DEBUG mode ON]" if self.debug_mode.get() else ""
        self.status_var.set(f"Ready to process {modality} {source} files{debug_info}")
        if self.debug_mode.get():
            print(f"DEBUG: Status updated - {modality} {source}")

    def select_directory(self):
        """Select directory with DICOM files"""
        directory = filedialog.askdirectory()
        if directory:
            if self.debug_mode.get():
                print(f"DEBUG: Selected directory: {directory}")
            self.path_var.set(directory)
            self.process_btn['state'] = tk.NORMAL
            self.status_var.set("Ready to process files")
    
    def clear_dates(self):
        """Clear date fields"""
        if self.debug_mode.get():
            print("DEBUG: Clearing dates")
        self.date_from.set_date(None)
        self.date_to.set_date(None)
    
    def open_drl_config(self):
        """Open DRL configuration window"""
        if self.debug_mode.get():
            print("DEBUG: Opening DRL configuration window")
        DRLConfigWindow(self.root)
    def find_dicom_files(self, directory):
        """Find DICOM files in directory"""
        if self.debug_mode.get():
            print("\nDEBUG: Starting DICOM file search")
        dicom_files = []
        try:
            # Parse date range
            if self.date_from.get():
                date_from = datetime.strptime(self.date_from.get(), '%d.%m.%Y').date()
                if self.debug_mode.get():
                    print(f"DEBUG: Start date: {date_from}")
            else:
                date_from = None
                if self.debug_mode.get():
                    print("DEBUG: No start date specified")
                
            if self.date_to.get():
                date_to = datetime.strptime(self.date_to.get(), '%d.%m.%Y').date()
                if self.debug_mode.get():
                    print(f"DEBUG: End date: {date_to}")
            else:
                date_to = None
                if self.debug_mode.get():
                    print("DEBUG: No end date specified")
        except (ValueError, TypeError) as e:
            if self.debug_mode.get():
                print(f"DEBUG: Date parsing error - {str(e)}")
            messagebox.showerror("Error", "Invalid date format")
            return []
            
        # Search files
        if self.scan_subdirs.get():
            if self.debug_mode.get():
                print("DEBUG: Scanning subdirectories")
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(('.dcm', '.DCM')):
                        file_path = os.path.join(root, file)
                        try:
                            dcm = pydicom.dcmread(file_path)
                            if self.check_dicom_type(dcm):
                                study_date = dcm.get('StudyDate', '')
                                if study_date:
                                    file_date = datetime.strptime(study_date, '%Y%m%d').date()
                                    if ((not date_from or file_date >= date_from) and 
                                        (not date_to or file_date <= date_to)):
                                        dicom_files.append(file_path)
                                        if self.debug_mode.get():
                                            print(f"DEBUG: Found matching file: {file_path}")
                        except Exception as e:
                            if self.debug_mode.get():
                                print(f"DEBUG: Error reading file {file_path}: {str(e)}")
                            continue
        else:
            if self.debug_mode.get():
                print("DEBUG: Scanning only root directory")
            for file in os.listdir(directory):
                if file.endswith(('.dcm', '.DCM')):
                    file_path = os.path.join(directory, file)
                    try:
                        dcm = pydicom.dcmread(file_path)
                        if self.check_dicom_type(dcm):
                            study_date = dcm.get('StudyDate', '')
                            if study_date:
                                file_date = datetime.strptime(study_date, '%Y%m%d').date()
                                if ((not date_from or file_date >= date_from) and 
                                    (not date_to or file_date <= date_to)):
                                    dicom_files.append(file_path)
                                    if self.debug_mode.get():
                                        print(f"DEBUG: Found matching file: {file_path}")
                    except Exception as e:
                        if self.debug_mode.get():
                            print(f"DEBUG: Error reading file {file_path}: {str(e)}")
                        continue
        
        if self.debug_mode.get():
            print(f"DEBUG: Found {len(dicom_files)} matching DICOM files")
        return dicom_files

    def check_dicom_type(self, dcm):
        """Check if DICOM file matches selected modality and source type"""
        modality = self.modality.get()
        data_source = self.data_source.get()
        
        dcm_modality = dcm.get('Modality', '')
        if self.debug_mode.get():
            print(f"DEBUG: Checking DICOM type - File modality: {dcm_modality}, Required: {modality}")
        
        if data_source == "RDSR":
            if self.debug_mode.get():
                print("DEBUG: Checking for RDSR")
            return dcm_modality == "SR"
        else:  # IMAGE
            if self.debug_mode.get():
                print("DEBUG: Checking for Image")
            return dcm_modality == modality
    def process_files(self):
        """Process DICOM files based on selected modality and source"""
        if self.debug_mode.get():
            print("\nDEBUG: Starting file processing")
        modality = self.modality.get()
        data_source = self.data_source.get()
        
        self.status_var.set(f"Processing {modality} files from {data_source}...")
        if self.debug_mode.get():
            print(f"DEBUG: Processing {modality} files from {data_source}")
        
        directory = self.path_var.get()
        dicom_files = self.find_dicom_files(directory)
        
        if not dicom_files:
            if self.debug_mode.get():
                print("DEBUG: No valid DICOM files found")
            messagebox.showerror("Error", "No valid DICOM files found")
            return
        
        results = []
        for file_path in dicom_files:
            if self.debug_mode.get():
                print(f"\nDEBUG: Processing file: {file_path}")
            data = None
            if data_source == "RDSR":
                data = self.extract_rdsr_data(file_path)
            else:  # IMAGE
                if modality == "CT":
                    data = self.extract_ct_dose_data(file_path)
                elif modality == "XA":
                    data = self.extract_xa_dose_data(file_path)
                elif modality == "MG":
                    data = self.extract_mg_dose_data(file_path)
                elif modality == "DX":
                    data = self.extract_dx_dose_data(file_path)
            
            if data:
                if self.debug_mode.get():
                    print("DEBUG: Successfully extracted data")
                results.append(data)
            else:
                if self.debug_mode.get():
                    print("DEBUG: Failed to extract data")
        
        if not results:
            if self.debug_mode.get():
                print("DEBUG: No valid data found in files")
            messagebox.showerror("Error", "No valid data found")
            return

        self.save_results(results)
        if self.debug_mode.get():
            print("DEBUG: File processing complete")
    def extract_patient_data(self, dcm):
        """Extract common patient data from DICOM file"""
        if self.debug_mode.get():
            print("\nDEBUG: Extracting patient data")
        patient_data = {
            'File': os.path.basename(dcm.filename),
            'Modality': dcm.get('Modality', ''),
            'Manufacturer': dcm.get('Manufacturer', ''),
            'DeviceObserverModelName': dcm.get('DeviceObserverModelName', ''),
            'StationName': dcm.get('StationName', ''),
            'PatientName': str(dcm.get('PatientName', '')),
            'PatientID': dcm.get('PatientID', ''),
            'PatientSex': dcm.get('PatientSex', ''),
            'PatientBirthDate': dcm.get('PatientBirthDate', ''),
            'PatientAge': dcm.get('PatientAge', ''),
            'PatientWeight': dcm.get('PatientWeight', None),
            'PatientSize': dcm.get('PatientSize', None),
            'StudyDate': dcm.get('StudyDate', ''),
            'StudyTime': dcm.get('StudyTime', ''),
            'StudyDescription': dcm.get('StudyDescription', ''),
            'BodyPartExamined': dcm.get('BodyPartExamined', '')
        }
        
        if patient_data['PatientBirthDate']:
            try:
                birth_date = datetime.strptime(patient_data['PatientBirthDate'], '%Y%m%d').date()
                study_date = datetime.strptime(dcm.get('StudyDate', date.today().strftime('%Y%m%d')), '%Y%m%d').date()
                patient_data['CalculatedAge'] = (study_date - birth_date).days // 365
                if self.debug_mode.get():
                    print(f"DEBUG: Calculated age: {patient_data['CalculatedAge']}")
            except Exception as e:
                if self.debug_mode.get():
                    print(f"DEBUG: Error calculating age: {str(e)}")
        
        if self.debug_mode.get():
            print("DEBUG: Patient data extracted successfully")
        return patient_data

    def extract_rdsr_data(self, file_path):
        """Extract dose data from RDSR DICOM file"""
        if self.debug_mode.get():
            print("\nDEBUG: Starting RDSR data extraction")
        try:
            dcm = pydicom.dcmread(file_path)
            
            if dcm.get('Modality', '') != 'SR':
                if self.debug_mode.get():
                    print("DEBUG: Not an RDSR file")
                return None
                
            patient_data = self.extract_patient_data(dcm)
            
            if hasattr(dcm, 'ContentSequence'):
                if self.debug_mode.get():
                    print("DEBUG: Processing RDSR content sequence")
                self.process_content_sequence(dcm.ContentSequence, patient_data)
            else:
                if self.debug_mode.get():
                    print("DEBUG: No content sequence found")
            
            return patient_data
        except Exception as e:
            if self.debug_mode.get():
                print(f"DEBUG: Error processing RDSR file: {str(e)}")
                print(f"DEBUG: Full error: {traceback.format_exc()}")
            return None

    def process_content_sequence(self, sequence, patient_data):
        """Process DICOM SR content sequence"""
        if self.debug_mode.get():
            print("\nDEBUG: Processing content sequence")
        if not sequence:
            if self.debug_mode.get():
                print("DEBUG: Empty sequence")
            return
            
        for content_item in sequence:
            if hasattr(content_item, 'ConceptNameCodeSequence'):
                concept_name = content_item.ConceptNameCodeSequence[0].CodeMeaning
                if self.debug_mode.get():
                    print(f"DEBUG: Found concept: {concept_name}")
                
                if 'Acquisition Protocol' in concept_name and hasattr(content_item, 'TextValue'):
                    patient_data['AcquisitionProtocol'] = str(content_item.TextValue)
                    if self.debug_mode.get():
                        print(f"DEBUG: Protocol: {patient_data['AcquisitionProtocol']}")
                elif 'Mean CTDIvol' in concept_name and hasattr(content_item, 'MeasuredValueSequence'):
                    try:
                        patient_data['CTDIvol'] = float(content_item.MeasuredValueSequence[0].NumericValue)
                        if self.debug_mode.get():
                            print(f"DEBUG: CTDIvol: {patient_data['CTDIvol']}")
                    except:
                        if self.debug_mode.get():
                            print("DEBUG: Error extracting CTDIvol")
                elif 'DLP' in concept_name and hasattr(content_item, 'MeasuredValueSequence'):
                    try:
                        patient_data['TotalDLP'] = float(content_item.MeasuredValueSequence[0].NumericValue)
                        if self.debug_mode.get():
                            print(f"DEBUG: DLP: {patient_data['TotalDLP']}")
                    except:
                        if self.debug_mode.get():
                            print("DEBUG: Error extracting DLP")
                elif 'Dose Area Product' in concept_name and hasattr(content_item, 'MeasuredValueSequence'):
                    try:
                        patient_data['TotalDoseAreaProduct'] = float(content_item.MeasuredValueSequence[0].NumericValue)
                        if self.debug_mode.get():
                            print(f"DEBUG: DAP: {patient_data['TotalDoseAreaProduct']}")
                    except:
                        if self.debug_mode.get():
                            print("DEBUG: Error extracting DAP")
                elif 'Average Glandular Dose' in concept_name and hasattr(content_item, 'MeasuredValueSequence'):
                    try:
                        patient_data['AverageGlandularDose'] = float(content_item.MeasuredValueSequence[0].NumericValue)
                        if self.debug_mode.get():
                            print(f"DEBUG: AGD: {patient_data['AverageGlandularDose']}")
                    except:
                        if self.debug_mode.get():
                            print("DEBUG: Error extracting AGD")
                        
            if hasattr(content_item, 'ContentSequence'):
                self.process_content_sequence(content_item.ContentSequence, patient_data)
    def extract_ct_dose_data(self, file_path):
        """Extract dose data from CT DICOM image file"""
        if self.debug_mode.get():
            print("\nDEBUG: Starting CT dose data extraction")
        try:
            dcm = pydicom.dcmread(file_path)
            
            if dcm.get('Modality', '') != 'CT':
                if self.debug_mode.get():
                    print("DEBUG: Not a CT image")
                return None
                
            patient_data = self.extract_patient_data(dcm)
            
            # CT specific exposure data
            if self.debug_mode.get():
                print("DEBUG: Extracting CT-specific data")
            patient_data.update({
                'ScanningLength': dcm.get('DataCollectionDiameter', ''),
                'ExposureTime': dcm.get('ExposureTime', ''),
                'KVP': dcm.get('KVP', ''),
                'TubeCurrent': dcm.get('XRayTubeCurrent', ''),
                'Exposure': dcm.get('Exposure', ''),
                'ExposureInuAs': dcm.get('ExposureInuAs', ''),
                'CTDIvol': self.get_ctdi_vol(dcm),
                'DLP': self.get_dlp(dcm),
                'ScanOptions': dcm.get('ScanOptions', ''),
                'AcquisitionType': dcm.get('AcquisitionType', ''),
                'ProtocolName': dcm.get('ProtocolName', ''),
                'SeriesDescription': dcm.get('SeriesDescription', '')
            })
            
            if self.debug_mode.get():
                print("DEBUG: CT dose data extracted successfully")
            return patient_data
        except Exception as e:
            if self.debug_mode.get():
                print(f"DEBUG: Error processing CT file: {str(e)}")
                print(f"DEBUG: Full error: {traceback.format_exc()}")
            return None

    def extract_dx_dose_data(self, file_path):
        """Extract dose data from Digital X-Ray DICOM file"""
        if self.debug_mode.get():
            print("\nDEBUG: Starting DX dose data extraction")
        try:
            dcm = pydicom.dcmread(file_path)
            
            if dcm.get('Modality', '') != 'DX':
                if self.debug_mode.get():
                    print("DEBUG: Not a DX image")
                return None
                
            patient_data = self.extract_patient_data(dcm)
            
            # DX specific exposure data
            if self.debug_mode.get():
                print("DEBUG: Extracting DX-specific data")
            patient_data.update({
                'KVP': dcm.get('KVP', ''),
                'ExposureTime': dcm.get('ExposureTime', ''),
                'XRayTubeCurrent': dcm.get('XRayTubeCurrent', ''),
                'Exposure': dcm.get('Exposure', ''),
                'ExposureInuAs': dcm.get('ExposureInuAs', ''),
                'ImageAndFluoroscopyAreaDoseProduct': dcm.get('ImageAndFluoroscopyAreaDoseProduct', ''),
                'EntranceDose': self.calculate_entrance_dose(dcm),
                'DistanceSourceToDetector': dcm.get('DistanceSourceToDetector', ''),
                'DistanceSourceToPatient': dcm.get('DistanceSourceToPatient', ''),
                'ImageLaterality': dcm.get('ImageLaterality', ''),
                'ViewPosition': dcm.get('ViewPosition', ''),
                'ProtocolName': dcm.get('ProtocolName', ''),
                'SeriesDescription': dcm.get('SeriesDescription', ''),
                'Grid': dcm.get('Grid', ''),
                'ExposureControlMode': dcm.get('ExposureControlMode', '')
            })
            
            if self.debug_mode.get():
                print("DEBUG: DX dose data extracted successfully")
                print(f"DEBUG: Protocol Name: {patient_data['ProtocolName']}")
                print(f"DEBUG: DAP: {patient_data['ImageAndFluoroscopyAreaDoseProduct']}")
            return patient_data
        except Exception as e:
            if self.debug_mode.get():
                print(f"DEBUG: Error processing DX file: {str(e)}")
                print(f"DEBUG: Full error: {traceback.format_exc()}")
            return None

    def extract_xa_dose_data(self, file_path):
        """Extract dose data from X-Ray Angiography DICOM file"""
        if self.debug_mode.get():
            print("\nDEBUG: Starting XA dose data extraction")
        try:
            dcm = pydicom.dcmread(file_path)
            
            if dcm.get('Modality', '') != 'XA':
                if self.debug_mode.get():
                    print("DEBUG: Not an XA image")
                return None
                
            patient_data = self.extract_patient_data(dcm)
            
            # XA specific exposure data
            if self.debug_mode.get():
                print("DEBUG: Extracting XA-specific data")
            patient_data.update({
                'KVP': dcm.get('KVP', ''),
                'ExposureTime': dcm.get('ExposureTime', ''),
                'XRayTubeCurrent': dcm.get('XRayTubeCurrent', ''),
                'Exposure': dcm.get('Exposure', ''),
                'DoseAreaProduct': dcm.get('DoseAreaProduct', ''),
                'TotalFluoroTime': dcm.get('FluoroscopyTime', ''),
                'TotalNumberOfExposures': dcm.get('NumberOfExposures', ''),
                'TotalDoseAreaProduct': self.get_total_dap(dcm),
                'ReferencePointAirKerma': dcm.get('ReferencePointAirKerma', ''),
                'DistanceSourceToIsocenter': dcm.get('DistanceSourceToIsocenter', ''),
                'DistanceSourceToReference': dcm.get('DistanceSourceToReference', ''),
                'TableHeight': dcm.get('TableHeight', ''),
                'ProtocolName': dcm.get('ProtocolName', ''),
                'SeriesDescription': dcm.get('SeriesDescription', ''),
                'AcquisitionProtocol': dcm.get('AcquisitionProtocol', '')
            })
            
            if self.debug_mode.get():
                print("DEBUG: XA dose data extracted successfully")
            return patient_data
        except Exception as e:
            if self.debug_mode.get():
                print(f"DEBUG: Error processing XA file: {str(e)}")
                print(f"DEBUG: Full error: {traceback.format_exc()}")
            return None
            
    def extract_mg_dose_data(self, file_path):
        """Extract dose data from Mammography DICOM file"""
        if self.debug_mode.get():
            print("\nDEBUG: Starting MG dose data extraction")
        try:
            dcm = pydicom.dcmread(file_path)
            
            if dcm.get('Modality', '') != 'MG':
                if self.debug_mode.get():
                    print("DEBUG: Not an MG image")
            return None
               
            patient_data = self.extract_patient_data(dcm)
            
            # MG specific exposure data
            if self.debug_mode.get():
                print("DEBUG: Extracting MG-specific data")
            patient_data.update({
                'KVP': dcm.get('KVP', ''),
                'ExposureTime': dcm.get('ExposureTime', ''),
                'XRayTubeCurrent': dcm.get('XRayTubeCurrent', ''),
                'Exposure': dcm.get('Exposure', ''),
                'EntranceDose': dcm.get('EntranceDose', ''),
                'OrganDose': dcm.get('OrganDose', ''),
                'RelativeXRayExposure': dcm.get('RelativeXRayExposure', ''),
                'CompressionForce': dcm.get('CompressionForce', ''),
                'CompressionPressure': dcm.get('CompressionPressure', ''),
                'BodyPartThickness': dcm.get('BodyPartThickness', ''),
                'ExposureControlMode': dcm.get('ExposureControlMode', ''),
                'AnodeTargetMaterial': dcm.get('AnodeTargetMaterial', ''),
                'FilterMaterial': dcm.get('FilterMaterial', ''),
                'GridFocalDistance': dcm.get('GridFocalDistance', ''),
                'ImageLaterality': dcm.get('ImageLaterality', ''),
                'ViewPosition': dcm.get('ViewPosition', ''),
                'SeriesDescription': dcm.get('SeriesDescription', ''),
                'AcquisitionProtocol': dcm.get('AcquisitionProtocol', '')
            })
            
            if self.debug_mode.get():
                print("DEBUG: MG dose data extracted successfully")
            return patient_data
        except Exception as e:
            if self.debug_mode.get():
                print(f"DEBUG: Error processing MG file: {str(e)}")
                print(f"DEBUG: Full error: {traceback.format_exc()}")
            return None
    def get_ctdi_vol(self, dcm):
        """Extract CTDIvol from various DICOM tags"""
        if self.debug_mode.get():
            print("DEBUG: Extracting CTDIvol")
        try:
            if hasattr(dcm, 'CTDIvol'):
                value = float(dcm.CTDIvol)
                if self.debug_mode.get():
                    print(f"DEBUG: CTDIvol found: {value}")
                return value
            elif hasattr(dcm, 'ExposureDoseSequence'):
                for item in dcm.ExposureDoseSequence:
                    if hasattr(item, 'CTDIvol'):
                        value = float(item.CTDIvol)
                        if self.debug_mode.get():
                            print(f"DEBUG: CTDIvol found in sequence: {value}")
                        return value
        except Exception as e:
            if self.debug_mode.get():
                print(f"DEBUG: Error extracting CTDIvol: {str(e)}")
        return None

    def get_dlp(self, dcm):
        """Extract DLP from various DICOM tags"""
        if self.debug_mode.get():
            print("DEBUG: Extracting DLP")
        try:
            if hasattr(dcm, 'DLP'):
                value = float(dcm.DLP)
                if self.debug_mode.get():
                    print(f"DEBUG: DLP found: {value}")
                return value
            elif hasattr(dcm, 'ExposureDoseSequence'):
                for item in dcm.ExposureDoseSequence:
                    if hasattr(item, 'DLP'):
                        value = float(item.DLP)
                        if self.debug_mode.get():
                            print(f"DEBUG: DLP found in sequence: {value}")
                        return value
        except Exception as e:
            if self.debug_mode.get():
                print(f"DEBUG: Error extracting DLP: {str(e)}")
        return None

    def get_total_dap(self, dcm):
        """Calculate total DAP from available data"""
        if self.debug_mode.get():
            print("DEBUG: Calculating total DAP")
        try:
            if hasattr(dcm, 'DoseAreaProduct'):
                value = float(dcm.DoseAreaProduct)
                if self.debug_mode.get():
                    print(f"DEBUG: DAP found: {value}")
                return value
            elif hasattr(dcm, 'ImageAndFluoroscopyAreaDoseProduct'):
                value = float(dcm.ImageAndFluoroscopyAreaDoseProduct)
                if self.debug_mode.get():
                    print(f"DEBUG: DAP found in ImageAndFluoroscopy: {value}")
                return value
        except Exception as e:
            if self.debug_mode.get():
                print(f"DEBUG: Error calculating DAP: {str(e)}")
        return None

    def calculate_entrance_dose(self, dcm):
        """Calculate entrance dose if possible"""
        if self.debug_mode.get():
            print("DEBUG: Calculating entrance dose")
        try:
            if hasattr(dcm, 'EntranceDose'):
                value = float(dcm.EntranceDose)
                if self.debug_mode.get():
                    print(f"DEBUG: Entrance dose found: {value}")
                return value
            elif all(hasattr(dcm, attr) for attr in ['Exposure', 'DistanceSourceToPatient']):
                exposure = float(dcm.Exposure)
                distance = float(dcm.DistanceSourceToPatient)
                value = exposure * (100/distance)**2 * 0.01  # Convert to mGy
                if self.debug_mode.get():
                    print(f"DEBUG: Calculated entrance dose: {value}")
                return value
        except Exception as e:
            if self.debug_mode.get():
                print(f"DEBUG: Error calculating entrance dose: {str(e)}")
        return None
    def calculate_drl_comparison(self, df):
        """Calculate DRL comparison data for the report"""
        if self.debug_mode.get():
            print("\nDEBUG: Starting DRL comparison calculation")
            print("Input DataFrame:")
            print(df.head())
            print("\nDataFrame columns:", df.columns.tolist())
        
        comparison_data = []
        modality = self.modality.get()
        if self.debug_mode.get():
            print(f"\nDEBUG: Processing {modality} data")
        
        try:
            if modality == "CT":
                grouped_stats = df.groupby('AcquisitionProtocol').agg({
                    'TotalDLP': 'mean',
                    'CTDIvol': 'mean',
                    'DeviceObserverModelName': 'first'
                }).round(2)
                
            elif modality in ["XA", "DX"]:
                grouped_stats = df.groupby('ProtocolName').agg({
                    'ImageAndFluoroscopyAreaDoseProduct': 'mean',
                    'EntranceDose': 'mean',
                    'DeviceObserverModelName': 'first'
                }).round(2)
                
            elif modality == "MG":
                grouped_stats = df.groupby(['AcquisitionProtocol', 'BodyPartThickness']).agg({
                    'OrganDose': 'mean',
                    'EntranceDose': 'mean',
                    'DeviceObserverModelName': 'first'
                }).round(2)
            
            if self.debug_mode.get():
                print("\nDEBUG: Grouped statistics:")
                print(grouped_stats)
            
            # Process each protocol
            for protocol, stats in grouped_stats.iterrows():
                if self.debug_mode.get():
                    print(f"\nDEBUG: Processing protocol: {protocol}")
                drl_protocol, drl_data = self.drl_config.get_matching_protocol(modality, protocol)
                if self.debug_mode.get():
                    print(f"DEBUG: DRL data found: {drl_data}")
                
                if drl_data:
                    if modality == "CT":
                        self.add_ct_comparison(comparison_data, protocol, stats, drl_data, df)
                    elif modality in ["XA", "DX"]:
                        self.add_xray_comparison(comparison_data, protocol, stats, drl_data, df)
                    elif modality == "MG":
                        self.add_mg_comparison(comparison_data, protocol[0], protocol[1], stats, drl_data)
        
        except Exception as e:
            if self.debug_mode.get():
                print(f"DEBUG: Error in comparison calculation: {str(e)}")
                print(f"DEBUG: Full error: {traceback.format_exc()}")
        
        if self.debug_mode.get():
            print("\nDEBUG: Final comparison data:")
            print(comparison_data)
        return comparison_data

    def add_ct_comparison(self, comparison_data, protocol, stats, drl_data, df):
        """Add CT comparison data"""
        if self.debug_mode.get():
            print(f"\nDEBUG: Adding CT comparison for protocol: {protocol}")
        # Get age-specific records for this protocol
        child_records = df[
            (df['AcquisitionProtocol'] == protocol) & 
            (df['CalculatedAge'] <= 18)
        ]
        if self.debug_mode.get():
            print(f"DEBUG: Number of child records: {len(child_records)}")
        
        # Choose appropriate DRL
        if len(child_records) > 0:
            for age_range, values in drl_data['child'].items():
                min_age, max_age = map(int, age_range.split('-'))
                age_records = child_records[
                    (child_records['CalculatedAge'] >= min_age) & 
                    (child_records['CalculatedAge'] <= max_age)
                ]
                if len(age_records) > 0:
                    drl_level = values['DLP']
                    if self.debug_mode.get():
                        print(f"DEBUG: Using child DRL for age {age_range}: {drl_level}")
                    break
            else:
                drl_level = drl_data['adult']['DLP']
                if self.debug_mode.get():
                    print(f"DEBUG: Using adult DRL: {drl_level}")
        else:
            drl_level = drl_data['adult']['DLP']
            if self.debug_mode.get():
                print(f"DEBUG: Using adult DRL: {drl_level}")
        
        # Calculate comparison
        percentage = (stats['TotalDLP'] / drl_level) * 100
        relative_percentage = percentage - 100
        if self.debug_mode.get():
            print(f"DEBUG: Calculated percentage: {percentage}%")
        
        self.add_comparison_result(comparison_data, protocol, stats, 
                                 drl_level, relative_percentage)

    def add_xray_comparison(self, comparison_data, protocol, stats, drl_data, df):
        """Add X-ray comparison data"""
        if self.debug_mode.get():
            print(f"\nDEBUG: Adding X-ray comparison for protocol: {protocol}")
        # Check for pediatric cases
        child_records = df[
            (df['ProtocolName'] == protocol) & 
            (df['CalculatedAge'] <= 18)
        ]
        if self.debug_mode.get():
            print(f"DEBUG: Number of child records: {len(child_records)}")
        
        if len(child_records) > 0 and 'child' in drl_data:
            drl_level = drl_data['child']['DAP']
            if self.debug_mode.get():
                print(f"DEBUG: Using child DRL: {drl_level}")
        else:
            drl_level = drl_data['adult']['DAP']
            if self.debug_mode.get():
                print(f"DEBUG: Using adult DRL: {drl_level}")
        
        # Calculate comparison
        dose_value = stats['ImageAndFluoroscopyAreaDoseProduct']
        percentage = (dose_value / drl_level) * 100
        relative_percentage = percentage - 100
        if self.debug_mode.get():
            print(f"DEBUG: Dose value: {dose_value}, DRL: {drl_level}, Percentage: {percentage}%")
        
        self.add_comparison_result(comparison_data, protocol, stats, 
                                 drl_level, relative_percentage)

    def add_mg_comparison(self, comparison_data, protocol, thickness, stats, drl_data):
        """Add mammography comparison data"""
        if self.debug_mode.get():
            print(f"\nDEBUG: Adding mammography comparison for protocol: {protocol}")
        # Find matching thickness range
        thickness_float = float(thickness)
        for range_str, drl_level in drl_data['thickness_ranges'].items():
            min_thick, max_thick = map(float, range_str.split('-'))
            if min_thick <= thickness_float <= max_thick:
                percentage = (stats['OrganDose'] / drl_level) * 100
                relative_percentage = percentage - 100
                if self.debug_mode.get():
                    print(f"DEBUG: Thickness range {range_str}: Value {stats['OrganDose']}, DRL {drl_level}")
                
                protocol_with_thickness = f"{protocol} ({thickness}mm)"
                self.add_comparison_result(comparison_data, protocol_with_thickness, 
                                         stats, drl_level, relative_percentage)
                break

    def add_comparison_result(self, comparison_data, protocol, stats, drl_level, relative_percentage):
        """Add comparison result with status and color"""
        if self.debug_mode.get():
            print(f"\nDEBUG: Adding comparison result for {protocol}")
        percentage = relative_percentage + 100
        
        if percentage <= 85:
            status = "Optimals"
            color = "#90EE90"  # Light green
        elif percentage <= 100:
            status = "Pienemams"
            color = "#FFD700"  # Gold
        else:
            status = "Parsniegts"
            color = "#FFB6C6"  # Light red
        
        if self.debug_mode.get():
            print(f"DEBUG: Status: {status}, Percentage: {percentage}%")
        
        comparison_data.append({
            'protocol': protocol,
            'device_model': stats['DeviceObserverModelName'],
            'avg_value': stats.get('TotalDLP', stats.get('DoseAreaProduct', stats.get('OrganDose'))),
            'drl_level': drl_level,
            'percentage': relative_percentage,
            'status': status,
            'color': color
        })
    def save_results(self, results):
        """Save results to Excel and generate PDF report"""
        if self.debug_mode.get():
            print("\nDEBUG: Starting results saving")
        # Generate filename based on date range and modality
        filename_base = f"DICOM_Dose_{self.modality.get()}"
        if self.date_from.get() and self.date_to.get():
            filename_base += f"_{self.date_from.get()}-{self.date_to.get()}"
        elif self.date_from.get():
            filename_base += f"_{self.date_from.get()}"
        elif self.date_to.get():
            filename_base += f"_{self.date_to.get()}"

        if self.debug_mode.get():
            print(f"DEBUG: Generated filename base: {filename_base}")
        excel_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=filename_base + ".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if excel_path:
            try:
                if self.debug_mode.get():
                    print(f"DEBUG: Saving Excel to: {excel_path}")
                df = pd.DataFrame(results)
                if self.data_source.get() == "RDSR":
                    df['Modality'] = df['Modality'].replace('SR', self.modality.get())
                    if self.debug_mode.get():
                        print("DEBUG: Replaced SR modality with selected modality")
                df.to_excel(excel_path, index=False)
                if self.debug_mode.get():
                    print("DEBUG: Excel saved successfully")
                
                # Generate PDF with same name but .pdf extension
                pdf_path = os.path.splitext(excel_path)[0] + ".pdf"
                if self.debug_mode.get():
                    print(f"DEBUG: Generating PDF: {pdf_path}")
                self.generate_pdf_report(df, pdf_path)
                
                self.status_var.set(f"Processed {len(results)} files")
                messagebox.showinfo("Success", 
                    f"Processed {len(results)} files\nSaved to:\n{excel_path}\n{pdf_path}")
            except Exception as e:
                if self.debug_mode.get():
                    print(f"DEBUG: Error saving files: {str(e)}")
                    print(f"DEBUG: Full error: {traceback.format_exc()}")
                messagebox.showerror("Error", f"Failed to save files: {e}")

    def generate_pdf_report(self, df, save_path):
        """Generate PDF report for dose data"""
        if self.debug_mode.get():
            print("\nDEBUG: Starting PDF report generation")
        try:
            # Basic HTML content
            html = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <title>DICOM Dose Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    h1 {{ text-align: center; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                    th, td {{ border: 1px solid #000; padding: 5px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .optimals {{ background-color: #90EE90; }}
                    .pienemams {{ background-color: #FFD700; }}
                    .parsniegts {{ background-color: #FFB6C6; }}
                </style>
            </head>
            <body>
                <h1>DICOM Dozu Datu Parskats</h1>
                <p><strong>Modalitate:</strong> {self.get_modality_name()}</p>
                <p><strong>Datums:</strong> {datetime.now().strftime("%d.%m.%Y %H:%M")}</p>
                <hr>
                <h2>DRL Salidzinajums</h2>
                <table>
                    <tr>
                        <th>Protokols</th>
                        <th>Videja vertiba</th>
                        <th>DRL Limits</th>
                        <th>Novirze %</th>
                        <th>Statuss</th>
                    </tr>
            """

            # Add data rows
            drl_comparison = self.calculate_drl_comparison(df)
            if self.debug_mode.get():
                print(f"DEBUG: DRL comparison for PDF: {drl_comparison}")
            
            for row in drl_comparison:
                status_class = "optimals" if row['status'] == "Optimals" else "pienemams" if row['status'] == "Pienemams" else "parsniegts"
                html += f"""
                    <tr class="{status_class}">
                        <td>{row['protocol']}</td>
                        <td>{row['avg_value']:.2f}</td>
                        <td>{row['drl_level']:.2f}</td>
                        <td>{"+" if row['percentage'] >= 0 else ""}{row['percentage']:.1f}%</td>
                        <td>{row['status']}</td>
                    </tr>
                """

            # Close HTML
            html += """
                </table>
                <div>
                    <p><strong>Statuss:</strong></p>
                    <p><span style="color: green;">■</span> Optimals: vertiba ≤ 85% no DRL</p>
                    <p><span style="color: gold;">■</span> Pienemams: vertiba 86-100% no DRL</p>
                    <p><span style="color: red;">■</span> Parsniegts: vertiba > 100% no DRL</p>
                </div>
            </body>
            </html>
            """

            # Save HTML for debugging
            if self.debug_mode.get():
                debug_html_path = save_path.replace('.pdf', '_debug.html')
                print(f"DEBUG: Saving debug HTML to: {debug_html_path}")
                with open(debug_html_path, 'w', encoding='utf-8') as f:
                    f.write(html)

            # Convert to PDF
            if self.debug_mode.get():
                print("DEBUG: Converting HTML to PDF")
            with open(save_path, "wb") as output_file:
                pisa.CreatePDF(
                    src=html,
                    dest=output_file,
                    encoding='utf-8'
                )
            if self.debug_mode.get():
                print("DEBUG: PDF generation complete")
            return True
        except Exception as e:
            if self.debug_mode.get():
                print(f"DEBUG: Error generating PDF: {str(e)}")
                print(f"DEBUG: Full error: {traceback.format_exc()}")
            return False

    def get_modality_name(self):
        """Get modality name without special characters"""
        modality_names = {
            "CT": "Datortomografija",
            "XA": "Angiografija",
            "MG": "Mamografija",
            "DX": "Rentgenografija"
        }
        if self.debug_mode.get():
            print(f"DEBUG: Getting modality name for: {self.modality.get()}")
        return modality_names.get(self.modality.get(), self.modality.get())

    def get_date_range(self):
        """Get formatted date range string"""
        date_range = ""
        if self.date_from.get():
            date_range = f"No: {self.date_from.get()}"
        if self.date_to.get():
            date_range += f" Lidz: {self.date_to.get()}"
        if self.debug_mode.get():
            print(f"DEBUG: Date range: {date_range}")
        return date_range
def main():
    print("DEBUG: Starting application")
    root = tk.Tk()
    app = DICOMDoseReader(root)
    print("DEBUG: Entering main loop")
    root.mainloop()


if __name__ == "__main__":
        main()
