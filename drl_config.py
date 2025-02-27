# drl_config.py
import json
import pandas as pd
import os
import traceback

class DRLConfiguration:
    def __init__(self):
        print("DEBUG: Initializing DRLConfiguration")
        self.config_dir = "drl_configs"
        self.config_files = {
            "CT": "ct_drl_config.json",
            "XA": "xa_drl_config.json",
            "MG": "mg_drl_config.json",
            "DX": "dx_drl_config.json"
        }
        self.protocols = {
            "CT": {},
            "XA": {},
            "MG": {},
            "DX": {}
        }
        self.ensure_config_directory()
        self.load_all_configs()
        print("DEBUG: DRLConfiguration initialized")
    
    def ensure_config_directory(self):
        """Ensure configuration directory exists"""
        print(f"DEBUG: Ensuring config directory exists: {self.config_dir}")
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            print(f"DEBUG: Created directory: {self.config_dir}")
        
        # Create empty config files if they don't exist
        for modality, filename in self.config_files.items():
            filepath = os.path.join(self.config_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
                print(f"DEBUG: Created empty config file: {filepath}")
    
    def load_all_configs(self):
        """Load configuration for all modalities"""
        print("DEBUG: Loading all configurations")
        for modality, filename in self.config_files.items():
            try:
                filepath = os.path.join(self.config_dir, filename)
                print(f"DEBUG: Loading config for {modality} from {filepath}")
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.protocols[modality] = json.load(f)
                print(f"DEBUG: Loaded {len(self.protocols[modality])} protocols for {modality}")
            except FileNotFoundError:
                print(f"DEBUG: Config file not found for {modality}")
                self.protocols[modality] = {}
    
    def save_config(self, modality):
        """Save configuration for specific modality"""
        print(f"DEBUG: Saving configuration for {modality}")
        filepath = os.path.join(self.config_dir, self.config_files[modality])
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.protocols[modality], f, indent=4, ensure_ascii=False)
        print(f"DEBUG: Configuration saved to {filepath}")
    
    def add_protocol(self, modality, name, data):
        """Add protocol for specific modality"""
        print(f"DEBUG: Adding protocol {name} for {modality}")
        if modality not in self.protocols:
            self.protocols[modality] = {}
        self.protocols[modality][name] = data
        self.save_config(modality)
    
    def delete_protocol(self, modality, name):
        """Delete protocol for specific modality"""
        print(f"DEBUG: Deleting protocol {name} for {modality}")
        if name in self.protocols.get(modality, {}):
            del self.protocols[modality][name]
            self.save_config(modality)
    
    def get_protocol(self, modality, name):
        """Get protocol for specific modality"""
        print(f"DEBUG: Getting protocol {name} for {modality}")
        return self.protocols.get(modality, {}).get(name, None)
    
    def get_all_protocols(self, modality):
        """Get all protocols for specific modality"""
        print(f"DEBUG: Getting all protocols for {modality}")
        return self.protocols.get(modality, {})

    def get_matching_protocol(self, modality, protocol_name):
        """Get matching protocol for specific modality"""
        print(f"\nDEBUG: Looking for matching protocol for {modality}: {protocol_name}")
        for protocol, data in self.protocols.get(modality, {}).items():
            print(f"DEBUG: Checking match patterns for {protocol}: {data['protocol_match']}")
            if any(pattern.lower() in protocol_name.lower() 
                  for pattern in data['protocol_match']):
                print(f"DEBUG: Found matching protocol: {protocol}")
                return protocol, data
        print("DEBUG: No matching protocol found")
        return None, None

    def import_from_excel(self, modality, file_path):
        """Import protocols from Excel for specific modality"""
        print(f"DEBUG: Importing {modality} protocols from Excel")
        try:
            df = pd.read_excel(file_path)
            new_protocols = {}
            
            if modality == "CT":
                # CT specific import logic
                for _, row in df.iterrows():
                    protocol_data = {
                        'protocol_match': [x.strip() for x in row['Match Patterns'].split(',')],
                        'adult': {
                            'DLP': float(row['Adult DLP']),
                            'CTDIvol': float(row['Adult CTDIvol'])
                        },
                        'child': {}
                    }
                    
                    # Process children data
                    age_ranges = ['0-1', '1-5', '5-10', '10-15']
                    for age_range in age_ranges:
                        if f'Child {age_range} DLP' in row and f'Child {age_range} CTDIvol' in row:
                            protocol_data['child'][age_range] = {
                                'DLP': float(row[f'Child {age_range} DLP']),
                                'CTDIvol': float(row[f'Child {age_range} CTDIvol'])
                            }
                    
                    new_protocols[row['Protocol']] = protocol_data
            
            elif modality == "XA":
                # X-Ray Angiography specific import logic
                for _, row in df.iterrows():
                    protocol_data = {
                        'protocol_match': [x.strip() for x in row['Match Patterns'].split(',')],
                        'adult': {
                            'DAP': float(row['Adult DAP']),
                            'AirKerma': float(row['Adult AirKerma']) if 'Adult AirKerma' in row else None,
                            'FluoroTime': float(row['Adult FluoroTime']) if 'Adult FluoroTime' in row else None
                        },
                        'child': {}
                    }
                    
                    # Process children data if available
                    if 'Child DAP' in row:
                        protocol_data['child']['DAP'] = float(row['Child DAP'])
                    if 'Child AirKerma' in row:
                        protocol_data['child']['AirKerma'] = float(row['Child AirKerma'])
                    if 'Child FluoroTime' in row:
                        protocol_data['child']['FluoroTime'] = float(row['Child FluoroTime'])
                    
                    new_protocols[row['Protocol']] = protocol_data
                    
            elif modality == "DX":
                # Digital X-Ray specific import logic
                for _, row in df.iterrows():
                    protocol_data = {
                        'protocol_match': [x.strip() for x in row['Match Patterns'].split(',')],
                        'adult': {
                            'DAP': float(row['Adult DAP']),
                            'ESD': float(row['Adult ESD']) if 'Adult ESD' in row else None
                        },
                        'child': {}
                    }
                    
                    # Process children data if available
                    if 'Child DAP' in row:
                        protocol_data['child']['DAP'] = float(row['Child DAP'])
                    if 'Child ESD' in row:
                        protocol_data['child']['ESD'] = float(row['Child ESD'])
                    
                    new_protocols[row['Protocol']] = protocol_data
            
            elif modality == "MG":
                # Mammography specific import logic
                for _, row in df.iterrows():
                    protocol_data = {
                        'protocol_match': [x.strip() for x in row['Match Patterns'].split(',')],
                        'AGD': float(row['AGD']),
                        'thickness_ranges': {}
                    }
                    
                    # Process thickness ranges if available
                    thickness_ranges = ['20-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90']
                    for range_ in thickness_ranges:
                        if f'AGD_{range_}' in row:
                            protocol_data['thickness_ranges'][range_] = float(row[f'AGD_{range_}'])
                    
                    new_protocols[row['Protocol']] = protocol_data
            
            self.protocols[modality] = new_protocols
            self.save_config(modality)
            print(f"DEBUG: Import successful for {modality}")
            return True, "Import successful"
        except Exception as e:
            print(f"DEBUG: Import error - {str(e)}")
            print(f"DEBUG: Full error: {traceback.format_exc()}")
            return False, str(e)
    
    def export_to_excel(self, modality, file_path):
        """Export protocols to Excel for specific modality"""
        print(f"DEBUG: Exporting {modality} protocols to Excel")
        try:
            data = []
            
            if modality == "CT":
                # CT specific export logic
                for protocol_name, protocol_data in self.protocols[modality].items():
                    row = {
                        'Protocol': protocol_name,
                        'Match Patterns': ','.join(protocol_data['protocol_match']),
                        'Adult DLP': protocol_data['adult']['DLP'],
                        'Adult CTDIvol': protocol_data['adult']['CTDIvol']
                    }
                    
                    for age_range, values in protocol_data['child'].items():
                        row[f'Child {age_range} DLP'] = values['DLP']
                        row[f'Child {age_range} CTDIvol'] = values['CTDIvol']
                    
                    data.append(row)
            
            elif modality == "XA":
                # X-Ray Angiography specific export logic
                for protocol_name, protocol_data in self.protocols[modality].items():
                    row = {
                        'Protocol': protocol_name,
                        'Match Patterns': ','.join(protocol_data['protocol_match']),
                        'Adult DAP': protocol_data['adult']['DAP'],
                        'Adult AirKerma': protocol_data['adult'].get('AirKerma', ''),
                        'Adult FluoroTime': protocol_data['adult'].get('FluoroTime', '')
                    }
                    
                    if 'child' in protocol_data:
                        row['Child DAP'] = protocol_data['child'].get('DAP', '')
                        row['Child AirKerma'] = protocol_data['child'].get('AirKerma', '')
                        row['Child FluoroTime'] = protocol_data['child'].get('FluoroTime', '')
                    
                    data.append(row)
            
            elif modality == "DX":
                # Digital X-Ray specific export logic
                for protocol_name, protocol_data in self.protocols[modality].items():
                    row = {
                        'Protocol': protocol_name,
                        'Match Patterns': ','.join(protocol_data['protocol_match']),
                        'Adult DAP': protocol_data['adult']['DAP'],
                        'Adult ESD': protocol_data['adult'].get('ESD', '')
                    }
                    
                    if 'child' in protocol_data:
                        row['Child DAP'] = protocol_data['child'].get('DAP', '')
                        row['Child ESD'] = protocol_data['child'].get('ESD', '')
                    
                    data.append(row)
            
            elif modality == "MG":
                # Mammography specific export logic
                for protocol_name, protocol_data in self.protocols[modality].items():
                    row = {
                        'Protocol': protocol_name,
                        'Match Patterns': ','.join(protocol_data['protocol_match']),
                        'AGD': protocol_data['AGD']
                    }
                    
                    for range_, value in protocol_data['thickness_ranges'].items():
                        row[f'AGD_{range_}'] = value
                    
                    data.append(row)
            
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            print(f"DEBUG: Export successful for {modality}")
            return True, "Export successful"
        except Exception as e:
            print(f"DEBUG: Export error - {str(e)}")
            print(f"DEBUG: Full error: {traceback.format_exc()}")
            return False, str(e)
