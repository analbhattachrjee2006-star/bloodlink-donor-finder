# BloodLink — Local Blood Donor Directory (Prototype)

A Python-only web prototype built for **CodesClash 2026** that helps people search for potential local blood donors by blood group and area, register as sample donors, and submit blood requests—without needing HTML, CSS, or JavaScript[cite: 3, 5, 6].

> **Medical & Privacy Disclaimer:** This application uses strictly fictional/sample data. Listed profiles are not medically verified, and availability is not guaranteed. Always contact licensed hospitals or blood banks for actual blood requirements.

---

## Phase 1: Problem & Requirements

* **Problem:** During medical emergencies, finding matching blood donors nearby is slow because donor details are scattered across messages, spreadsheets, and outdated lists.
* **Solution:** A clean, searchable directory where requesters can filter local donors by blood group and locality, and send a contact request[cite: 3].
* **User Roles:**
  * **Requester:** Searches donors and submits a blood request[cite: 3].
  * **Donor:** Adds a sample profile with blood group, area, and availability[cite: 3].
  * **Admin:** Approves new donor entries, deactivates outdated ones, and tracks incoming requests[cite: 3].

---

## Phase 2: System Design & Architecture

### Architecture
```text
Browser / Mobile (Streamlit UI)
       │
       ▼
Python Logic (Filtering, Form Validation, Admin Auth)
       │
       ▼
SQLite Database (donors.db) ──► [ donors ] & [ requests ] tables
erDiagram
    DONORS ||--o{ REQUESTS : receives
    DONORS {
        int id PK
        string name
        string blood_group
        string city
        string locality
        string pin_code
        string availability
        string contact_handle
        string status
    }
    REQUESTS {
        int id PK
        int donor_id FK
        string requester_name
        string blood_group
        string hospital_area
        string urgency
        string message
        string status
    }
    blood-donor-finder/
├── app.py               # Main Streamlit web application
├── db.py                # SQLite setup, queries, and sample data seeding
├── requirements.txt     # Python dependencies (only streamlit & pandas)
└── README.md            # Project documentation
### Database work-flow
init_db()
   │
   ▼
Connect to database
   │
   ▼
Create cursor
   │
   ▼
Create tables (if needed)
   │
   ▼
Check donor count
   │
   ▼
Is count = 0 ?
   │
 ┌─Yes─────────────┐
 ▼                 │
Insert sample      │
donors             │
 └─────────────────┘
   │
   ▼
Commit changes
   │
   ▼
Close connection