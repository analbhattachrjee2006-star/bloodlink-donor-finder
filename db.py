import sqlite3

DB_NAME = "donors.db"

def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            city TEXT NOT NULL,
            locality TEXT NOT NULL,
            pin_code TEXT NOT NULL,
            availability TEXT NOT NULL,
            contact_handle TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_id INTEGER,
            requester_name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            hospital_area TEXT NOT NULL,
            urgency TEXT NOT NULL,
            message TEXT,
            status TEXT DEFAULT 'Open'
        )
    """)
    
    # Seed fictional sample data if table is empty
    cur.execute("SELECT COUNT(*) FROM donors")
    if cur.fetchone()[0] == 0:
        sample_donors = [
            ("Aarav S. (Sample)", "O+", "Kolkata", "Salt Lake", "700091", "Available on Call", "aarav.demo@example.test", "Approved"),
            ("Priya M. (Sample)", "A+", "Kolkata", "Jadavpur", "700032", "Weekends Only", "priya.demo@example.test", "Approved"),
            ("Rohan K. (Sample)", "B+", "Kolkata", "Behala", "700034", "Available on Call", "rohan.demo@example.test", "Approved"),
            ("Sneha D. (Sample)", "O-", "Kolkata", "Gariahat", "700019", "Available on Call", "sneha.demo@example.test", "Approved"),
            ("Vikram R. (Sample)", "AB+", "Kolkata", "New Town", "700156", "Evenings Only", "vikram.demo@example.test", "Approved"),
            ("Ananya G. (Sample)", "B-", "Kolkata", "Tollygunge", "700033", "Available on Call", "ananya.demo@example.test", "Pending"),
        ]
        cur.executemany("""
            INSERT INTO donors (name, blood_group, city, locality, pin_code, availability, contact_handle, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_donors)
        
    conn.commit()
    conn.close()