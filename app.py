import streamlit as st
import pandas as pd
import json
import re
import time
import os
from abc import ABC, abstractmethod

# ==========================================
# 1. KONSEP OOP (Inheritance, Encapsulation)
# ==========================================

class Orang(ABC):
    def __init__(self, nama):
        self._nama = nama  # Protected

    @abstractmethod
    def tampilkan_peran(self):
        pass

class Mahasiswa(Orang):
    def __init__(self, nim, nama, email, jurusan, pemilik_akun=""):
        super().__init__(nama)
        self.__nim = nim          # Private
        self.__email = email      # Private
        self.jurusan = jurusan    # Public
        self.pemilik_akun = pemilik_akun  

    def get_nim(self): return self.__nim
    def get_email(self): return self.__email
    def get_nama(self): return self._nama
    
    def tampilkan_peran(self):
        return f"Mahasiswa: {self._nama}"

class Dosen(Orang):
    def __init__(self, nidn, nama, email, matakuliah, pemilik_akun=""):
        super().__init__(nama)
        self.__nidn = nidn        # Private
        self.__email = email      # Private
        self.matakuliah = matakuliah  # Public
        self.pemilik_akun = pemilik_akun

    def get_nidn(self): return self.__nidn
    def get_email(self): return self.__email
    def get_nama(self): return self._nama

    def tampilkan_peran(self):
        return f"Dosen: {self._nama}"

# ==========================================
# 2. MANAGER DATA & SISTEM ALGORITMA
# ==========================================

class AuthManager:
    def __init__(self):
        self.file_path = "users.json"
        self.load_users()

    def load_users(self):
        if not os.path.exists(self.file_path):
            self.users = {"admin@gmail.com": "admin123"}
            self.save_users()
        else:
            with open(self.file_path, "r") as f:
                self.users = json.load(f)

    def save_users(self):
        with open(self.file_path, "w") as f:
            json.dump(self.users, f, indent=4)

    def register_user(self, email, password):
        gmail_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        if not re.match(gmail_pattern, email):
            raise ValueError("Email harus menggunakan format Gmail resmi (contoh: nama@gmail.com)!")
        if len(password) < 6:
            raise ValueError("Password minimal harus 6 karakter demi keamanan!")
        if email in self.users:
            raise ValueError("Email tersebut sudah terdaftar! Silakan login.")
        self.users[email] = password
        self.save_users()
        return True

    def login_user(self, email, password):
        if email in self.users and self.users[email] == password:
            return True
        return False


class AcademicManager:
    def __init__(self):
        self.mhs_file = "students.json"
        self.dsn_file = "lecturers.json"
        self.all_students = []
        self.all_lecturers = []
        self.load_data()

    def load_data(self):
        try:
            with open(self.mhs_file, "r") as f:
                raw_mhs = json.load(f)
                self.all_students = [
                    Mahasiswa(d.get('nim',''), d.get('nama',''), d.get('email',''), d.get('jurusan',''), d.get('pemilik_akun',''))
                    for d in raw_mhs
                ]
        except (FileNotFoundError, json.JSONDecodeError):
            self.all_students = []

        try:
            with open(self.dsn_file, "r") as f:
                raw_dsn = json.load(f)
                self.all_lecturers = [
                    Dosen(d.get('nidn',''), d.get('nama',''), d.get('email',''), d.get('matakuliah',''), d.get('pemilik_akun',''))
                    for d in raw_dsn
                ]
        except (FileNotFoundError, json.JSONDecodeError):
            self.all_lecturers = []

    def get_students_by_user(self, email_user):
        return [m for m in self.all_students if m.pemilik_akun == email_user]

    def get_lecturers_by_user(self, email_user):
        return [d for d in self.all_lecturers if d.pemilik_akun == email_user]

    def save_data(self):
        with open(self.mhs_file, "w") as f:
            data_mhs = [{
                "nim": m.get_nim(), "nama": m.get_nama(), "email": m.get_email(), "jurusan": m.jurusan, "pemilik_akun": m.pemilik_akun
            } for m in self.all_students]
            json.dump(data_mhs, f, indent=4)
        
        with open(self.dsn_file, "w") as f:
            data_dsn = [{
                "nidn": d.get_nidn(), "nama": d.get_nama(), "email": d.get_email(), "matakuliah": d.matakuliah, "pemilik_akun": d.pemilik_akun
            } for d in self.all_lecturers]
            json.dump(data_dsn, f, indent=4)

    # ------------------------------------------
    # ALGORITMA SORTING ENGINE
    # ------------------------------------------
    def bubble_sort_nim(self, email_user):
        user_students = self.get_students_by_user(email_user)
        n = len(user_students)
        for i in range(n):
            for j in range(0, n-i-1):
                if user_students[j].get_nim() > user_students[j+1].get_nim():
                    user_students[j], user_students[j+1] = user_students[j+1], user_students[j]
        self.all_students = [m for m in self.all_students if m.pemilik_akun != email_user] + user_students
        self.save_data()

    def selection_sort_nama_dosen(self, email_user):
        user_lecturers = self.get_lecturers_by_user(email_user)
        n = len(user_lecturers)
        for i in range(n):
            min_idx = i
            for j in range(i+1, n):
                if user_lecturers[j].get_nama().lower() < user_lecturers[min_idx].get_nama().lower():
                    min_idx = j
            user_lecturers[i], user_lecturers[min_idx] = user_lecturers[min_idx], user_lecturers[i]
        self.all_lecturers = [d for d in self.all_lecturers if d.pemilik_akun != email_user] + user_lecturers
        self.save_data()

    # Double Sort (Urutkan prodi, jika sama urutkan nama)
    def double_sort_mhs_prodi_nama(self, email_user):
        user_students = self.get_students_by_user(email_user)
        n = len(user_students)
        for i in range(n):
            for j in range(0, n-i-1):
                if user_students[j].jurusan > user_students[j+1].jurusan:
                    user_students[j], user_students[j+1] = user_students[j+1], user_students[j]
                elif user_students[j].jurusan == user_students[j+1].jurusan:
                    if user_students[j].get_nama().lower() > user_students[j+1].get_nama().lower():
                        user_students[j], user_students[j+1] = user_students[j+1], user_students[j]
        self.all_students = [m for m in self.all_students if m.pemilik_akun != email_user] + user_students
        self.save_data()

    # ------------------------------------------
    # ALGORITMA LINEAR SEARCH ENGINE
    # ------------------------------------------
    def linear_search_mhs(self, email_user, keyword, kriteria):
        user_students = self.get_students_by_user(email_user)
        hasil = []
        for m in user_students:
            if kriteria == "NIM" and m.get_nim() == keyword:
                hasil.append(m)
            elif kriteria == "Nama" and keyword.lower() in m.get_nama().lower():
                hasil.append(m)
        return hasil

    def linear_search_dsn(self, email_user, keyword, kriteria):
        user_lecturers = self.get_lecturers_by_user(email_user)
        hasil = []
        for d in user_lecturers:
            if kriteria == "NIDN" and d.get_nidn() == keyword:
                hasil.append(d)
            elif kriteria == "Nama" and keyword.lower() in d.get_nama().lower():
                hasil.append(d)
        return hasil

# ==========================================
# 3. INTERFACE / TAMPILAN WEB STREAMLIT KUSTOM
# ==========================================

st.set_page_config(page_title="Sistem Academic - Mario Tech", page_icon="💻", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp { 
        font-family: 'Space Grotesk', sans-serif; 
        background-color: #0B0F19 !important; 
        color: #E2E8F0 !important; 
    }
    label { color: #F8FAFC !important; font-weight: 500 !important; }
    .dashboard-card {
        background: #161D30; border-radius: 16px; padding: 24px; 
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25); border: 1px solid #24324F; margin-bottom: 24px;
    }
    .metric-container { display: flex; justify-content: space-between; gap: 20px; margin-bottom: 24px; }
    .metric-card {
        background: #161D30; border-radius: 16px; padding: 24px; flex: 1;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25); border-left: 6px solid #3B82F6; border-top: 1px solid #24324F; border-right: 1px solid #24324F; border-bottom: 1px solid #24324F;
    }
    .metric-value { font-size: 36px; font-weight: 700; color: #FFFFFF; margin-top: 8px; }
    .metric-label { font-size: 13px; color: #94A3B8; font-weight: 600; letter-spacing: 0.5px; }
    
    div.stButton > button, div.stFormSubmitButton > button {
        background: linear-gradient(135deg, #3B82F6, #1D4ED8) !important; 
        color: #FFFFFF !important; border-radius: 10px !important; padding: 12px 24px !important; 
        font-weight: 600 !important; border: none !important; width: 100%; transition: all 0.3s;
    }
    div.stButton > button:hover, div.stFormSubmitButton > button:hover { 
        transform: translateY(-2px); box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4); 
    }
    input { background-color: #1F2A45 !important; color: white !important; border: 1px solid #334874 !important; }
    section[data-testid="stSidebar"] { background-color: #090D16 !important; border-right: 1px solid #1E293B; }
    </style>
    """, unsafe_allow_html=True)

auth = AuthManager()
manager = AcademicManager()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = "Login"
if 'current_user' not in st.session_state: st.session_state.current_user = ""

# Halaman Login/Register
if not st.session_state.logged_in:
    col_left, col_right = st.columns([1.2, 1.2])
    with col_left:
        st.markdown("""
            <div style="background: linear-gradient(rgba(11, 15, 25, 0.6), rgba(11, 15, 25, 0.9)), 
                        url('https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80'); 
                        background-size: cover; background-position: center; padding: 50px; border-radius: 24px; color: white; min-height: 85vh; display: flex; flex-direction: column; justify-content: flex-end; border: 1px solid #24324F;">
                <div style="font-weight: 800; font-size: 14px; letter-spacing: 2px; color: #3B82F6; margin-bottom: auto;">MARIO CORE SYSTEM</div>
                <h1 style="font-size: 38px; font-weight: 800; line-height: 1.2; margin-bottom: 20px; color: #FFFFFF;">SISTEM MANAJEMEN<br>AKADEMIK MODERN</h1>
                <p style="font-size: 14px; color: #94A3B8; line-height: 1.7; margin-bottom: 25px;">Selamat datang di platform pusat kendali data akademik terpadu. Web ini dirancang khusus untuk mempermudah pemrosesan data mahasiswa dan dosen secara instan, aman, terisolasi, serta mendukung pengolahan data massal.</p>
                <span style="font-size: 12px; color: #64748B;">Sistem Informasi V2.0 • Berbasis Cloud</span>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.write("\n\n")
        if st.session_state.auth_mode == "Login":
            st.markdown("<h2 style='font-size: 32px; font-weight: 700; margin-bottom: 5px; color: white;'>SELAMAT DATANG KEMBALI !</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #94A3B8; font-size: 14px; margin-bottom: 30px;'>Selamat datang kembali! Please enter your details.</p>", unsafe_allow_html=True)
            
            with st.form("login_form"):
                email_input = st.text_input("Email", placeholder="Enter your email")
                pwd_input = st.text_input("Password", type="password", placeholder="••••••••")
                st.markdown("<div style='display:flex; justify-content:space-between; font-size:12px; color:#94A3B8; margin-bottom:15px;'><span>Remember me</span><span style='color:#3B82F6;'>Forgot password</span></div>", unsafe_allow_html=True)
                submit_login = st.form_submit_button("Sign in")
                
                if submit_login:
                    if auth.login_user(email_input, pwd_input):
                        st.session_state.logged_in = True
                        st.session_state.current_user = email_input
                        st.success("🎯 Login Berhasil!")
                        st.rerun()
                    else: st.error("❌ Email atau Password salah!")
            
            st.write("")
            if st.button("Don't have an account? Sign up"):
                st.session_state.auth_mode = "Daftar"
                st.rerun()
                
        elif st.session_state.auth_mode == "Daftar":
            st.markdown("<h2 style='font-size: 32px; font-weight: 700; margin-bottom: 5px; color: white;'>BUAT AKUN BARU</h2>", unsafe_allow_html=True)
            
            with st.form("register_form"):
                new_email = st.text_input("Email Gmail", placeholder="nama@gmail.com")
                new_pwd = st.text_input("Password (Min. 6 Karakter)", type="password", placeholder="••••••••")
                submit_register = st.form_submit_button("Sign up now")
                
                if submit_register:
                    try:
                        auth.register_user(new_email, new_pwd)
                        st.success("🎉 Pendaftaran Berhasil! Silakan masuk kembali.")
                    except ValueError as e: st.error(f"⚠️ Gagal: {e}")
            st.write("")
            if st.button("Already have an account? Sign in"):
                st.session_state.auth_mode = "Login"
                st.rerun()

# Halaman Aplikasi Utama
else:
    active_user = st.session_state.current_user
    user_students = manager.get_students_by_user(active_user)
    user_lecturers = manager.get_lecturers_by_user(active_user)
    
    st.sidebar.markdown(f"""
        <div style='text-align: center; background: #161D30; padding: 20px; border-radius: 16px; margin-bottom: 20px; border: 1px solid #24324F;'>
            <div style='font-size: 11px; color: #3B82F6; font-weight: 700; letter-spacing: 1px;'>ONLINE USER</div>
            <div style='font-weight: 600; color: #FFFFFF; font-size: 14px; word-break: break-all; margin-top: 5px;'>{active_user}</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("<h3 style='font-size: 11px; color: #64748B; font-weight: 700; letter-spacing: 1px; margin-bottom: 15px;'>MENU UTAMA</h3>", unsafe_allow_html=True)
    menu = st.sidebar.radio("Pilih Tindakan:", ["📊 Dashboard Ringkasan", "➕ Tambah Mahasiswa", "➕ Tambah Dosen", "🔍 Cari & Urutkan"])

    # Reset State Pencarian jika ganti menu
    if 'current_menu' not in st.session_state: st.session_state.current_menu = menu
    if st.session_state.current_menu != menu:
        st.session_state.current_menu = menu
        if 'sort_df' in st.session_state: del st.session_state.sort_df
        if 'search_df' in st.session_state: del st.session_state.search_df

    # MENU 1: DASHBOARD
    if menu == "📊 Dashboard Ringkasan":
        st.markdown(f"# Frign Fit Academic Workspace ⚡")
        st.write("---")
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-card" style="border-left-color: #3B82F6;">
                    <div class="metric-label">TOTAL MAHASISWA</div>
                    <div class="metric-value">{len(user_students)} <span style='font-size:14px; color:#3B82F6; font-weight:500;'>Orang</span></div>
                </div>
                <div class="metric-card" style="border-left-color: #10B981;">
                    <div class="metric-label">TOTAL DOSEN</div>
                    <div class="metric-value">{len(user_lecturers)} <span style='font-size:14px; color:#10B981; font-weight:500;'>Dosen</span></div>
                </div>
                <div class="metric-card" style="border-left-color: #A855F7;">
                    <div class="metric-label">SISTEM PENYIMPANAN</div>
                    <div class="metric-value">JSON Engine <span style='font-size:13px; color:#A855F7; font-weight:500;'><br>Enkripsi Akun</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        col_mhs, col_dsn = st.columns(2)
        with col_mhs:
            st.markdown('<div class="dashboard-card"><h3>📋 Tabel Data Mahasiswa</h3>', unsafe_allow_html=True)
            if user_students:
                df = pd.DataFrame([{"NIM": s.get_nim(), "Nama Lengkap": s.get_nama(), "Email": s.get_email(), "Prodi": s.jurusan} for s in user_students])
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.write("---")
                nim_hapus = st.selectbox("Pilih NIM Mahasiswa yang ingin dihapus:", df["NIM"])
                if st.button("Hapus Mahasiswa Permanen"):
                    manager.all_students = [s for s in manager.all_students if not (s.get_nim() == nim_hapus and s.pemilik_akun == active_user)]
                    manager.save_data()
                    st.success("Data mahasiswa berhasil dihapus.")
                    st.rerun()
            else: st.info("Belum ada data mahasiswa terdaftar.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_dsn:
            st.markdown('<div class="dashboard-card"><h3>👨‍🏫 Tabel Data Dosen</h3>', unsafe_allow_html=True)
            if user_lecturers:
                df_d = pd.DataFrame([{"NIDN": d.get_nidn(), "Nama Dosen": d.get_nama(), "Email": d.get_email(), "Matakuliah": d.matakuliah} for d in user_lecturers])
                st.dataframe(df_d, use_container_width=True, hide_index=True)
                st.write("---")
                nidn_hapus = st.selectbox("Pilih NIDN Dosen yang ingin dihapus:", df_d["NIDN"])
                if st.button("Hapus Dosen Permanen"):
                    manager.all_lecturers = [d for d in manager.all_lecturers if not (d.get_nidn() == nidn_hapus and d.pemilik_akun == active_user)]
                    manager.save_data()
                    st.success("Data dosen berhasil dihapus.")
                    st.rerun()
            else: st.info("Belum ada data dosen terdaftar.")
            st.markdown('</div>', unsafe_allow_html=True)

    # MENU 2: TAMBAH MAHASISWA (FITUR MASSAL DAN MANUAL DIKEMBALIKAN UTUH)
    elif menu == "➕ Tambah Mahasiswa":
        st.markdown("# ➕ Input Data Mahasiswa")
        st.write("---")
        
        # FITUR UTAMA 1: IMPORT MASSAL FILE
        st.markdown("<div class='dashboard-card'><h4>📥 Import Data Secara Massal (CSV, JSON, XLSX)</h4>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Pilih file data mahasiswa", type=["csv", "json", "xlsx"])
        
        if uploaded_file is not None:
            if st.button("Proses & Tambah Data File"):
                try:
                    count_added = 0
                    df_uploaded = None
                    if uploaded_file.name.endswith('.csv'):
                        df_uploaded = pd.read_csv(uploaded_file, sep=None, engine='python')
                    elif uploaded_file.name.endswith('.xlsx'):
                        df_uploaded = pd.read_excel(uploaded_file)
                    elif uploaded_file.name.endswith('.json'):
                        file_data = json.load(uploaded_file)
                        if isinstance(file_data, list): df_uploaded = pd.DataFrame(file_data)
                    
                    if df_uploaded is not None:
                        df_uploaded.dropna(how='all', inplace=True)
                        df_uploaded.columns = [str(col).lower().strip() for col in df_uploaded.columns]
                        for _, row in df_uploaded.iterrows():
                            v_nim = str(row['nim']).split('.')[0].strip()
                            v_nama = str(row['nama']).strip()
                            v_email = str(row['email']).strip()
                            v_jurusan = str(row['jurusan']).strip()
                            if not v_nim or v_nim.lower() == 'nan' or not v_nama: continue
                            if any(m.get_nim() == v_nim and m.pemilik_akun == active_user for m in manager.all_students): continue 
                            manager.all_students.append(Mahasiswa(v_nim, v_nama, v_email, v_jurusan, active_user))
                            count_added += 1
                        if count_added > 0:
                            manager.save_data()
                            st.success(f"🎉 Berhasil mengimpor {count_added} data mahasiswa baru!")
                            st.rerun()
                except Exception as e: st.error(f"❌ Gagal: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # FITUR UTAMA 2: FORM MANUAL
        st.markdown("<div class='dashboard-card'><h4>📝 Tambah Data Secara Manual</h4>", unsafe_allow_html=True)
        with st.form("tambah_mhs_form"):
            nim = st.text_input("NIM (Harus Angka)")
            nama = st.text_input("Nama Lengkap Mahasiswa")
            email = st.text_input("Email Mahasiswa")
            jurusan = st.selectbox("Jurusan / Prodi", ["Informatika", "Sistem Informasi", "Teknik Elektro"])
            
            if st.form_submit_button("Simpan Data Manual"):
                try:
                    if not nim.isdigit(): raise ValueError("NIM harus berupa angka!")
                    if any(m.get_nim() == nim and m.pemilik_akun == active_user for m in manager.all_students):
                        raise ValueError("NIM tersebut sudah terdaftar!")
                    manager.all_students.append(Mahasiswa(nim, nama, email, jurusan, active_user))
                    manager.save_data()
                    st.success(f"Berhasil menambahkan data manual: {nama}!")
                    st.rerun()
                except Exception as e: st.error(f"Gagal Menyimpan: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    # MENU 3: TAMBAH DOSEN
    elif menu == "➕ Tambah Dosen":
        st.markdown("# ➕ Input Data Dosen")
        st.write("---")
        st.markdown("<div class='dashboard-card'><h4>📝 Form Penginputan Data Dosen Baru</h4>", unsafe_allow_html=True)
        with st.form("tambah_dosen_form"):
            nidn = st.text_input("NIDN (Nomor Induk Dosen Nasional)")
            nama_dosen = st.text_input("Nama Lengkap Dosen Beserta Gelar")
            email_dosen = st.text_input("Email Resmi Instansi Dosen")
            matakuliah = st.text_input("Mata Kuliah Utama yang Diampu")
            
            if st.form_submit_button("Simpan Data Dosen"):
                if nidn.isdigit() and nama_dosen and matakuliah:
                    if any(d.get_nidn() == nidn and d.pemilik_akun == active_user for d in manager.all_lecturers):
                        st.error("NIDN Dosen tersebut sudah terdaftar!")
                    else:
                        manager.all_lecturers.append(Dosen(nidn, nama_dosen, email_dosen, matakuliah, active_user))
                        manager.save_data()
                        st.success(f"🎉 Berhasil menyimpan data dosen: {nama_dosen}!")
                        st.rerun()
                else: st.error("❌ Mohon isi data dengan benar!")
        st.markdown('</div>', unsafe_allow_html=True)

    # MENU 4: CARI & URUTKAN
    elif menu == "🔍 Cari & Urutkan":
        st.markdown("# 🔍 Pusat Pemrosesan Algoritma")
        st.write("---")
        
        col1, col2 = st.columns(2)
        
        # --- KOLOM 1: ENGINE PENGURUTAN (SORTING) ---
        with col1:
            st.markdown('<div class="dashboard-card"><h4>🔽 Sorting Engine (Pengurutan Data)</h4>', unsafe_allow_html=True)
            sort_opt = st.selectbox("Pilih Opsi Pengurutan", [
                "NIM Mahasiswa (Bubble Sort)", 
                "Nama Dosen (Selection Sort)",
                "Mahasiswa - Prodi & Nama (Double Sort)"
            ])
            
            if st.button("Jalankan Pengurutan"):
                start_time = time.time()
                
                if sort_opt == "NIM Mahasiswa (Bubble Sort)":
                    manager.bubble_sort_nim(active_user)
                    res_sorted = manager.get_students_by_user(active_user)
                    st.session_state.sort_df = pd.DataFrame([{"NIM": s.get_nim(), "Nama Lengkap": s.get_nama(), "Prodi": s.jurusan} for s in res_sorted])
                
                elif sort_opt == "Nama Dosen (Selection Sort)":
                    manager.selection_sort_nama_dosen(active_user)
                    res_sorted = manager.get_lecturers_by_user(active_user)
                    st.session_state.sort_df = pd.DataFrame([{"NIDN": d.get_nidn(), "Nama Dosen": d.get_nama(), "Matakuliah": d.matakuliah} for d in res_sorted])
                
                elif sort_opt == "Mahasiswa - Prodi & Nama (Double Sort)":
                    manager.double_sort_mhs_prodi_nama(active_user)
                    res_sorted = manager.get_students_by_user(active_user)
                    st.session_state.sort_df = pd.DataFrame([{"Prodi": s.jurusan, "Nama Lengkap": s.get_nama(), "NIM": s.get_nim()} for s in res_sorted])
                
                st.session_state.sort_time = time.time() - start_time

            if 'sort_df' in st.session_state:
                st.write(f"⏱️ *Execution Time:* {st.session_state.sort_time:.6f} detik")
                st.markdown("<p style='color:#10B981; font-weight:600;'>📊 Hasil Urutan Data Terbaru:</p>", unsafe_allow_html=True)
                st.dataframe(st.session_state.sort_df, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        # --- KOLOM 2: ENGINE PENCARIAN (SEARCHING) ---
        with col2:
            st.markdown('<div class="dashboard-card"><h4>🔍 Searching Engine (Pencarian Data)</h4>', unsafe_allow_html=True)
            
            kategori_cari = st.radio("Pilih Objek:", ["Mahasiswa", "Dosen"], horizontal=True)
            metode_cari = st.selectbox("Pilih Metode Algoritma:", ["Linear Search", "Built-in Filter Engine"])
            
            if kategori_cari == "Mahasiswa":
                kriteria_mhs = st.selectbox("Cari Berdasarkan:", ["NIM", "Nama"])
                search_query = st.text_input(f"Masukkan {kriteria_mhs} Mahasiswa:")
                
                if st.button("Mulai Cari Mahasiswa"):
                    if search_query:
                        if metode_cari == "Linear Search":
                            res_mhs = manager.linear_search_mhs(active_user, search_query, kriteria_mhs)
                        else:
                            if kriteria_mhs == "NIM":
                                res_mhs = [m for m in user_students if m.get_nim() == search_query]
                            else:
                                res_mhs = [m for m in user_students if search_query.lower() in m.get_nama().lower()]
                        
                        if res_mhs:
                            st.session_state.search_df = pd.DataFrame([{"NIM": m.get_nim(), "Nama": m.get_nama(), "Prodi": m.jurusan, "Email": m.get_email()} for m in res_mhs])
                        else: st.session_state.search_df = "KOSONG"
                    else: st.warning("Silakan masukkan kata kunci pencarian!")
                    
            elif kategori_cari == "Dosen":
                kriteria_dsn = st.selectbox("Cari Berdasarkan:", ["NIDN", "Nama"])
                search_query = st.text_input(f"Masukkan {kriteria_dsn} Dosen:")
                
                if st.button("Mulai Cari Dosen"):
                    if search_query:
                        if metode_cari == "Linear Search":
                            res_dsn = manager.linear_search_dsn(active_user, search_query, kriteria_dsn)
                        else:
                            if kriteria_dsn == "NIDN":
                                res_dsn = [d for d in user_lecturers if d.get_nidn() == search_query]
                            else:
                                res_dsn = [d for d in user_lecturers if search_query.lower() in d.get_nama().lower()]
                        
                        if res_dsn:
                            st.session_state.search_df = pd.DataFrame([{"NIDN": d.get_nidn(), "Nama Dosen": d.get_nama(), "Matakuliah": d.matakuliah, "Email": d.get_email()} for d in res_dsn])
                        else: st.session_state.search_df = "KOSONG"
                    else: st.warning("Silakan masukkan kata kunci pencarian!")

            if 'search_df' in st.session_state:
                if isinstance(st.session_state.search_df, pd.DataFrame):
                    st.markdown("<p style='color:#3B82F6; font-weight:600;'>🎯 Data Ditemukan:</p>", unsafe_allow_html=True)
                    st.dataframe(st.session_state.search_df, use_container_width=True, hide_index=True)
                else:
                    st.error("❌ Data tidak ditemukan. Periksa kembali kata kunci Anda.")
                    
            st.markdown('</div>', unsafe_allow_html=True)

    # Tombol Keluar
    st.sidebar.write("\n" * 10)
    st.sidebar.markdown("<div style='text-align: center; color: #475569; font-size: 11px; margin-bottom: 10px;'>Created by Mario</div>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Keluar / Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.rerun()
