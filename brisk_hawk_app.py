import os
import pandas as pd
import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Set up page configurations for mobile and desktop view syncing
st.set_page_config(page_title="Brisk Hawk Portal", page_icon="🚛", layout="wide")

# ==============================================================================
# DATA STORAGE & SYSTEM PATH ARCHITECTURE (ONEDRIVE SYNCED)
# ==============================================================================
DOCS_DIR = os.path.expanduser("~/OneDrive/Documents/")
PDF_FOLDER = os.path.expanduser("~/OneDrive/Documents/Generated_Invoices/")
LOGS_DB_PATH = os.path.expanduser("~/OneDrive/Documents/brisk_hawk_logs.csv")
INVOICE_DB_PATH = os.path.expanduser("~/OneDrive/Documents/invoices_db.csv")
PROFILE_DB_PATH = os.path.expanduser("~/OneDrive/Documents/brisk_hawk_profile.csv")
CONTAINER_DB_PATH = os.path.expanduser("~/OneDrive/Documents/container_tracking_db.csv")
TODO_DB_PATH = os.path.expanduser("~/OneDrive/Documents/brisk_hawk_todo.csv")
TRUCK_DB_PATH = os.path.expanduser("~/OneDrive/Documents/fleet_trucks_db.csv")
DRIVER_DB_PATH = os.path.expanduser("~/OneDrive/Documents/fleet_drivers_db.csv")

# Safety Compliance Sub-Database Paths
DRUG_DB_PATH = os.path.expanduser("~/OneDrive/Documents/safety_drug_db.csv")
DOCS_DB_PATH = os.path.expanduser("~/OneDrive/Documents/safety_docs_db.csv")
ELD_DB_PATH = os.path.expanduser("~/OneDrive/Documents/safety_eld_db.csv")
VIOLATION_DB_PATH = os.path.expanduser("~/OneDrive/Documents/safety_violations_db.csv")

# Ensure all systemic folders exist safely
for folder in [DOCS_DIR, PDF_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

if not os.path.exists(LOGS_DB_PATH):
    pd.DataFrame(columns=["ID", "Date", "Driver_Name", "Move_Index", "Pickup_Location", "Delivery_Location", "Return_Location", "Hours_Worked", "Container_Num"]).to_csv(LOGS_DB_PATH, index=False)

if not os.path.exists(INVOICE_DB_PATH):
    pd.DataFrame(columns=["Invoice_ID", "Customer_Name", "Container_Num", "Base_Rate", "Chassis_Fee", "Fuel_Surcharge", "Port_Fees", "Detention_Fee", "Storage_Fee", "Custom_Charge_Name", "Custom_Charge_Amount", "Total_Amount", "Status"]).to_csv(INVOICE_DB_PATH, index=False)

if not os.path.exists(PROFILE_DB_PATH):
    pd.DataFrame([{"Legal_Name": "Brisk Hawk Transport Inc.", "Address_Line": "Intermodal Drayage & Logistics Solutions Center", "MC_Number": "MC-XXXXXX", "DOT_Number": "USDOT XXXXXXX", "Phone": "(555) 019-2831", "Email_Dispatch": "dispatch@briskhawkops.com", "Email_Billing": "billing@briskhawkops.com"}]).to_csv(PROFILE_DB_PATH, index=False)

if not os.path.exists(CONTAINER_DB_PATH):
    pd.DataFrame(columns=["ID", "Order_Number", "Container_Number", "Size", "Chassis", "Shipping_Line", "Broker", "LFD", "Pickup_Date", "Delivery_Date", "Delivery_Location", "Return_Date", "Remarks"]).to_csv(CONTAINER_DB_PATH, index=False)

# Initialize Safety databases if missing
if not os.path.exists(DRUG_DB_PATH):
    pd.DataFrame(columns=["ID", "Driver_Name", "Drug_Test_Date", "Reason", "Result", "Random_Test_Date", "Random_Result", "License_Expiration"]).to_csv(DRUG_DB_PATH, index=False)

if not os.path.exists(DOCS_DB_PATH):
    pd.DataFrame(columns=["ID", "Driver_Name", "App_Checklist", "Drug_Report", "Medical_Test", "Hazmat_Cert", "MVR", "Training", "Situation_Notes"]).to_csv(DOCS_DB_PATH, index=False)

if not os.path.exists(ELD_DB_PATH):
    pd.DataFrame(columns=["ID", "Truck_Number", "ELD_Connected", "ELD_Number"]).to_csv(ELD_DB_PATH, index=False)

if not os.path.exists(VIOLATION_DB_PATH):
    pd.DataFrame(columns=["ID", "Driver_Name", "Truck_Number", "Violation_Type", "Action_Taken", "Remarks"]).to_csv(VIOLATION_DB_PATH, index=False)

if not os.path.exists(TODO_DB_PATH):
    pd.DataFrame(columns=["Task_ID", "Task_Description", "Due_Date", "Priority", "Status"]).to_csv(TODO_DB_PATH, index=False)

# Initialize 15 Pre-Built Editable Truck Row Slots
if not os.path.exists(TRUCK_DB_PATH):
    init_truck_rows = []
    for i in range(1, 16):
        init_truck_rows.append({
            "Slot_ID": f"SLOT-{i:02d}", "Truck_Number": f"Truck {i}", "VIN": "", "License_Plate": "", 
            "RFID_Tag": "", "Driver_Name": "", "Reg_Issue_Date": "", "Reg_Expiry_Date": "", 
            "Ins_Issue_Date": "", "Ins_Expiry_Date": "", "IFTA_Expiry_Date": "", "Safety_Issue_Date": "", 
            "Safety_Expiry_Date": "", "Extinguisher_Repair_Date": "", "ELD_Connected": "No", 
            "Violations": "None", "Subject_Driver": "", "Action_Taken_Remarks": ""
        })
    pd.DataFrame(init_truck_rows).to_csv(TRUCK_DB_PATH, index=False)

# Initialize 15 Pre-Built Editable Driver Row Slots
if not os.path.exists(DRIVER_DB_PATH):
    init_driver_rows = []
    for i in range(1, 16):
        init_driver_rows.append({
            "Driver_Slot_ID": f"DRV-SLOT-{i:02d}", "Driver_Name": f"Driver {i}", "License_Number": "", 
            "License_Expiry_Date": "", "Medical_Expiry_Date": "", "MVR_Date": "", 
            "Training_Status": "Pending", "Violations_With_Dates": "None", "Monthly_Pay": 0.0, 
            "Driver_Records": "", "Remarks": ""
        })
    pd.DataFrame(init_driver_rows).to_csv(DRIVER_DB_PATH, index=False)

# ==============================================================================
# SIDEBAR NAVIGATION INTERFACE
# ==============================================================================
st.sidebar.title("🦅 Brisk Hawk Control Center")
st.sidebar.markdown("Intermodal Operations Portal v8.0")

app_mode = st.sidebar.radio("Navigate Workspace Tabs", [
    "📊 Dispatch Dashboard",
    "🏢 Company Profile Control",
    "📦 Container Tracking Control",
    "🚛 Fleet Truck Management",
    "👥 Driver Management",
    "🧾 Customer Profiles & Billing Control",
    "📋 Move Scheduler & Driver Logs",
    "🛡️ Compliance & Safety Tracking",
    "📝 To-Do List Manager"
])

# ==============================================================================
# TAB 1: DISPATCH DASHBOARD
# ==============================================================================
if app_mode == "📊 Dispatch Dashboard":
    st.header("📊 Real-Time Operations Fleet Status")
    
    logs_df = pd.read_csv(LOGS_DB_PATH)
    inv_df = pd.read_csv(INVOICE_DB_PATH)
    cont_df = pd.read_csv(CONTAINER_DB_PATH)
    todo_df = pd.read_csv(TODO_DB_PATH)
    truck_df = pd.read_csv(TRUCK_DB_PATH).fillna("")
    driver_df = pd.read_csv(DRIVER_DB_PATH).fillna("")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Tracked Fleet Containers", f"📦 {len(cont_df)}")
    with c2: 
        active_trucks = len(truck_df[truck_df["VIN"] != ""])
        st.metric("Registered Trucks in Fleet", f"🚛 {active_trucks} / 15 Active")
    with c3:
        active_drivers = len(driver_df[driver_df["License_Number"] != ""])
        st.metric("Active Managed Drivers", f"👥 {active_drivers} / 15 Active")
    with c4: 
        pending_tasks = len(todo_df[todo_df["Status"] == "Pending"]) if not todo_df.empty else 0
        st.metric("Open Tasks To Do", f"📝 {pending_tasks} Remaining")
        
    st.markdown("---")
    st.subheader("📦 Master Intermodal Container Tracking Matrix")
    if not cont_df.empty: st.dataframe(cont_df, use_container_width=True)
    else: st.info("No containers logged inside your system yet.")

# ==============================================================================
# TAB 2: COMPANY PROFILE CONTROL
# ==============================================================================
elif app_mode == "🏢 Company Profile Control":
    st.header("🏢 Company Profile Control")
    prof_df = pd.read_csv(PROFILE_DB_PATH)
    p_data = prof_df.iloc[0]
    
    st.markdown("---")
    col_logo, col_header_info = st.columns([1, 4])
    with col_logo:
        logo_path = os.path.expanduser("~/OneDrive/Documents/brisk_hawk_logo.png")
        if os.path.exists(logo_path): st.image(logo_path, width=140)
        else: st.info("🦅 Logo missing.")
            
    with col_header_info:
        st.subheader(p_data["Legal_Name"])
        st.write(f"📍 {p_data['Address_Line']} | ☎️ {p_data['Phone']}")
        st.write(f"📧 Dispatch: `{p_data['Email_Dispatch']}` | Billing: `{p_data['Email_Billing']}`")

    st.markdown("---")
    st.subheader("✏️ Edit Corporate Credentials Registry")
    with st.form("profile_edit_form"):
        cx1, cx2 = st.columns(2)
        with cx1:
            u_name = st.text_input("Company Legal Name", value=p_data["Legal_Name"])
            u_addr = st.text_input("Operational Center Address Line", value=p_data["Address_Line"])
            u_phone = st.text_input("Primary Support Line", value=p_data["Phone"])
        with cx2:
            u_mc = st.text_input("FMCSA Operating Authority (MC #)", value=p_data["MC_Number"])
            u_dot = st.text_input("US Department of Transportation (DOT #)", value=p_data["DOT_Number"])
            u_disp = st.text_input("Operations Center Dispatch Email", value=p_data["Email_Dispatch"])
            u_bill = st.text_input("Billing Resolution Email", value=p_data["Email_Billing"])
        save_profile_btn = st.form_submit_button("Commit Changes")
        
    if save_profile_btn:
        pd.DataFrame([{"Legal_Name": u_name, "Address_Line": u_addr, "MC_Number": u_mc, "DOT_Number": u_dot, "Phone": u_phone, "Email_Dispatch": u_disp, "Email_Billing": u_bill}]).to_csv(PROFILE_DB_PATH, index=False)
        st.success("🎉 Corporate profile records updated successfully across the system!")
        st.rerun()

# ==============================================================================
# TAB 3: CONTAINER TRACKING CONTROL
# ==============================================================================
elif app_mode == "📦 Container Tracking Control":
    st.header("📦 Container Tracking Control & Ledger")
    cont_df = pd.read_csv(CONTAINER_DB_PATH).fillna("")

    if "editing_container_id" in st.session_state:
        st.warning(f"📝 Editing Mode Active: Modifying System Log ID {st.session_state['editing_container_id']}")
        m_row = cont_df[cont_df["ID"] == st.session_state["editing_container_id"]]
        if not m_row.empty:
            rec = m_row.iloc[0]
            c_id, c_ord, c_num, c_size, c_chas, c_line, c_brok, c_lfd, c_pkup, c_delv, c_loc, c_ret, c_rem = str(rec["ID"]), str(rec["Order_Number"]), str(rec["Container_Number"]), str(rec["Size"]), str(rec["Chassis"]), str(rec["Shipping_Line"]), str(rec["Broker"]), str(rec["LFD"]), str(rec["Pickup_Date"]), str(rec["Delivery_Date"]), str(rec["Delivery_Location"]), str(rec["Return_Date"]), str(rec["Remarks"])
        else: del st.session_state["editing_container_id"]; st.rerun()
    else:
        c_id, c_ord, c_num, c_chas, c_line, c_brok, c_loc, c_rem = f"CT-{len(cont_df) + 5001}", "", "", "", "", "", "", ""
        c_size = "40ft HC"
        c_lfd, c_pkup, c_delv, c_ret = datetime.today().strftime('%Y-%m-%d'), datetime.today().strftime('%Y-%m-%d'), datetime.today().strftime('%Y-%m-%d'), datetime.today().strftime('%Y-%m-%d')

    with st.form("container_entry_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            f_ord = st.text_input("Order Number / Booking #", value=c_ord)
            f_num = st.text_input("Container Number", value=c_num)
            f_size = st.selectbox("Size Type", ["20ft Standard", "40ft Standard", "40ft HC", "45ft HC"], index=["20ft Standard", "40ft Standard", "40ft HC", "45ft HC"].index(c_size))
            f_chas = st.text_input("Chassis Assigned #", value=c_chas)
        with col2:
            f_line = st.text_input("Shipping Line / Steamship Co.", value=c_line)
            f_brok = st.text_input("Broker Associated Name", value=c_brok)
            f_loc = st.text_input("Delivery Target Location Address", value=c_loc)
            f_rem = st.text_area("Remarks / Yard Notes", value=c_rem)
        with col3:
            f_lfd = st.text_input("LFD (Last Free Day) [YYYY-MM-DD]", value=c_lfd)
            f_pkup = st.text_input("Terminal Pick-up Date [YYYY-MM-DD]", value=c_pkup)
            f_delv = st.text_input("Customer Delivery Date [YYYY-MM-DD]", value=c_delv)
            f_ret = st.text_input("Empty Return Date [YYYY-MM-DD]", value=c_ret)
        c_submit = st.form_submit_button("Commit Container Log Record")

    if c_submit:
        if not f_ord or not f_num: st.error("⚠️ Order Number and Container Number details must be filled out.")
        else:
            if "editing_container_id" in st.session_state: cont_df = cont_df[cont_df["ID"] != st.session_state["editing_container_id"]]; del st.session_state["editing_container_id"]
            new_cont_data = {"ID": c_id, "Order_Number": f_ord, "Container_Number": f_num, "Size": f_size, "Chassis": f_chas, "Shipping_Line": f_line, "Broker": f_brok, "LFD": f_lfd, "Pickup_Date": f_pkup, "Delivery_Date": f_delv, "Delivery_Location": f_loc, "Return_Date": f_ret, "Remarks": f_rem}
            cont_df = pd.concat([cont_df, pd.DataFrame([new_cont_data])], ignore_index=True).to_csv(CONTAINER_DB_PATH, index=False)
            st.success("🎉 Container records synced.")
            st.rerun()

    st.markdown("---")
    st.subheader("🗂️ Active Container Inventory Tracker & Editor")
    if not cont_df.empty:
        for idx, row in cont_df.iterrows():
            grid_col1, grid_col2, grid_col3, grid_col4 = st.columns([3, 4, 1, 1])
            with grid_col1: st.markdown(f"📦 **{row['Container_Number']}** ({row['Size']})<br/>📋 Order: `{row['Order_Number']}`", unsafe_allow_html=True)
            with grid_col2: st.markdown(f"📍 Loc: *{row['Delivery_Location']}*<br/>📅 **LFD:** `{row['LFD']}` | **Ret:** `{row['Return_Date']}`", unsafe_allow_html=True)
            with grid_col3:
                if st.button("✏️ Edit", key=f"cnt_edit_{row['ID']}_{idx}"): st.session_state["editing_container_id"] = row["ID"]; st.rerun()
            with grid_col4:
                if st.button("🗑️ Del", key=f"cnt_del_{row['ID']}_{idx}"): cont_df = cont_df[cont_df["ID"] != row["ID"]]; cont_df.to_csv(CONTAINER_DB_PATH, index=False); st.rerun()

# ==============================================================================
# TAB 4: FLEET TRUCK MANAGEMENT
# ==============================================================================
elif app_mode == "🚛 Fleet Truck Management":
    st.header("🚛 Corporate Fleet Truck Management Registry")
    st.caption("Maintain identification records, plates, regulatory expirations, and asset safety logs for up to 15 trucks.")
    
    truck_df = pd.read_csv(TRUCK_DB_PATH).fillna("")

    if "editing_truck_slot" in st.session_state:
        slot_id = st.session_state["editing_truck_slot"]
        match_truck = truck_df[truck_df["Slot_ID"] == slot_id].iloc[0]
        
        st.markdown(f"---")
        st.warning(f"📝 **Editing Details for Panel Slot: {match_truck['Truck_Number']}**")
        
        with st.form("truck_edit_drawer_form"):
            tc1, tc2, tc3 = st.columns(3)
            with tc1:
                u_truck_num = st.text_input("Truck ID Designation / Number", value=match_truck["Truck_Number"])
                u_vin = st.text_input("Vehicle Identification Number (VIN)", value=match_truck["VIN"])
                u_plate = st.text_input("License Plate Number", value=match_truck["License_Plate"])
                u_rfid = st.text_input("Port RFID Tag Identification Code", value=match_truck["RFID_Tag"])
                u_driver = st.text_input("Assigned Operator / Driver Name", value=match_truck["Driver_Name"])
            with tc2:
                u_reg_is = st.text_input("Registration Issue Date [YYYY-MM-DD]", value=match_truck["Reg_Issue_Date"])
                u_reg_ex = st.text_input("Registration Expiration Date [YYYY-MM-DD]", value=match_truck["Reg_Expiry_Date"])
                u_ins_is = st.text_input("Insurance Binder Issue Date [YYYY-MM-DD]", value=match_truck["Ins_Issue_Date"])
                u_ins_ex = st.text_input("Insurance Binder Expiration Date [YYYY-MM-DD]", value=match_truck["Ins_Expiry_Date"])
                u_ifta = st.text_input("IFTA Decal Expiration Date [YYYY-MM-DD]", value=match_truck["IFTA_Expiry_Date"])
            with tc3:
                u_safe_is = st.text_input("Annual Safety Dot Inspection Issue Date", value=match_truck["Safety_Issue_Date"])
                u_safe_ex = st.text_input("Annual Safety Dot Inspection Expiry Date", value=match_truck["Safety_Expiry_Date"])
                u_ext = st.text_input("Fire Extinguisher Certification Repair Date", value=match_truck["Extinguisher_Repair_Date"])
                u_eld = st.selectbox("ELD Connected Device Attached Status", ["No", "Yes", "Standby"], index=["No", "Yes", "Standby"].index(match_truck["ELD_Connected"]))
                u_vio = st.text_input("Active Logged Violations (If applicable)", value=match_truck["Violations"])
                u_subj = st.text_input("Subject Driver for the Violation", value=match_truck["Subject_Driver"])
                
            st.markdown("**📄 Action Taken, Safety Resolutions & Remarks Box**")
            u_remarks = st.text_area("Input expanded detailed write-up actions taken or safety metrics remarks", value=match_truck["Action_Taken_Remarks"])
            save_truck_btn = st.form_submit_button("Lock Asset Records into Database File")
            
        if save_truck_btn:
            idx_match = truck_df[truck_df["Slot_ID"] == slot_id].index[0]
            truck_df.at[idx_match, "Truck_Number"] = u_truck_num; truck_df.at[idx_match, "VIN"] = u_vin; truck_df.at[idx_match, "License_Plate"] = u_plate; truck_df.at[idx_match, "RFID_Tag"] = u_rfid; truck_df.at[idx_match, "Driver_Name"] = u_driver
            truck_df.at[idx_match, "Reg_Issue_Date"] = u_reg_is; truck_df.at[idx_match, "Reg_Expiry_Date"] = u_reg_ex; truck_df.at[idx_match, "Ins_Issue_Date"] = u_ins_is; truck_df.at[idx_match, "Ins_Expiry_Date"] = u_ins_ex; truck_df.at[idx_match, "IFTA_Expiry_Date"] = u_ifta
            truck_df.at[idx_match, "Safety_Issue_Date"] = u_safe_is; truck_df.at[idx_match, "Safety_Expiry_Date"] = u_safe_ex; truck_df.at[idx_match, "Extinguisher_Repair_Date"] = u_ext; truck_df.at[idx_match, "ELD_Connected"] = u_eld; truck_df.at[idx_match, "Violations"] = u_vio; truck_df.at[idx_match, "Subject_Driver"] = u_subj; truck_df.at[idx_match, "Action_Taken_Remarks"] = u_remarks
            truck_df.to_csv(TRUCK_DB_PATH, index=False)
            st.success("🎉 Asset records updated successfully!")
            del st.session_state["editing_truck_slot"]; st.rerun()

    st.markdown("---")
    st.subheader("📋 15 Horizontal Fleet Truck Asset Lines")
    h_1, h_2, h_3, h_4, h_5 = st.columns([2, 3, 3, 3, 1])
    with h_1: st.caption("**Truck Identity**")
    with h_2: st.caption("**Plate / VIN / RFID**")
    with h_3: st.caption("**Expirations (Reg, Ins, IFTA, Safety)**")
    with h_4: st.caption("**Violations & Action Taken Remarks**")
    with h_5: st.caption("**Modify**")
    st.markdown("<hr style='margin:0px 0px 10px 0px; padding:0px;'>", unsafe_allow_html=True)

    for idx, r in truck_df.iterrows():
        r_1, r_2, r_3, r_4, r_5 = st.columns([2, 3, 3, 3, 1])
        with r_1: st.markdown(f"🚛 **{r['Truck_Number']}**<br/>👤 Driver: *{r['Driver_Name'] if r['Driver_Name'] else 'Unassigned'}*<br/>📟 ELD Pair: `{r['ELD_Connected']}`", unsafe_allow_html=True)
        with r_2: st.markdown(f"🔑 VIN: `{r['VIN'] if r['VIN'] else '---'}`<br/>🔢 Plate: `{r['License_Plate'] if r['License_Plate'] else '---'}`<br/>🏷️ RFID Tag: `{r['RFID_Tag'] if r['RFID_Tag'] else '---'}`", unsafe_allow_html=True)
        with r_3: st.markdown(f"📝 Reg Exp: `{r['Reg_Expiry_Date'] if r['Reg_Expiry_Date'] else '---'}` | Ins Exp: `{r['Ins_Expiry_Date'] if r['Ins_Expiry_Date'] else '---'}`<br/>⛽ IFTA Exp: `{r['IFTA_Expiry_Date'] if r['IFTA_Expiry_Date'] else '---'}` | DOT Exp: `{r['Safety_Expiry_Date'] if r['Safety_Expiry_Date'] else '---'}`<br/>🧯 Extinguisher Check: `{r['Extinguisher_Repair_Date'] if r['Extinguisher_Repair_Date'] else '---'}`", unsafe_allow_html=True)
        with r_4: st.markdown(f"🛑 Violations: <span style='color:red;'><b>{r['Violations']}</b></span> (Driver: *{r['Subject_Driver'] if r['Subject_Driver'] else 'None'}*)<br/>🛠️ *Actions/Remarks:* {r['Action_Taken_Remarks'] if r['Action_Taken_Remarks'] else 'No logged data remarks.'}", unsafe_allow_html=True)
        with r_5:
            if st.button("✏️ Edit", key=f"trk_slot_btn_{r['Slot_ID']}_{idx}"): st.session_state["editing_truck_slot"] = r["Slot_ID"]; st.rerun()
        st.markdown("<hr style='margin:5px 0px; border-top: 1px dotted #CBD5E1;'>", unsafe_allow_html=True)

# ==============================================================================
# TAB 5: DRIVER MANAGEMENT (BRAND NEW 15 EDITABLE DRIVERS MODULE EXCLUSIVE)
# ==============================================================================
elif app_mode == "👥 Driver Management":
    st.header("👥 Commercial Driver Management Workspace")
    st.caption("Track operator licenses, medical certification logs, background MVR validations, monthly payouts, and safety remarks for 15 operators.")
    
    driver_df = pd.read_csv(DRIVER_DB_PATH).fillna("")

    # Handle active driver slot editing drawer panel
    if "editing_driver_slot" in st.session_state:
        drv_slot_id = st.session_state["editing_driver_slot"]
        match_driver = driver_df[driver_df["Driver_Slot_ID"] == drv_slot_id].iloc[0]
        
        st.markdown(f"---")
        st.warning(f"📝 **Editing Profile Panel for: {match_driver['Driver_Name']}**")
        
        with st.form("driver_edit_drawer_form"):
            td1, td2, td3 = st.columns(3)
            with td1:
                u_drv_name = st.text_input("Driver Full Legal Name", value=match_driver["Driver_Name"])
                u_license = st.text_input("Commercial Driver License (CDL #)", value=match_driver["License_Number"])
                u_lic_exp = st.text_input("License Expiration Date [YYYY-MM-DD]", value=match_driver["License_Expiry_Date"])
            with td2:
                u_med_exp = st.text_input("Medical Certificate Expiration [YYYY-MM-DD]", value=match_driver["Medical_Expiry_Date"])
                u_mvr_dt = st.text_input("Last MVR Check Date [YYYY-MM-DD]", value=match_driver["MVR_Date"])
                u_train = st.selectbox("Driver Safety Training Status", ["Passed / Certified", "Pending Review", "Overdue Re-training"], index=["Passed / Certified", "Pending Review", "Overdue Re-training"].index(match_driver["Training_Status"]))
            with td3:
                u_drv_vios = st.text_input("Violation Numbers with Dates (If any)", value=match_driver["Violations_With_Dates"])
                u_pay = st.number_input("Fixed Monthly Pay Salary ($)", min_value=0.0, value=float(match_driver["Monthly_Pay"]), step=100.0)
                u_records = st.text_input("Driver Record / Internal File Designation", value=match_driver["Driver_Records"])
                
            st.markdown("**📄 Internal Corporate Safety Remarks & Audit Box**")
            u_drv_remarks = st.text_area("Input expanded administrative notes or performance remarks", value=match_driver["Remarks"])
            
            save_driver_btn = st.form_submit_button("Lock Driver Records into Database File")
            
        if save_driver_btn:
            idx_drv_match = driver_df[driver_df["Driver_Slot_ID"] == drv_slot_id].index[0]
            driver_df.at[idx_drv_match, "Driver_Name"] = u_drv_name
            driver_df.at[idx_drv_match, "License_Number"] = u_license
            driver_df.at[idx_drv_match, "License_Expiry_Date"] = u_lic_exp
            driver_df.at[idx_drv_match, "Medical_Expiry_Date"] = u_med_exp
            driver_df.at[idx_drv_match, "MVR_Date"] = u_mvr_dt
            driver_df.at[idx_drv_match, "Training_Status"] = u_train
            driver_df.at[idx_drv_match, "Violations_With_Dates"] = u_drv_vios
            driver_df.at[idx_drv_match, "Monthly_Pay"] = u_pay
            driver_df.at[idx_drv_match, "Driver_Records"] = u_records
            driver_df.at[idx_drv_match, "Remarks"] = u_drv_remarks
            
            driver_df.to_csv(DRIVER_DB_PATH, index=False)
            st.success("🎉 Driver qualification profile updated successfully!")
            del st.session_state["editing_driver_slot"]
            st.rerun()
            
        if st.button("❌ Close Operator Form Panel"):
            del st.session_state["editing_driver_slot"]
            st.rerun()

    st.markdown("---")
    st.subheader("📋 15 Horizontal Operator Qualification Lines")
    
    # Grid column layout for high scannability matching user request rows
    dg_1, dg_2, dg_3, dg_4, dg_5 = st.columns([2.5, 3, 2.5, 3, 1])
    with dg_1: st.caption("**Operator & Pay**")
    with dg_2: st.caption("**CDL & Medical Credentials**")
    with dg_3: st.caption("**MVR & Training Matrix**")
    with dg_4: st.caption("**Violations Record & Remarks Log**")
    with dg_5: st.caption("**Modify**")
    st.markdown("<hr style='margin:0px 0px 10px 0px; padding:0px;'>", unsafe_allow_html=True)

    for idx, drv in driver_df.iterrows():
        rd_1, rd_2, rd_3, rd_4, rd_5 = st.columns([2.5, 3, 2.5, 3, 1])
        
        with rd_1:
            st.markdown(f"👤 **{drv['Driver_Name']}**<br/>💰 Monthly Pay: <b>${float(drv['Monthly_Pay']):,.2f}</b><br/>📂 Folder Ref: `{drv['Driver_Records'] if drv['Driver_Records'] else 'None'}`", unsafe_allow_html=True)
        with rd_2:
            st.markdown(f"💳 CDL #: `{drv['License_Number'] if drv['License_Number'] else '---'}`<br/>📅 CDL Exp: `{drv['License_Expiry_Date'] if drv['License_Expiry_Date'] else '---'}`<br/>🩺 Med Card Exp: `{drv['Medical_Expiry_Date'] if drv['Medical_Expiry_Date'] else '---'}`", unsafe_allow_html=True)
        with rd_3:
            st.markdown(f"📊 MVR Audit: `{drv['MVR_Date'] if drv['MVR_Date'] else '---'}`<br/>🛡️ Training: **{drv['Training_Status']}**", unsafe_allow_html=True)
        with rd_4:
            st.markdown(f"🛑 Infractions: <span style='color:red;'><b>{drv['Violations_With_Dates']}</b></span><br/>📝 *Remarks:* {drv['Remarks'] if drv['Remarks'] else 'No active remarks logged.'}", unsafe_allow_html=True)
        with rd_5:
            if st.button("✏️ Edit", key=f"drv_slot_btn_{drv['Driver_Slot_ID']}_{idx}"):
                st.session_state["editing_driver_slot"] = drv["Driver_Slot_ID"]
                st.rerun()
        st.markdown("<hr style='margin:5px 0px; border-top: 1px dotted #CBD5E1;'>", unsafe_allow_html=True)

# ==============================================================================
# TAB 6: CUSTOMER PROFILES & BILLING CONTROL
# ==============================================================================
elif app_mode == "🧾 Customer Profiles & Billing Control":
    st.header("🧾 Advanced Freight Invoicing Engine")
    prof_df = pd.read_csv(PROFILE_DB_PATH)
    p_data = prof_df.iloc[0]
    inv_df = pd.read_csv(INVOICE_DB_PATH).fillna(0.0)

    st.subheader("📊 Financial Overview")
    col1, col2 = st.columns(2)
    with col1: st.metric("Unpaid Invoices", f"{len(inv_df[inv_df['Status'] == 'Unpaid'])} Pending")
    with col2: st.metric("Total Money Collected", f"${inv_df[inv_df['Status'] == 'Paid']['Total_Amount'].sum():,.2f}")

    st.markdown("---")
    st.subheader("🔍 Quick Customer Lookup & Auto-Fill")
    unique_brokers = ["New Customer / Manual Entry"]
    if not inv_df.empty: unique_brokers.extend(inv_df["Customer_Name"].unique().tolist())
    selected_lookup = st.selectbox("Select Existing Broker to Auto-Populate Form Fields", unique_brokers)

    auto_cust, auto_cont, auto_cname = "", "", "None"
    auto_base, auto_chas, auto_fuel, auto_port, auto_det, auto_stor, auto_camt = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    auto_stat, auto_id = "Unpaid", f"BH-{len(inv_df) + 1001}"

    if "editing_invoice_id" in st.session_state:
        match_row = inv_df[inv_df["Invoice_ID"] == st.session_state["editing_invoice_id"]]
        if not match_row.empty:
            edit_record = match_row.iloc[0]
            auto_id, auto_cust, auto_cont = str(edit_record["Invoice_ID"]), str(edit_record["Customer_Name"]), str(edit_record["Container_Num"])
            auto_base, auto_chas, auto_fuel = float(edit_record["Base_Rate"]), float(edit_record["Chassis_Fee"]), float(edit_record["Fuel_Surcharge"])
            auto_port, auto_det, auto_stor = float(edit_record["Port_Fees"]), float(edit_record["Detention_Fee"]), float(edit_record["Storage_Fee"])
            auto_cname, auto_camt, auto_stat = str(edit_record["Custom_Charge_Name"]), float(edit_record["Custom_Charge_Amount"]), str(edit_record["Status"])
    elif selected_lookup != "New Customer / Manual Entry":
        hist_rows = inv_df[inv_df["Customer_Name"] == selected_lookup]
        if not hist_rows.empty:
            last_record = hist_rows.iloc[-1]
            auto_cust, auto_cont = str(last_record["Customer_Name"]), str(last_record["Container_Num"])
            auto_base, auto_chas, auto_fuel = float(last_record["Base_Rate"]), float(last_record["Chassis_Fee"]), float(last_record["Fuel_Surcharge"])
            auto_port, auto_det, auto_stor = float(last_record["Port_Fees"]), float(last_record["Detention_Fee"]), float(last_record["Storage_Fee"])
            auto_cname, auto_camt = str(last_record["Custom_Charge_Name"]), float(last_record["Custom_Charge_Amount"])

    with st.form("inv_entry_form"):
        c1, c2 = st.columns(2)
        with c1:
            f_id = st.text_input("Invoice #", value=auto_id)
            f_cust = st.text_input("Broker/Customer Name", value=auto_cust)
            f_cont = st.text_input("Container #", value=auto_cont)
            st.markdown("**⏱️ Operational Accessorial Tabs**")
            f_det = st.number_input("Detention Total Fee ($)", min_value=0.0, value=auto_det, step=5.0)
            f_stor = st.number_input("Port Storage / Demurrage ($)", min_value=0.0, value=auto_stor, step=5.0)
        with c2:
            f_base = st.number_input("Base Linehaul Rate ($)", min_value=0.0, value=auto_base, step=50.0)
            f_chas = st.number_input("Chassis Rental/Usage Fee ($)", min_value=0.0, value=auto_chas, step=5.0)
            f_fuel = st.number_input("Fuel Surcharge SCM ($)", min_value=0.0, value=auto_fuel, step=5.0)
            f_port = st.number_input("Port Gate & Accessorial Fees ($)", min_value=0.0, value=auto_port, step=5.0)
            f_stat = st.selectbox("Payment Status", ["Unpaid", "Paid"], index=["Unpaid", "Paid"].index(auto_stat))
        cx1, cx2 = st.columns([2, 1])
        with cx1: f_cust_name = st.text_input("Custom Charge Label Name", value=auto_cname)
        with cx2: f_cust_amt = st.number_input("Custom Charge Amount ($)", min_value=0.0, value=auto_camt, step=5.0)
        f_submit = st.form_submit_button("Generate Official Invoice PDF")

    if f_submit:
        if not f_cust or not f_cont: st.error("⚠️ Fill out both Broker Name and Container Number.")
        else:
            t_bill = f_base + f_chas + f_fuel + f_port + f_det + f_stor + f_cust_amt
            if "editing_invoice_id" in st.session_state: inv_df = inv_df[inv_df["Invoice_ID"] != st.session_state["editing_invoice_id"]]; del st.session_state["editing_invoice_id"]
            new_data = {"Invoice_ID": f_id, "Customer_Name": f_cust, "Container_Num": f_cont, "Base_Rate": f_base, "Chassis_Fee": f_chas, "Fuel_Surcharge": f_fuel, "Port_Fees": f_port, "Detention_Fee": f_det, "Storage_Fee": f_stor, "Custom_Charge_Name": f_cust_name, "Custom_Charge_Amount": f_cust_amt, "Total_Amount": t_bill, "Status": f_stat}
            inv_df = pd.concat([inv_df, pd.DataFrame([new_data])], ignore_index=True)
            inv_df.to_csv(INVOICE_DB_PATH, index=False)

            pdf_out = f"{PDF_FOLDER}Invoice_{f_id}.pdf"
            doc = SimpleDocTemplate(pdf_out, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
            styles = getSampleStyleSheet()
            story = []

            title_style = ParagraphStyle('T', fontSize=22, leading=26, textColor=colors.HexColor('#1A365D'), fontName="Helvetica-Bold")
            sub_style = ParagraphStyle('S', fontSize=10, leading=14, textColor=colors.HexColor('#4A5568'), fontName="Helvetica")
            m_style = ParagraphStyle('M', fontSize=10, leading=16)
            
            letterhead_left = [Paragraph(f"<b>{p_data['Legal_Name'].upper()}</b>", title_style), Spacer(1, 6), Paragraph(p_data["Address_Line"], sub_style), Spacer(1, 3), Paragraph(f"Email: {p_data['Email_Billing']} | Tel: {p_data['Phone']}", sub_style)]
            logo_path = os.path.expanduser("~/OneDrive/Documents/brisk_hawk_logo.png")
            if os.path.exists(logo_path):
                from reportlab.platypus import Image as RLImage
                letterhead_right = [RLImage(logo_path, width=150, height=84)]
            else: letterhead_right = [Paragraph("<b>INVOICE</b>", ParagraphStyle('InvTitle', fontSize=26, alignment=2, textColor=colors.HexColor('#1A365D'), fontName="Helvetica-Bold"))]
            
            letterhead_table = Table([[letterhead_left, letterhead_right]], colWidths=[350, 190])
            letterhead_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
            story.append(letterhead_table)

            divider = Table([[""]], colWidths=[540], rowHeights=[3])
            divider.setStyle(TableStyle([('BACKGROUND', (0,0), (0,0), colors.HexColor('#1A365D'))]))
            story.append(divider)
            story.append(Spacer(1, 15))

            story.append(Paragraph(f"<b>INVOICE ID:</b> {f_id}<br/><b>DATE:</b> May 2026<br/><b>BILL TO:</b> {f_cust.upper()}<br/><b>CONTAINER ID:</b> {f_cont}", m_style))
            story.append(Spacer(1, 15))

            t_data = [["Line Item Freight Charge Description", "Amount Due"], ["Base Linehaul Intermodal Transit Rate", f"${f_base:,.2f}"], ["Intermodal Chassis Usage / Rental Fee", f"${f_chas:,.2f}"], ["Fuel Surcharge Matrix Indexation", f"${f_fuel:,.2f}"], ["Port Gate Logistics & Drop-Pull Charges", f"${f_port:,.2f}"]]
            if f_det > 0: t_data.append(["Driver Detention / Waiting Time Fee", f"${f_det:,.2f}"])
            if f_stor > 0: t_data.append(["Port Storage / Demurrage Fee", f"${f_stor:,.2f}"])
            if f_cust_amt > 0: t_data.append([f"Accessorial: {f_cust_name}", f"${f_cust_amt:,.2f}"])
            t_data.append(["TOTAL BALANCE DUE (USD):", f"${t_bill:,.2f}"])
            
            t_grid = Table(t_data, colWidths=[390, 140])
            t_grid.setStyle(TableStyle([('BACKGROUND', (0,0), (1,0), colors.HexColor('#1A365D')), ('TEXTCOLOR', (0,0), (1,0), colors.white), ('BOTTOMPADDING', (0,0), (-1,-1), 7), ('TOPPADDING', (0,0), (-1,-1), 7), ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')), ('BACKGROUND', (0,-1), (1,-1), colors.HexColor('#E2E8F0')), ('FONTNAME', (0,-1), (1,-1), 'Helvetica-Bold')]))
            story.append(t_grid)
            story.append(Spacer(1, 25))
            story.append(Paragraph("<b>REMITTANCE INSTRUCTIONS:</b>", styles['Heading3']))
            story.append(Paragraph(f"<b>PAYMENT TERMS: QUICK PAY SAME DAY</b>. Please route all fast-funding remittance transfers directly through our verified corporate bank profile wire setup.", m_style))
            doc.build(story)
            st.session_state["last_invoice_id"] = f_id
            st.session_state["last_invoice_path"] = pdf_out
            st.rerun()

    if "last_invoice_id" in st.session_state:
        with open(st.session_state["last_invoice_path"], "rb") as file: st.download_button(label=f"📥 Download Invoice {st.session_state['last_invoice_id']} PDF Directly", data=file, file_name=f"Invoice_{st.session_state['last_invoice_id']}.pdf", mime="application/pdf")

    st.subheader("🗂️ Active Accounts Receivable Ledger")
    if not inv_df.empty:
        for idx, r in inv_df.iterrows():
            col_a, col_b, col_c, col_d, col_e = st.columns([3, 2, 2, 1, 1])
            with col_a: st.text(f"📄 {r['Invoice_ID']} - {r['Customer_Name']}")
            with col_b: st.text(f"💰 ${float(r['Total_Amount']):,.2f}")
            with col_c:
                target_pdf_path = f"{PDF_FOLDER}Invoice_{r['Invoice_ID']}.pdf"
                if os.path.exists(target_pdf_path):
                    with open(target_pdf_path, "rb") as pdf_file: st.download_button(label="📥 PDF", data=pdf_file, file_name=f"Invoice_{r['Invoice_ID']}.pdf", mime="application/pdf", key=f"dl_{r['Invoice_ID']}_{idx}")
            with col_d:
                if st.button("✏️ Edit", key=f"edt_{r['Invoice_ID']}_{idx}"): st.session_state["editing_invoice_id"] = r["Invoice_ID"]; st.rerun()
            with col_e:
                if st.button("🗑️ Del", key=f"del_{r['Invoice_ID']}_{idx}"): inv_df = inv_df[inv_df["Invoice_ID"] != r["Invoice_ID"]]; inv_df.to_csv(INVOICE_DB_PATH, index=False); st.rerun()

# ==============================================================================
# TAB 7: MOVE SCHEDULER & DRIVER LOGS
# ==============================================================================
elif app_mode == "📋 Move Scheduler & Driver Logs":
    st.header("📋 Multi-Move Scheduler & Daily Driver Sheet")
    logs_df = pd.read_csv(LOGS_DB_PATH)
    if "num_moves" not in st.session_state: st.session_state["num_moves"] = 2

    with st.form("multi_move_driver_form"):
        col_m1, col_m2 = st.columns(2)
        with col_m1: f_driver = st.text_input("Driver / Fleet Operator Name", placeholder="e.g., John Doe")
        with col_m2: f_date = st.text_input("Log Date [YYYY-MM-DD]", value=datetime.today().strftime('%Y-%m-%d'))
            
        st.markdown("---")
        h_c1, h_c2, h_c3, h_c4, h_c5, h_c6 = st.columns([1, 2, 2, 2, 2, 1])
        with h_c1: st.caption("**Leg Run**")
        with h_c2: st.caption("**Container ID**")
        with h_c3: st.caption("**Pick-up Location**")
        with h_c4: st.caption("**Drop-off / Delivery Location**")
        with h_c5: st.caption("**Container Return Location**")
        with h_c6: st.caption("**Hours Worked**")

        move_data_entries = []
        for i in range(st.session_state["num_moves"]):
            r_c1, r_c2, r_c3, r_c4, r_c5, r_c6 = st.columns([1, 2, 2, 2, 2, 1])
            with r_c1: st.markdown(f"<p style='padding:8px 0px;'><b>Move #{i+1}</b></p>", unsafe_allow_html=True)
            with r_c2: r_cont = st.text_input("Container #", key=f"mc_cont_{i}", label_visibility="collapsed")
            with r_c3: r_pick = st.text_input("Pick up point", key=f"mc_pick_{i}", label_visibility="collapsed")
            with r_c4: r_drop = st.text_input("Delivery spot", key=f"mc_drop_{i}", label_visibility="collapsed")
            with r_c5: r_ret = st.text_input("Return location", key=f"mc_ret_{i}", label_visibility="collapsed")
            with r_c6: r_hrs = st.number_input("Hours", min_value=0.0, step=0.5, key=f"mc_hrs_{i}", label_visibility="collapsed")
            move_data_entries.append({"Container": r_cont, "Pick": r_pick, "Drop": r_drop, "Return": r_ret, "Hours": r_hrs})

        total_day_hours = sum([item["Hours"] for item in move_data_entries])
        st.markdown("---")
        d_col1, d_col2 = st.columns([3, 1])
        with d_col1: st.info("💡 Need to log more runs? Click 'Add Row' outside this box.")
        with d_col2: st.metric("Total Day Hours Worked", f"⏱️ {total_day_hours} Hrs")
        commit_day_sheet = st.form_submit_button("Commit Daily Sheet")

    x_c1, x_c2 = st.columns(2)
    with x_c1:
        if st.button("➕ Add Row Line Item"): st.session_state["num_moves"] += 1; st.rerun()
    with x_c2:
        if st.button("➖ Remove Row Line Item") and st.session_state["num_moves"] > 1: st.session_state["num_moves"] -= 1; st.rerun()

    if commit_day_sheet:
        if not f_driver: st.error("⚠️ Driver Name required.")
        else:
            session_batch_id = f"BATCH-{int(datetime.now().timestamp())}"
            new_rows_batch = []
            for index, move in enumerate(move_data_entries):
                if move["Container"]:
                    new_rows_batch.append({"ID": session_batch_id, "Date": f_date, "Driver_Name": f_driver, "Move_Index": index + 1, "Pickup_Location": move["Pick"], "Delivery_Location": move["Drop"], "Return_Location": move["Return"], "Hours_Worked": move["Hours"], "Container_Num": move["Container"]})
            if new_rows_batch:
                pd.concat([logs_df, pd.DataFrame(new_rows_batch)], ignore_index=True).to_csv(LOGS_DB_PATH, index=False)
                st.success("🎉 Committed operational hours!")
                st.rerun()

    st.markdown("---")
    st.subheader("📋 Historical Driver Log Sheets")
    if not logs_df.empty: st.dataframe(logs_df, use_container_width=True)

# ==============================================================================
# TAB 8: COMPLIANCE & SAFETY TRACKING
# ==============================================================================
elif app_mode == "🛡️ Compliance & Safety Tracking":
    st.header("🛡️ FMCSA Corporate Safety Registry & Compliance Matrix")
    st.caption("Log federal highway mandates, manage drug screenings, driver qualifications, and ELD statuses.")

    sub_tab = st.tabs(["🧪 Drug Test Control", "📁 Driver Qualification Documents", "📟 ELD Tracking Logs", "⚠️ Safety Violations Log"])

    with sub_tab[0]:
        st.subheader("🧪 Controlled Substance Testing Log")
        drug_df = pd.read_csv(DRUG_DB_PATH).fillna("")
        
        with st.form("drug_test_form", clear_on_submit=True):
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                dt_name = st.text_input("Driver Name")
                dt_date = st.text_input("Date of Drug Test [YYYY-MM-DD]", value=datetime.today().strftime('%Y-%m-%d'))
                dt_reason = st.selectbox("Reason for Drug Test", ["Pre-Employment", "Random Screening", "Post-Accident", "Reasonable Suspicion", "Return-to-Duty"])
                dt_result = st.selectbox("Test Result", ["Negative (Passed)", "Positive (Failed)", "Refusal to Test", "Inconclusive"])
            with col_d2:
                dt_rand_date = st.text_input("Random Selection Date [YYYY-MM-DD]", value="None")
                dt_rand_res = st.selectbox("Random Screening Result", ["N/A - Not Selected", "Negative (Passed)", "Positive (Failed)"])
                dt_exp = st.text_input("Commercial Driver License (CDL) Expiration [YYYY-MM-DD]")
            dt_submit = st.form_submit_button("Commit Drug Test Entry")

        if dt_submit:
            if not dt_name: st.error("⚠️ Please specify a Driver Name.")
            else:
                new_row = {"ID": f"DG-{len(drug_df)+1001}", "Driver_Name": dt_name, "Drug_Test_Date": dt_date, "Reason": dt_reason, "Result": dt_result, "Random_Test_Date": dt_rand_date, "Random_Result": dt_rand_res, "License_Expiration": dt_exp}
                pd.concat([drug_df, pd.DataFrame([new_row])], ignore_index=True).to_csv(DRUG_DB_PATH, index=False)
                st.success("🎉 Drug test metric committed securely!")
                st.rerun()

        st.markdown("---")
        st.subheader("🗂️ Active Driver Testing Records")
        if not drug_df.empty:
            for idx, r in drug_df.iterrows():
                c_a, c_b, c_c = st.columns([4, 4, 1])
                with c_a: st.markdown(f"👤 **{r['Driver_Name']}** | CDL Exp: `{r['License_Expiration']}`<br/>📋 Test Reason: *{r['Reason']}* | Date: `{r['Drug_Test_Date']}`", unsafe_allow_html=True)
                with c_b: st.markdown(f"🧬 Result: **{r['Result']}**<br/>🎯 Random Test: `{r['Random_Test_Date']}` -> *{r['Random_Result']}*", unsafe_allow_html=True)
                with c_c:
                    if st.button("🗑️", key=f"del_drg_{r['ID']}_{idx}"): drug_df[drug_df["ID"] != r["ID"]].to_csv(DRUG_DB_PATH, index=False); st.rerun()
        else: st.write("No testing entries archived.")

    with sub_tab[1]:
        st.subheader("📁 Mandatory Driver Qualification Files (DQF)")
        docs_df = pd.read_csv(DOCS_DB_PATH).fillna("")

        with st.form("driver_docs_form", clear_on_submit=True):
            dc_name = st.text_input("Driver Name Reference")
            st.markdown("**Select Verified Document Statuses on File:**")
            cx1, cx2, cx3 = st.columns(3)
            with cx1:
                chk_app = st.checkbox("Checklist for Application Completed")
                chk_drg = st.checkbox("Drug Test Report Received & Archived")
            with cx2:
                chk_med = st.checkbox("Medical Examiner's Certificate (Med Test Card)")
                chk_haz = st.checkbox("Hazmat Certification Endorsement (If applicable)")
            with cx3:
                chk_mvr = st.checkbox("Motor Vehicle Record (MVR) Background Check Clear")
                chk_trn = st.checkbox("Driver Safety Training Clearance Certificate")
            dc_notes = st.text_area("Custom Situation Audit Notes / Additional File Details")
            dc_submit = st.form_submit_button("Update DQF Document Profile")

        if dc_submit:
            if not dc_name: st.error("⚠️ Driver Name required.")
            else:
                new_row = {"ID": f"DC-{len(docs_df)+1001}", "Driver_Name": dc_name, "App_Checklist": "PASSED" if chk_app else "MISSING", "Drug_Report": "PASSED" if chk_drg else "MISSING", "Medical_Test": "PASSED" if chk_med else "MISSING", "Hazmat_Cert": "PASSED" if chk_haz else "MISSING", "MVR": "PASSED" if chk_mvr else "MISSING", "Training": "PASSED" if chk_trn else "MISSING", "Situation_Notes": dc_notes}
                pd.concat([docs_df, pd.DataFrame([new_row])], ignore_index=True).to_csv(DOCS_DB_PATH, index=False)
                st.success("🎉 Driver Qualification Document metrics logged.")
                st.rerun()

        st.markdown("---")
        st.subheader("🗂️ Active Qualification File Auditor")
        if not docs_df.empty:
            for idx, r in docs_df.iterrows():
                c_a, c_b, c_c = st.columns([3, 5, 1])
                with c_a: st.markdown(f"👤 **{r['Driver_Name']}**<br/>📝 *Notes: {r['Situation_Notes']}*", unsafe_allow_html=True)
                with c_b: st.caption(f"App: {r['App_Checklist']} | Drug: {r['Drug_Report']} | Med: {r['Medical_Test']} | Hazmat: {r['Hazmat_Cert']} | MVR: {r['MVR']} | Training: {r['Training']}")
                with c_c:
                    if st.button("🗑️", key=f"del_doc_{r['ID']}_{idx}"): docs_df[docs_df["ID"] != r["ID"]].to_csv(DOCS_DB_PATH, index=False); st.rerun()
        else: st.write("No document profiles compiled.")

    with sub_tab[2]:
        st.subheader("📟 Electronic Logging Device Hardware Registry")
        eld_df = pd.read_csv(ELD_DB_PATH).fillna("")

        with st.form("eld_form", clear_on_submit=True):
            el_truck = st.text_input("Truck Number", placeholder="e.g., TRK-501")
            el_conn = st.selectbox("ELD Hardware Connected Status", ["ELD Connected & Active", "Hardware Malfunction", "Disconnected / Standby"])
            el_num = st.text_input("ELD Device Serial Identifier Number", placeholder="e.g., ELD-998231")
            el_submit = st.form_submit_button("Save Truck ELD Pairing")

        if el_submit:
            if not el_truck or not el_num: st.error("⚠️ Truck number and ELD identifier code required.")
            else:
                new_row = {"ID": f"EL-{len(eld_df)+1001}", "Truck_Number": el_truck, "ELD_Connected": el_conn, "ELD_Number": el_num}
                pd.concat([eld_df, pd.DataFrame([new_row])], ignore_index=True).to_csv(ELD_DB_PATH, index=False)
                st.success("🎉 ELD pairing metrics committed across system arrays!")
                st.rerun()

        st.markdown("---")
        st.subheader("🗂️ Hardware Pairing Fleet Inventory")
        if not eld_df.empty:
            for idx, r in eld_df.iterrows():
                c_a, c_b, c_c = st.columns([4, 4, 1])
                with c_a: st.markdown(f"🚛 Truck ID: **{r['Truck_Number']}**")
                with c_b: st.markdown(f"📟 Serial: `{r['ELD_Number']}` | Link Status: *{r['ELD_Connected']}*")
                with c_c:
                    if st.button("🗑️", key=f"del_eld_{r['ID']}_{idx}"): eld_df[eld_df["ID"] != r["ID"]].to_csv(ELD_DB_PATH, index=False); st.rerun()
        else: st.write("No ELD systems paired.")

    with sub_tab[3]:
        st.subheader("⚠️ Internal Corporate Infractions & Roadside Violations Log")
        violation_df = pd.read_csv(VIOLATION_DB_PATH).fillna("")

        with st.form("violation_form", clear_on_submit=True):
            v_driver = st.text_input("Driver Name")
            v_truck = st.text_input("Truck Number involved")
            v_type = st.selectbox("Violation Type", ["Hours of Service (HOS) Breach", "Speeding / Moving Violation", "Overweight Axle Load", "Pre-Trip Inspection Omission", "Equipment Maintenance Defect", "Port Gate Infraction", "Other / Miscellaneous Custom Entry"])
            v_action = st.text_input("Action Taken / Correction Protocol Applied", placeholder="e.g., Driver safety re-training completed")
            v_remarks = st.text_area("Detailed Incident Safety Remarks")
            v_submit = st.form_submit_button("Log Incident File Entry")

        if v_submit:
            if not v_driver or not v_truck: st.error("⚠️ Please assign the Driver Name and Truck Number fields.")
            else:
                new_row = {"ID": f"VL-{len(violation_df)+1001}", "Driver_Name": v_driver, "Truck_Number": v_truck, "Violation_Type": v_type, "Action_Taken": v_action, "Remarks": v_remarks}
                pd.concat([violation_df, pd.DataFrame([new_row])], ignore_index=True).to_csv(VIOLATION_DB_PATH, index=False)
                st.success("🎉 Incident violation file successfully logged!")
                st.rerun()

        st.markdown("---")
        st.subheader("🗂️ Historical Violation Records Data Matrix")
        if not violation_df.empty:
            for idx, r in violation_df.iterrows():
                c_a, c_b, c_c = st.columns([4, 4, 1])
                with c_a: st.markdown(f"👤 Driver: **{r['Driver_Name']}** | 🚛 Truck: `{r['Truck_Number']}`<br/>🛑 Incident Type: *{r['Violation_Type']}*", unsafe_allow_html=True)
                with c_b: st.markdown(f"🛠️ Action: *{r['Action_Taken']}*<br/>📝 Summary: *{r['Remarks']}*", unsafe_allow_html=True)
                with c_c:
                    if st.button("🗑️", key=f"del_vio_{r['ID']}_{idx}"): violation_df[violation_df["ID"] != r["ID"]].to_csv(VIOLATION_DB_PATH, index=False); st.rerun()
        else: st.write("Clean Record Sheet. No safety incidents logged.")

# ==============================================================================
# TAB 9: TO-DO LIST MANAGER
# ==============================================================================
elif app_mode == "📝 To-Do List Manager":
    st.header("📝 Operational To-Do Tasks Manager")
    todo_df = pd.read_csv(TODO_DB_PATH).fillna("")
    
    st.subheader("➕ Add New Pending Assignment")
    with st.form("todo_input_form", clear_on_submit=True):
        col_t1, col_t2 = st.columns([2, 1])
        with col_t1: t_desc = st.text_input("Task / Action Required Description")
        with col_t2:
            t_date = st.text_input("Target Due Date [YYYY-MM-DD]", value=datetime.today().strftime('%Y-%m-%d'))
            t_priority = st.selectbox("Task Priority Level", ["🔴 High Priority", "🟡 Medium Priority", "🟢 Low Priority"])
        submit_task = st.form_submit_button("Lock Task onto Action Tracker Ledger")
        
    if submit_task:
        if not t_desc: st.error("⚠️ Form rejected: Please describe the task requirement details.")
        else:
            new_task_row = {"Task_ID": f"TD-{int(datetime.now().timestamp())}", "Task_Description": t_desc, "Due_Date": t_date, "Priority": t_priority, "Status": "Pending"}
            pd.concat([todo_df, pd.DataFrame([new_task_row])], ignore_index=True).to_csv(TODO_DB_PATH, index=False)
            st.success("🎉 Task added successfully!")
            st.rerun()
            
    st.markdown("---")
    st.subheader("📌 Open Operational Action Assignments")
    if not todo_df.empty:
        pending_items = todo_df[todo_df["Status"] == "Pending"]
        completed_items = todo_df[todo_df["Status"] == "Completed"]
        
        if not pending_items.empty:
            for idx, task in pending_items.iterrows():
                t_col1, t_col2, t_col3, t_col4 = st.columns([4, 2, 2, 1])
                with t_col1: st.markdown(f"📋 {task['Task_Description']}")
                with t_col2: st.markdown(f"📅 Due: `{task['Due_Date']}`")
                with t_col3: st.markdown(f"⚠️ Status: **{task['Priority']}**")
                with t_col4:
                    if st.button("✅ Done", key=f"todo_done_{task['Task_ID']}_{idx}"): todo_df.at[idx, "Status"] = "Completed"; todo_df.to_csv(TODO_DB_PATH, index=False); st.rerun()
        else: st.success("☀️ Outstanding task ledger clear!")
            
        if not completed_items.empty:
            st.markdown("---")
            with st.expander("📂 View Recently Completed Tasks Archive"):
                for idx, task in completed_items.iterrows():
                    tc_col1, tc_col2, tc_col3 = st.columns([5, 3, 1])
                    with tc_col1: st.markdown(f"<s>✅ {task['Task_Description']}</s>", unsafe_allow_html=True)
                    with tc_col2: st.caption(f"Finished Tracker Ref: `{task['Task_ID']}`")
                    with tc_col3:
                        if st.button("🗑️ Clear", key=f"todo_del_{task['Task_ID']}_{idx}"): todo_df = todo_df[todo_df["Task_ID"] != task["Task_ID"]]; todo_df.to_csv(TODO_DB_PATH, index=False); st.rerun()
