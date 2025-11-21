import os
import sys
import subprocess
from typing import Optional, Dict
import datetime
import uuid
import tempfile
import shutil

# Now import the packages
import streamlit as st
import pandas as pd
import yaml
import bcrypt
from streamlit.runtime.scriptrunner import get_script_run_ctx

# Setup paths - GitHub repository ke andar hi files store hongi
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MASTER_CSV = os.path.join(SCRIPT_DIR, 'master.csv')
HISTORY_CSV = os.path.join(SCRIPT_DIR, 'history.csv')
CREDENTIALS_YAML = os.path.join(SCRIPT_DIR, 'credentials.yaml')
SAMPLE_MASTER = os.path.join(SCRIPT_DIR, 'sample_master.csv')
MASTER_TEMPLATE = os.path.join(SCRIPT_DIR, 'master_template.csv')
HISTORY_TEMPLATE = os.path.join(SCRIPT_DIR, 'history_template.csv')

# Data sync function - GitHub mein automatically commit karega
def sync_data_to_github():
    """Auto-commit data changes to GitHub"""
    try:
        # Git commands to auto-commit data changes
        subprocess.run(['git', 'add', 'master.csv', 'history.csv'], cwd=SCRIPT_DIR, capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'Auto-update data {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'], 
                      cwd=SCRIPT_DIR, capture_output=True)
        subprocess.run(['git', 'push'], cwd=SCRIPT_DIR, capture_output=True)
    except Exception as e:
        print(f"GitHub sync warning: {e}")

# Create files if they don't exist - FIXED DOUBLE HEADER
def create_file_if_not_exists(file_path: str, content: str):
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

# Master CSV header (SINGLE HEADER)
MASTER_HEADER = 'person_id,record_id,area,pp_sz,zone,cc_uc,role,name,cnic,phone,vehicle_id,vehicle_reg_no,supervisor_id,status,updated_on,status_changed_on,last_transfer_on,remarks\n'

# History CSV header (SINGLE HEADER)  
HISTORY_HEADER = 'log_id,person_id,record_id,action,field,old_value,new_value,by_user,timestamp,notes\n'

# Create files if not exists - WITH SINGLE HEADER
create_file_if_not_exists(MASTER_CSV, MASTER_HEADER)
create_file_if_not_exists(HISTORY_CSV, HISTORY_HEADER)

# Create credentials.yaml if not exists
if not os.path.exists(CREDENTIALS_YAML):
    default_creds = {
        'users': {
            'admin': {'password': bcrypt.hashpw('adminpass'.encode(), bcrypt.gensalt()).decode(), 'role': 'admin'},
            'user': {'password': bcrypt.hashpw('userpass'.encode(), bcrypt.gensalt()).decode(), 'role': 'user'},
            'arslan': {'password': bcrypt.hashpw('ArslanPass123'.encode(), bcrypt.gensalt()).decode(), 'role': 'admin'},
            'ali': {'password': bcrypt.hashpw('AliPass456'.encode(), bcrypt.gensalt()).decode(), 'role': 'admin'},
            'babar': {'password': bcrypt.hashpw('BabarPass789'.encode(), bcrypt.gensalt()).decode(), 'role': 'admin'}
        }
    }
    with open(CREDENTIALS_YAML, 'w') as f:
        yaml.dump(default_creds, f)

# Create sample_master.csv - FIXED DOUBLE HEADER
SAMPLE_CONTENT = """P001,W001,City,PP-110,Zone-01,CC-001,Sanitary Worker,Bilal Ahmed,3520212345671,03001234567,,,W010,active,2025-11-01 00:00:00,,,
P002,W002,City,PP-110,Zone-01,CC-001,Driver,Kamran Ali,3520298765439,03007654321,V-005,LEB1234,W010,active,2025-10-15 00:00:00,,,
P002,W003,City,PP-111,Zone-02,CC-005,Driver,Kamran Ali,3520298765439,03007654321,V-005,LEB1234,W020,active,2025-11-04 00:00:00,,,Transferred from CC-001
P003,W004,Sadar,SZ-06,Z-09,UC-140,Supervisor,Imran Khan,3520176543219,03001112222,,,,active,2025-11-05 00:00:00,,,
P004,W005,City,PP-110,Zone-01,CC-001,Cleaner,Ahmed Khan,3520212345672,03001234568,,,W010,active,2025-11-06 00:00:00,,,
P005,W006,Sadar,SZ-01,Z-01,UC-131,Driver,Ali Raza,3520298765440,03007654322,V-001,LEA1234,W011,active,2025-11-07 00:00:00,,,
"""
# SINGLE HEADER - sirf data content
create_file_if_not_exists(SAMPLE_MASTER, MASTER_HEADER + SAMPLE_CONTENT)

# Create templates - SINGLE HEADER
create_file_if_not_exists(MASTER_TEMPLATE, MASTER_HEADER)
create_file_if_not_exists(HISTORY_TEMPLATE, HISTORY_HEADER)

# City data for dynamic selections
city_data = {
    'PP-110': {
        'zones': ['Zone-01', 'Zone-02', 'ZONE-03', 'Zone-04', 'Zone-05', 'Road Wing'],
        'zone_to_cc': {
            'Zone-01': ['CC-136', 'CC-137', 'CC-144', 'CC-145'],
            'Zone-02': ['CC-134', 'CC-143', 'CC-146', 'CC-147'],
            'ZONE-03': ['CC-133', 'CC-135', 'CC-148', 'CC-149'],
            'Zone-04': ['CC-006', 'CC-138', 'CC-139', 'CC-140'],
            'Zone-05': ['CC-141', 'CC-142', 'CC-152', 'CC-150'],
            'Road Wing': ['RW-1']
        }
    },
    'PP-111': {
        'zones': ['Zone-06', 'Zone-07', 'Night', 'Zone-08', 'Zone-09', 'Zone-10', 'Zone-11', 'Road Wing'],
        'zone_to_cc': {
            'Zone-06': ['CC-151', 'CC-153', 'CC-154', 'CC-156'],
            'Zone-07': ['CC-001A', 'CC-001B', 'CC-003', 'CC-157'],
            'Night': ['CC-001 (Night)'],
            'Zone-08': ['CC-002', 'CC-020', 'CC-021', 'CC-029'],
            'Zone-09': ['CC-024', 'CC-025', 'CC-026', 'CC-027'],
            'Zone-10': ['CC-022', 'CC-030', 'CC-051', 'CC-052'],
            'Zone-11': ['CC-121', 'CC-122', 'CC-123', 'CC-124', 'CC-155'],
            'Road Wing': ['RW-02', 'RW-03']
        }
    },
    'PP-112': {
        'zones': ['Zone-12', 'Zone-13', 'Zone-14', 'Zone-15', 'Road Wing'],
        'zone_to_cc': {
            'Zone-12': ['CC-126', 'CC-130', 'CC-131', 'CC-132'],
            'Zone-13': ['CC-125', 'CC-127', 'CC-128', 'CC-129'],
            'Zone-14': ['CC-117', 'CC-118', 'CC-119', 'CC-120'],
            'Zone-15': ['CC-112', 'CC-113', 'CC-114', 'CC-115', 'CC-116'],
            'Road Wing': ['RW-4', 'RW-5']
        }
    },
    'PP-113': {
        'zones': ['Zone-16', 'Zone-17', 'Zone-18', 'Zone-19', 'Zone-20', 'Zone-21', 'Road Wing'],
        'zone_to_cc': {
            'Zone-16': ['CC-108', 'CC-109', 'CC-110', 'CC-111'],
            'Zone-17': ['CC-104', 'CC-105', 'CC-106', 'CC-107'],
            'Zone-18': ['CC-101', 'CC-102', 'CC-103'],
            'Zone-19': ['CC-095', 'CC-096', 'CC-097', 'CC-100', 'CC-098'],
            'Zone-20': ['CC-079', 'CC-092', 'CC-093', 'CC-094'],
            'Zone-21': ['CC-072', 'CC-073', 'CC-074', 'CC-078'],
            'Road Wing': ['RW-6', 'RW-7']
        }
    },
    'PP-114': {
        'zones': ['Zone-22', 'Zone-23', 'Zone-24', 'Zone-25', 'Zone-26', 'Zone-27', 'Road Wing'],
        'zone_to_cc': {
            'Zone-22': ['CC-075', 'CC-076', 'CC-077', 'CC-081'],
            'Zone-23': ['CC-082', 'CC-083', 'CC-087', 'CC-088'],
            'Zone-24': ['CC-080', 'CC-089', 'CC-090', 'CC-091'],
            'Zone-25': ['CC-099', 'CC-084', 'CC-085', 'CC-086'],
            'Zone-26': ['CC-066', 'CC-067', 'CC-068', 'CC-069'],
            'Zone-27': ['CC-053', 'CC-054', 'CC-070', 'CC-071'],
            'Road Wing': ['RW-8', 'RW-9']
        }
    },
    'PP-115': {
        'zones': ['Zone-28', 'Zone-29', 'Zone-30', 'Zone-31', 'Road Wing'],
        'zone_to_cc': {
            'Zone-28': ['CC-058', 'CC-063', 'CC-064', 'CC-065'],
            'Zone-29': ['CC-055', 'CC-056', 'CC-057', 'CC-060'],
            'Zone-30': ['CC-046', 'CC-059', 'CC-061', 'CC-062'],
            'Zone-31': ['CC-047', 'CC-048', 'CC-049', 'CC-050'],
            'Road Wing': ['RW-10', 'RW-11']
        }
    },
    'PP-116': {
        'zones': ['Zone-32', 'Zone-33', 'Zone-35', 'Zone-34', 'Road Wing'],
        'zone_to_cc': {
            'Zone-32': ['CC-040', 'CC-041', 'CC-042', 'CC-043'],
            'Zone-33': ['CC-038', 'CC-039', 'CC-044', 'CC-045'],
            'Zone-35': ['CC-028', 'CC-031', 'CC-032', 'CC-033'],
            'Zone-34': ['CC-034', 'CC-035', 'CC-036', 'CC-037'],
            'Road Wing': ['RW-12', 'RW-13A', 'RW-13B']
        }
    },
    'PP-117': {
        'zones': ['Zone-36', 'Zone-37', 'Zone-38', 'Zone-39', 'Road Wing'],
        'zone_to_cc': {
            'Zone-36': ['CC-017', 'CC-018', 'CC-019', 'CC-023'],
            'Zone-37': ['CC-013', 'CC-014', 'CC-015', 'CC-016'],
            'Zone-38': ['CC-008', 'CC-009', 'CC-011', 'CC-012'],
            'Zone-39': ['CC-004', 'CC-005', 'CC-007', 'CC-010'],
            'Road Wing': ['RW-14', 'RW-15', 'RW-16']
        }
    },
}

# Helper functions
def load_df(file_path: str) -> pd.DataFrame:
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
        # Double header check - agar header row duplicate hai to remove karein
        if not df.empty and 'person_id' in df.columns and df['person_id'].str.contains('person_id').any():
            # Remove header rows
            df = df[~df['person_id'].str.contains('person_id', na=False)]
        return df
    else:
        return pd.DataFrame()

def atomic_append_df(df: pd.DataFrame, new_rows: pd.DataFrame, file_path: str):
    combined = pd.concat([df, new_rows], ignore_index=True)
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
    combined.to_csv(temp_file, index=False)
    temp_file.close()
    shutil.move(temp_file.name, file_path)
    
    # Auto-sync to GitHub after data changes
    try:
        sync_data_to_github()
    except:
        pass  # GitHub sync optional hai

def generate_person_id() -> str:
    return f"P{uuid.uuid4().hex[:8].upper()}"

def generate_record_id(df: pd.DataFrame) -> str:
    master_df = load_df(MASTER_CSV)  # Existing master file se ID generate karein
    max_id = 0
    if not master_df.empty and 'record_id' in master_df.columns:
        # Extract numeric part from existing record_ids
        ids = master_df['record_id'].str.extract(r'W(\d+)', expand=False).dropna()
        if not ids.empty:
            ids = ids.astype(int)
            max_id = ids.max()
    return f"W{max_id + 1:04d}"

def generate_log_id(df: pd.DataFrame) -> str:
    max_id = 0
    if not df.empty and 'log_id' in df.columns:
        ids = df['log_id'].str.extract(r'H(\d+)', expand=False).dropna().astype(int)
        if not ids.empty:
            max_id = ids.max()
    return f"H{max_id + 1:04d}"

def validate_cnic(cnic: str) -> bool:
    return len(str(cnic)) == 13 and str(cnic).isdigit()

def validate_phone(phone: str) -> bool:
    return len(str(phone)) == 11 and str(phone).isdigit()

def validate_date(date_str: Optional[str]) -> bool:
    if not date_str:
        return True
    try:
        pd.to_datetime(date_str)
        return True
    except ValueError:
        return False

def validate_pp_sz(pp_sz: str, area: str) -> bool:
    if area == 'City' and pp_sz.startswith('PP-') and pp_sz[3:].isdigit() and len(pp_sz[3:]) == 3:
        return True
    if area == 'Sadar' and pp_sz.startswith('SZ-') and pp_sz[3:].isdigit() and len(pp_sz[3:]) == 2:
        return True
    return False

def validate_cc_uc(cc_uc: str, area: str) -> bool:
    if area == 'City':
        return cc_uc.startswith('CC-') or cc_uc.startswith('RW-')
    if area == 'Sadar' and cc_uc.startswith('UC-') and cc_uc[3:].isdigit() and len(cc_uc[3:]) == 3:
        return True
    return False

def get_supervisor_for_cc_uc(cc_uc: str, master_df: pd.DataFrame) -> str:
    master_df['updated_on'] = pd.to_datetime(master_df['updated_on'], errors='coerce')
    sups = master_df[(master_df['role'] == 'Supervisor') & (master_df['status'] == 'active') & (master_df['cc_uc'] == cc_uc)]
    if sups.empty:
        return ""
    latest_idx = sups['updated_on'].idxmax()
    return sups.loc[latest_idx, 'record_id']

def is_supervisor_exists(supervisor_id: str, master_df: pd.DataFrame) -> bool:
    if not supervisor_id:
        return True
    master_df['updated_on'] = pd.to_datetime(master_df['updated_on'], errors='coerce')
    sup_rows = master_df[master_df['record_id'] == supervisor_id]
    if sup_rows.empty:
        return False
    sup_person_id = sup_rows['person_id'].iloc[0]
    latest_idx = master_df[master_df['person_id'] == sup_person_id]['updated_on'].idxmax()
    latest_row = master_df.loc[latest_idx]
    return latest_row['status'] == 'active' and latest_row['role'] == 'Supervisor'

def log_action(person_id: str, record_id: str, action: str, field: str, old_value: str, new_value: str, by_user: str, notes: str):
    history_df = load_df(HISTORY_CSV)
    log_id = generate_log_id(history_df)
    timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
    new_log = pd.DataFrame({
        'log_id': [log_id],
        'person_id': [person_id],
        'record_id': [record_id],
        'action': [action],
        'field': [field],
        'old_value': [old_value],
        'new_value': [new_value],
        'by_user': [by_user],
        'timestamp': [timestamp],
        'notes': [notes]
    })
    atomic_append_df(history_df, new_log, HISTORY_CSV)

def add_new_worker(form_data: Dict, by_user: str) -> str:
    master_df = load_df(MASTER_CSV)
    
    # Validate
    if not validate_cnic(form_data['cnic']):
        return "Invalid CNIC: Must be 13 digits."
    if not validate_phone(form_data['phone']):
        return "Invalid Phone: Must be 11 digits."
    if form_data['area'] not in ['City', 'Sadar']:
        return "Invalid Area: Must be City or Sadar."
    if not validate_pp_sz(form_data['pp_sz'], form_data['area']):
        return "Invalid PP/SZ format."
    if not validate_cc_uc(form_data['cc_uc'], form_data['area']):
        return "Invalid CC/UC format."
    if form_data['role'] != 'Driver' and (form_data['vehicle_id'] or form_data['vehicle_reg_no']):
        return "Only Drivers can have vehicles."
    
    # Auto set updated_on
    updated_on = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Auto set supervisor_id
    if form_data['role'] == 'Supervisor':
        # Check if already exists
        master_df['updated_on'] = pd.to_datetime(master_df['updated_on'], errors='coerce')
        existing_sups = master_df[(master_df['role'] == 'Supervisor') & (master_df['status'] == 'active') & (master_df['cc_uc'] == form_data['cc_uc'])]
        if not existing_sups.empty:
            return "Already a supervisor for this CC/UC."
        supervisor_id = ''
    else:
        supervisor_id = get_supervisor_for_cc_uc(form_data['cc_uc'], master_df)
        if not supervisor_id:
            return "No supervisor found for this CC/UC."
        if not is_supervisor_exists(supervisor_id, master_df):
            return "Supervisor not active."
    
    # Check for existing person by CNIC
    existing = master_df[master_df['cnic'] == form_data['cnic']]
    person_id = existing['person_id'].iloc[0] if not existing.empty else generate_person_id()
    
    record_id = generate_record_id(master_df)
    new_row = pd.DataFrame({
        'person_id': [person_id],
        'record_id': [record_id],
        'area': [form_data['area']],
        'pp_sz': [form_data['pp_sz']],
        'zone': [form_data['zone']],
        'cc_uc': [form_data['cc_uc']],
        'role': [form_data['role']],
        'name': [form_data['name']],
        'cnic': [form_data['cnic']],
        'phone': [form_data['phone']],
        'vehicle_id': [form_data['vehicle_id']],
        'vehicle_reg_no': [form_data['vehicle_reg_no']],
        'supervisor_id': [supervisor_id],
        'status': ['active'],
        'updated_on': [updated_on],
        'status_changed_on': [''],
        'last_transfer_on': [''],
        'remarks': [form_data['remarks']]
    })
    atomic_append_df(master_df, new_row, MASTER_CSV)
    log_action(person_id, record_id, 'add', '', '', '', by_user, form_data['remarks'])
    return ""

def perform_transfer(person_id: str, old_record_id: str, new_data: Dict, by_user: str, notes: str):
    master_df = load_df(MASTER_CSV)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date_today = datetime.date.today().isoformat()
    
    master_df['updated_on'] = pd.to_datetime(master_df['updated_on'], errors='coerce')
    old_row = master_df[(master_df['person_id'] == person_id) & (master_df['record_id'] == old_record_id)].iloc[0]
    
    # Validate new data
    if not validate_pp_sz(new_data['pp_sz'], new_data['area']):
        st.error("Invalid PP/SZ format.")
        return
    if not validate_cc_uc(new_data['cc_uc'], new_data['area']):
        st.error("Invalid CC/UC format.")
        return
    
    # Auto set new supervisor_id based on new cc_uc
    if old_row['role'] == 'Supervisor':
        existing_sups = master_df[(master_df['role'] == 'Supervisor') & (master_df['status'] == 'active') & (master_df['cc_uc'] == new_data['cc_uc'])]
        if not existing_sups.empty and old_row['cc_uc'] != new_data['cc_uc']:
            st.error("Already a supervisor for the new CC/UC.")
            return
        new_supervisor_id = ''
    else:
        new_supervisor_id = get_supervisor_for_cc_uc(new_data['cc_uc'], master_df)
        if not new_supervisor_id:
            st.error("No supervisor found for the new CC/UC.")
            return
    
    new_record_id = generate_record_id(master_df)
    new_row = pd.DataFrame({
        'person_id': [person_id],
        'record_id': [new_record_id],
        'area': [new_data['area']],
        'pp_sz': [new_data['pp_sz']],
        'zone': [new_data['zone']],
        'cc_uc': [new_data['cc_uc']],
        'role': [old_row['role']],
        'name': [old_row['name']],
        'cnic': [old_row['cnic']],
        'phone': [old_row['phone']],
        'vehicle_id': [old_row['vehicle_id']],
        'vehicle_reg_no': [old_row['vehicle_reg_no']],
        'supervisor_id': [new_supervisor_id],
        'status': ['active'],
        'updated_on': [now],
        'status_changed_on': [''],
        'last_transfer_on': [date_today],
        'remarks': [f"Transferred from {old_row['cc_uc']}. {notes}"]
    })
    atomic_append_df(master_df, new_row, MASTER_CSV)
    log_action(person_id, new_record_id, 'transfer', 'cc_uc', old_row['cc_uc'], new_data['cc_uc'], by_user, notes)
    if old_row['pp_sz'] != new_data['pp_sz']:
        log_action(person_id, new_record_id, 'transfer', 'pp_sz', old_row['pp_sz'], new_data['pp_sz'], by_user, notes)

def perform_remove(person_id: str, record_id: str, by_user: str, notes: str):
    master_df = load_df(MASTER_CSV)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date_today = datetime.date.today().isoformat()
    old_row = master_df[(master_df['person_id'] == person_id) & (master_df['record_id'] == record_id)].iloc[0]
    new_record_id = generate_record_id(master_df)
    new_row = old_row.copy()
    new_row['status'] = 'removed'
    new_row['status_changed_on'] = date_today
    new_row['updated_on'] = now
    new_row['remarks'] = notes
    new_row['record_id'] = new_record_id
    atomic_append_df(master_df, pd.DataFrame([new_row]), MASTER_CSV)
    log_action(person_id, new_record_id, 'remove', 'status', 'active', 'removed', by_user, notes)

def perform_edit(person_id: str, record_id: str, field: str, new_value: str, by_user: str, notes: str) -> str:
    master_df = load_df(MASTER_CSV)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    old_row = master_df[(master_df['person_id'] == person_id) & (master_df['record_id'] == record_id)].iloc[0]
    old_value = old_row[field]
    if old_value == new_value:
        return "No change in value."
    if field == 'cnic' and not validate_cnic(new_value):
        return "Invalid CNIC: Must be 13 digits."
    new_record_id = generate_record_id(master_df)
    new_row = old_row.copy()
    new_row[field] = new_value
    new_row['updated_on'] = now
    new_row['remarks'] = f"Edited {field} from {old_value} to {new_value}. {notes}"
    new_row['record_id'] = new_record_id
    atomic_append_df(master_df, pd.DataFrame([new_row]), MASTER_CSV)
    log_action(person_id, new_record_id, 'edit', field, old_value, new_value, by_user, notes)
    return ""

def perform_bulk_upload(uploaded_file, by_user: str):
    try:
        if uploaded_file.name.endswith('.csv'):
            upload_df = pd.read_csv(uploaded_file, dtype=str, keep_default_na=False)
        elif uploaded_file.name.endswith('.xlsx'):
            # Excel file ke liye proper handling
            upload_df = pd.read_excel(uploaded_file, dtype=str, keep_default_na=False)
            # NaN values ko empty string se replace karein
            upload_df = upload_df.fillna('')
        else:
            return "Unsupported file type. Only CSV and XLSX allowed."
        
        required_cols = ['person_id', 'record_id', 'area', 'pp_sz', 'zone', 'cc_uc', 'role', 'name', 'cnic', 'phone', 'vehicle_id', 'vehicle_reg_no', 'supervisor_id', 'status', 'updated_on', 'status_changed_on', 'last_transfer_on', 'remarks']
        
        # Add missing columns with empty values
        for col in required_cols:
            if col not in upload_df.columns:
                upload_df[col] = ''
        
        warnings = []
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for idx, row in upload_df.iterrows():
            # Auto-generate person_id if empty
            if pd.isna(row['person_id']) or row['person_id'] == '':
                upload_df.at[idx, 'person_id'] = generate_person_id()
            
            # Auto-generate record_id if empty
            if pd.isna(row['record_id']) or row['record_id'] == '':
                upload_df.at[idx, 'record_id'] = generate_record_id(upload_df)
            
            # Set updated_on to current time if empty
            if pd.isna(row['updated_on']) or row['updated_on'] == '':
                upload_df.at[idx, 'updated_on'] = current_time
            
            # Set remarks to "Bulk upload" if empty
            if pd.isna(row['remarks']) or row['remarks'] == '':
                upload_df.at[idx, 'remarks'] = 'Bulk upload'
            
            # Set status to active if empty
            if pd.isna(row['status']) or row['status'] == '':
                upload_df.at[idx, 'status'] = 'active'
            
            # Validations
            cnic_value = str(row['cnic']) if not pd.isna(row['cnic']) else ''
            phone_value = str(row['phone']) if not pd.isna(row['phone']) else ''
            
            if cnic_value and not validate_cnic(cnic_value):
                warnings.append(f"Row {idx+1}: Invalid CNIC.")
            if phone_value and not validate_phone(phone_value):
                warnings.append(f"Row {idx+1}: Invalid Phone.")
        
        master_df = load_df(MASTER_CSV)
        atomic_append_df(master_df, upload_df, MASTER_CSV)
        
        # Log actions for each row
        for idx, row in upload_df.iterrows():
            log_action(row['person_id'], row['record_id'], 'add', '', '', '', by_user, 'Bulk upload')
        
        if warnings:
            return "\n".join(warnings)
        return ""
    except Exception as e:
        return f"Error: {str(e)}"

# Authentication
def load_credentials() -> Dict:
    with open(CREDENTIALS_YAML, 'r') as f:
        return yaml.safe_load(f)

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        creds = load_credentials()
        if username in creds['users']:
            if bcrypt.checkpw(password.encode(), creds['users'][username]['password'].encode()):
                st.session_state['user'] = username
                st.session_state['role'] = creds['users'][username]['role']
                st.success("Logged in!")
                st.rerun()
            else:
                st.error("Invalid credentials")
        else:
            st.error("Invalid credentials")

# Main App
# Main App
def main():
    if 'user' not in st.session_state:
        login()
        return
    
    role = st.session_state['role']
    user = st.session_state['user']
    
    st.sidebar.title(f"Welcome, {user} ({role})")
    page = st.sidebar.selectbox("Page", ["Dashboard"] + (["Admin Panel", "History"] if role == 'admin' else []))
    
    master_df = load_df(MASTER_CSV)
    history_df = load_df(HISTORY_CSV)
    
    master_df['updated_on'] = pd.to_datetime(master_df['updated_on'], errors='coerce')
    
    if page == "Dashboard":
        st.title("Dashboard")
        area = st.selectbox("Area", ['All', 'City', 'Sadar'])
        pp_sz = ''
        zone = ''
        cc_uc = ''
        if area == 'All':
            pp_sz = st.text_input("PP/SZ")
            zone = st.text_input("Zone")
            cc_uc = st.text_input("CC/UC")
        elif area == 'City':
            pp_sz_options = sorted(city_data.keys())
            pp_sz = st.selectbox("PP/SZ", ['All'] + pp_sz_options)
            if pp_sz != 'All':
                zone_options = city_data[pp_sz]['zones']
                zone = st.selectbox("Zone", ['All'] + zone_options)
                cc_uc_options = []
                if zone != 'All':
                    cc_uc_options = city_data[pp_sz]['zone_to_cc'].get(zone, [])
                else:
                    for z in zone_options:
                        cc_uc_options += city_data[pp_sz]['zone_to_cc'].get(z, [])
                    cc_uc_options = sorted(set(cc_uc_options))
                cc_uc = st.selectbox("CC/UC", ['All'] + cc_uc_options)
                if cc_uc == 'All':
                    cc_uc = ''
                if zone == 'All':
                    zone = ''
            else:
                pp_sz = ''
                zone = st.text_input("Zone")
                cc_uc = st.text_input("CC/UC")
        else:  # Sadar
            pp_sz_options = [f"SZ-{i:02d}" for i in range(1, 12)]
            pp_sz = st.selectbox("PP/SZ", ['All'] + pp_sz_options)
            if pp_sz == 'All':
                pp_sz = ''
            zone = st.text_input("Zone")
            cc_uc_options = [f"UC-{i:03d}" for i in range(131, 190)]
            cc_uc = st.selectbox("CC/UC", ['All'] + cc_uc_options)
            if cc_uc == 'All':
                cc_uc = ''
        search = st.text_input("Search (name/id/cnic/vehicle)")
        
        filtered = master_df if role == 'admin' else master_df[master_df['status'] == 'active']
        if area != 'All':
            filtered = filtered[filtered['area'] == area]
        if pp_sz:
            filtered = filtered[filtered['pp_sz'].str.contains(pp_sz, case=False, na=False)]
        if zone:
            filtered = filtered[filtered['zone'].str.contains(zone, case=False, na=False)]
        if cc_uc:
            filtered = filtered[filtered['cc_uc'].str.contains(cc_uc, case=False, na=False)]
        if search:
            filtered = filtered[
                filtered['name'].str.contains(search, case=False, na=False) |
                filtered['record_id'].str.contains(search, case=False, na=False) |
                filtered['cnic'].str.contains(search, case=False, na=False) |
                filtered['vehicle_reg_no'].str.contains(search, case=False, na=False)
            ]
        
        st.dataframe(filtered)
        
        if st.download_button("Export CSV", filtered.to_csv(index=False), "export.csv"):
            pass
    
    elif page == "Admin Panel" and role == 'admin':
        st.title("Admin Panel")
        tab = st.tabs(["Bulk Upload", "Add New", "Edit/Transfer/Remove", "Remove All Data"])
        
        with tab[0]:
            st.subheader("Bulk Upload")
            uploaded = st.file_uploader("Upload master file", type=["csv", "xlsx"])
            if uploaded and st.button("Validate & Upload"):
                error = perform_bulk_upload(uploaded, user)
                if error:
                    st.error(error)
                else:
                    st.success("Uploaded successfully!")
        
        with tab[1]:
            st.subheader("Add New Worker")
            area = st.selectbox("Area", ['City', 'Sadar'])
            pp_sz = ''
            zone = ''
            cc_uc = ''
            vehicle_id = ''
            vehicle_reg_no = ''
            if area == 'City':
                pp_sz_options = sorted(city_data.keys())
                pp_sz = st.selectbox("PP/SZ", pp_sz_options)
                zone_options = city_data.get(pp_sz, {}).get('zones', [])
                zone = st.selectbox("Zone", zone_options)
                cc_uc_options = city_data.get(pp_sz, {}).get('zone_to_cc', {}).get(zone, [])
                cc_uc = st.selectbox("CC/UC", cc_uc_options)
            else:
                pp_sz_options = [f"SZ-{i:02d}" for i in range(1, 12)]
                pp_sz = st.selectbox("PP/SZ", pp_sz_options)
                zone_options = [f"Z-{i:02d}" for i in range(1, 21)]
                zone = st.selectbox("Zone", zone_options)
                cc_uc_options = [f"UC-{i:03d}" for i in range(131, 190)]
                cc_uc = st.selectbox("CC/UC", cc_uc_options)
            role = st.selectbox("Role", ['Sanitary Worker', 'Helper', 'Zonal Officer', 'Supervisor', 'Driver', 'Cleaner', 'Data Entry Operator', 'Assistant Manager'])
            name = st.text_input("Name")
            cnic = st.text_input("CNIC (13 digits)")
            phone = st.text_input("Phone (11 digits)")
            if role == 'Driver':
                vehicle_id = st.text_input("Vehicle ID")
                vehicle_reg_no = st.text_input("Vehicle Reg No")
            remarks = st.text_input("Remarks")
            if st.button("Add"):
                form_data = {
                    'area': area, 'pp_sz': pp_sz, 'zone': zone, 'cc_uc': cc_uc, 'role': role,
                    'name': name, 'cnic': cnic, 'phone': phone, 'vehicle_id': vehicle_id,
                    'vehicle_reg_no': vehicle_reg_no,
                    'remarks': remarks
                }
                error = add_new_worker(form_data, user)
                if error:
                    st.error(error)
                else:
                    st.success("Added successfully!")
        
        with tab[2]:
            st.subheader("Edit/Transfer/Remove")
            input_value = st.text_input("CNIC/Person ID to Modify")
            if input_value:
                if len(str(input_value)) == 13 and str(input_value).isdigit():
                    person_records = master_df[master_df['cnic'] == str(input_value)]
                else:
                    person_records = master_df[master_df['person_id'] == input_value]
                if person_records.empty:
                    st.error("No records found for the provided CNIC or Person ID.")
                else:
                    person_id = person_records['person_id'].iloc[0]
                    latest_idx = person_records['updated_on'].idxmax()
                    last_update = person_records.loc[latest_idx, 'updated_on']
                    st.write(f"Last Update: {last_update}")
                    st.dataframe(person_records)
                    latest_row = person_records.loc[latest_idx]
                    if latest_row['status'] == 'active':
                        record_id = latest_row['record_id']
                        action = st.selectbox("Action", ['Transfer', 'Remove', 'Edit'])
                        notes = st.text_input("Notes/Remarks")
                        
                        if action == 'Transfer':
                            new_area = st.selectbox("New Area", ['City', 'Sadar'])
                            new_pp_sz = ''
                            new_zone = ''
                            new_cc_uc = ''
                            if new_area == 'City':
                                new_pp_sz_options = sorted(city_data.keys())
                                new_pp_sz = st.selectbox("New PP/SZ", new_pp_sz_options)
                                new_zone_options = city_data.get(new_pp_sz, {}).get('zones', [])
                                new_zone = st.selectbox("New Zone", new_zone_options)
                                new_cc_uc_options = city_data.get(new_pp_sz, {}).get('zone_to_cc', {}).get(new_zone, [])
                                new_cc_uc = st.selectbox("New CC/UC", new_cc_uc_options)
                            else:
                                new_pp_sz_options = [f"SZ-{i:02d}" for i in range(1, 12)]
                                new_pp_sz = st.selectbox("New PP/SZ", new_pp_sz_options)
                                new_zone_options = [f"Z-{i:02d}" for i in range(1, 21)]
                                new_zone = st.selectbox("New Zone", new_zone_options)
                                new_cc_uc_options = [f"UC-{i:03d}" for i in range(131, 190)]
                                new_cc_uc = st.selectbox("New CC/UC", new_cc_uc_options)
                            if st.button("Confirm Transfer"):
                                new_data = {'area': new_area, 'pp_sz': new_pp_sz, 'zone': new_zone, 'cc_uc': new_cc_uc}
                                perform_transfer(person_id, record_id, new_data, user, notes)
                                st.success("Transferred!")
                        
                        elif action == 'Remove':
                            if st.button("Confirm Remove"):
                                perform_remove(person_id, record_id, user, notes)
                                st.success("Removed!")
                        
                        elif action == 'Edit':
                            field = st.selectbox("Field to Edit", ['phone', 'cnic', 'vehicle_id', 'vehicle_reg_no'])
                            new_value = st.text_input("New Value")
                            if st.button("Confirm Edit"):
                                error = perform_edit(person_id, record_id, field, new_value, user, notes)
                                if error:
                                    st.error(error)
                                else:
                                    st.success("Edited!")
                    else:
                        st.error("No active record for this person.")
        
        with tab[3]:
            st.subheader("🚨 Remove All Data")
            st.warning("**DANGER ZONE**: This will permanently delete ALL data from the system. This action cannot be undone!")
            
            st.write("**Instructions:**")
            st.write("1. Enter the confirmation code: `REX9797`")
            st.write("2. Click 'Remove All Data' button")
            st.write("3. All workers, history, and records will be deleted")
            
            confirmation_code = st.text_input("Confirmation Code", type="password")
            
            if st.button("🚨 Remove All Data", type="secondary"):
                if not confirmation_code:
                    st.error("Please enter the confirmation code.")
                else:
                    result = remove_all_data(confirmation_code, user)
                    if "successfully" in result.lower():
                        st.success(result)
                        st.info("The system has been reset to initial state. All data is removed.")
                    else:
                        st.error(result)
    
    elif page == "History" and role == 'admin':
        st.title("History")
        st.dataframe(history_df)
        if st.download_button("Export History CSV", history_df.to_csv(index=False), "history_export.csv"):
            pass

if __name__ == "__main__":
    main()
