import streamlit as st
import pandas as pd
from db import get_conn, init_db

st.set_page_config(page_title="BloodLink Donor Finder", page_icon="🩸", layout="wide")
init_db()

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]

# Header & Mandatory Safety Disclaimer
st.title("🩸 BloodLink — Community Blood Donor Directory")
st.warning(
    "⚠️ **Prototype Notice:** All profiles shown are fictional sample data[cite: 3]. "
    "Medical eligibility and real-time availability are not verified[cite: 3]. "
    "For medical emergencies, please contact a licensed hospital or blood bank directly[cite: 3]."
)

tab1, tab2, tab3 = st.tabs(["🔍 Find a Donor", "➕ Register as Donor", "🛡️ Admin Panel"])

# --- TAB 1: SEARCH & REQUEST ---
with tab1:
    st.subheader("Search Potential Donors")
    col1, col2 = st.columns(2)
    with col1:
        selected_bg = st.selectbox("Select Blood Group", ["All"] + BLOOD_GROUPS)
    with col2:
        location_query = st.text_input("Filter by City, Locality, or PIN Code", placeholder="e.g., Salt Lake or 700091")

    conn = get_conn()
    query = "SELECT id, name, blood_group, city, locality, pin_code, availability, contact_handle FROM donors WHERE status = 'Approved'"
    params = []

    if selected_bg != "All":
        query += " AND blood_group = ?"
        params.append(selected_bg)
    if location_query.strip():
        query += " AND (city LIKE ? OR locality LIKE ? OR pin_code LIKE ?)"
        like_term = f"%{location_query.strip()}%"
        params.extend([like_term, like_term, like_term])

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if df.empty:
        st.info("No matching approved donors found for this filter.")
    else:
        st.dataframe(df.drop(columns=["id"]), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Send a Contact / Blood Request")
        with st.form("request_form", clear_on_submit=True):
            donor_options = {f"{row['name']} ({row['blood_group']} - {row['locality']})": row['id'] for _, row in df.iterrows()}
            chosen_donor = st.selectbox("Select Donor to Contact", list(donor_options.keys()))
            req_name = st.text_input("Your Name (Requester)")
            hospital = st.text_input("Hospital / Area Name")
            urgency = st.selectbox("Urgency Level", ["Critical (Within 6 hrs)", "Urgent (Within 24 hrs)", "Planned"])
            msg = st.text_area("Message / Note")
            submitted = st.form_submit_button("Submit Request")

            if submitted:
                if not req_name.strip() or not hospital.strip():
                    st.error("Please fill in your name and hospital/area.")
                else:
                    conn = get_conn()
                    conn.execute(
                        "INSERT INTO requests (donor_id, requester_name, blood_group, hospital_area, urgency, message) VALUES (?, ?, ?, ?, ?, ?)",
                        (donor_options[chosen_donor], req_name, selected_bg if selected_bg != "All" else "Matched", hospital, urgency, msg)
                    )
                    conn.commit()
                    conn.close()
                    st.success("Request logged! In a live system, this would notify the donor via verified channels.")

# --- TAB 2: DONOR REGISTRATION ---
with tab2:
    st.subheader("Register a Sample Donor Profile")
    st.caption("Please enter fictional details only for hackathon demonstration purposes[cite: 3].")
    with st.form("donor_form", clear_on_submit=True):
        d_name = st.text_input("Display Name / Alias", placeholder="e.g., Kabir R. (Sample)")
        c1, c2 = st.columns(2)
        with c1:
            d_bg = st.selectbox("Blood Group", BLOOD_GROUPS)
            d_city = st.text_input("City", value="Kolkata")
            d_pin = st.text_input("PIN Code", placeholder="e.g., 700091")
        with c2:
            d_locality = st.text_input("Locality / Area", placeholder="e.g., Ballygunge")
            d_avail = st.selectbox("Availability Preference", ["Available on Call", "Weekends Only", "Evenings Only"])
            d_contact = st.text_input("Fictional Contact Handle", placeholder="e.g., kabir.demo@example.test")
        
        reg_submit = st.form_submit_button("Submit Profile for Review")
        if reg_submit:
            if not all([d_name.strip(), d_city.strip(), d_locality.strip(), d_pin.strip(), d_contact.strip()]):
                st.error("All fields are required.")
            else:
                conn = get_conn()
                conn.execute(
                    "INSERT INTO donors (name, blood_group, city, locality, pin_code, availability, contact_handle, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending')",
                    (d_name, d_bg, d_city, d_locality, d_pin, d_avail, d_contact)
                )
                conn.commit()
                conn.close()
                st.success("Profile submitted! An administrator must approve it in the Admin Panel before it appears publicly.")

# --- TAB 3: ADMIN PANEL ---
with tab3:
    st.subheader("Administrator Moderation")
    admin_pin = st.text_input("Enter Admin PIN (Demo PIN: 1234)", type="password")
    
    if admin_pin == "1234":
        conn = get_conn()
        all_donors = pd.read_sql_query("SELECT * FROM donors", conn)
        all_requests = pd.read_sql_query("SELECT * FROM requests", conn)

        st.markdown("### Manage Donor Listings")
        st.dataframe(all_donors, use_container_width=True, hide_index=True)

        col_a, col_b, col_c = st.columns([2, 2, 1])
        with col_a:
            target_id = st.number_input("Donor ID to Update", min_value=1, step=1)
        with col_b:
            new_status = st.selectbox("New Status", ["Approved", "Pending", "Deactivated"])
        with col_c:
            st.write("")
            st.write("")
            if st.button("Update Status"):
                conn.execute("UPDATE donors SET status = ? WHERE id = ?", (new_status, target_id))
                conn.commit()
                st.success(f"Donor #{target_id} updated to {new_status}.")
                st.rerun()

        st.markdown("### Incoming Blood Requests")
        if all_requests.empty:
            st.info("No blood requests submitted yet.")
        else:
            st.dataframe(all_requests, use_container_width=True, hide_index=True)
        conn.close()
    elif admin_pin:
        st.error("Incorrect PIN.")