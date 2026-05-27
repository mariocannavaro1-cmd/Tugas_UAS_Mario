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
    # Diberi default pemilik_akun="" agar data lama yang tidak punya kolom ini tidak bikin crash
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

# ==========================================
# 2. MANAGER DATA & SISTEM AUTENTIKASI
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


class StudentManager:
    def __init__(self):
        self.file_path = "students.json"
        self.all_students = []
        self.load_data()

    def load_data(self):
        try:
            with open(self.file_path, "r") as f:
                # Menggunakan baris aman agar file lama/baru sama-sama bisa terbaca tanpa crash
                raw_data = json.load(f)
                self.all_students = []
                for d in raw_data:
                    # Ambil data lama, jika pemilik_akun kosong beri default teks kosong
                    self.all_students.append(Mahasiswa(
                        nim=d.get('nim', ''),
                        nama=d.get('nama', ''),
                        email=d.get('email', ''),
                        jurusan=d.get('jurusan', ''),
                        pemilik_akun=d.get('pemilik_akun', '')
                    ))
        except (FileNotFoundError, json.JSONDecodeError):
            self.all_students = []

    def get_students_by_user(self, email_user):
        return [m for m in self.all_students if m.pemilik_akun == email_user]

    def save_data(self):
        with open(self.file_path, "w") as f:
            data = [{
                "nim": m.get_nim(), 
                "nama": m.get_nama(), 
                "email": m.get_email(), 
                "jurusan": m.jurusan,
                "pemilik_akun": m.pemilik_akun
            } for m in self.all_students]
            json.dump(data, f, indent=4)

    def bubble_sort_nim(self, email_user):
        user_students = self.get_students_by_user(email_user)
        n = len(user_students)
        for i in range(n):
            for j in range(0, n-i-1):
                if user_students[j].get_nim() > user_students[j+1].get_nim():
                    user_students[j], user_students[j+1] = user_students[j+1], user_students[j]
        self.update_main_list(user_students, email_user)

    def selection_sort_nama(self, email_user):
        user_students = self.get_students_by_user(email_user)
        n = len(user_students)
        for i in range(n):
            min_idx = i
            for j in range(i+1, n):
                if user_students[j].get_nama().lower() < user_students[min_idx].get_nama().lower():
                    min_idx = j
            user_students[i], user_students[min_idx] = user_students[min_idx], user_students[i]
        self.update_main_list(user_students, email_user)

    def update_main_list(self, user_students, email_user):
        self.all_students = [m for m in self.all_students if m.pemilik_akun != email_user]
        self.all_students.extend(user_students)
        self.save_data()

    def binary_search_nim(self, target_nim, email_user):
        user_students = self.get_students_by_user(email_user)
        user_students.sort(key=lambda x: x.get_nim())
        low, high = 0, len(user_students) - 1
        while low <= high:
            mid = (low + high) // 2
            if user_students[mid].get_nim() == target_nim: return user_students[mid]
            elif user_students[mid].get_nim() < target_nim: low = mid + 1
            else: high = mid - 1
        return None

# ==========================================
# 3. INTERFACE / TAMPILAN WEB STREAMLIT
# ==========================================

st.set_page_config(page_title="Sistem Informasi Mahasiswa", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    div.stButton > button:first-child {
        background-color: #1E3A8A; color: white; border-radius: 6px;
        padding: 0.4rem 2rem; font-weight: bold; border: none; transition: all 0.2s;
    }
    div.stButton > button:first-child:hover { background-color: #111827; transform: translateY(-1px); }
    .card-box {
        padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        background-color: #F3F4F6; margin-bottom: 20px; border-left: 5px solid #1E3A8A;
    }
    </style>
    """, unsafe_allow_html=True)

auth = AuthManager()
manager = StudentManager()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = "Login"
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

if not st.session_state.logged_in:
    _, col_center, _ = st.columns([1, 1.5, 1])
    
    with col_center:
        if st.session_state.auth_mode == "Login":
            st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🔑 LOGIN SISTEM</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #6B7280;'>Silakan masuk menggunakan akun Gmail terdaftar</p>", unsafe_allow_html=True)
            
            with st.form("login_form"):
                email_input = st.text_input("Email Gmail")
                pwd_input = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Masuk")
                
                if submit_login:
                    if auth.login_user(email_input, pwd_input):
                        st.session_state.logged_in = True
                        st.session_state.current_user = email_input
                        st.success("🎯 Login Berhasil!")
                        st.rerun()
                    else:
                        st.error("❌ Email atau Password salah! Silakan coba lagi.")
            
            if st.button("Belum punya akun? Daftar di sini"):
                st.session_state.auth_mode = "Daftar"
                st.rerun()
                
        elif st.session_state.auth_mode == "Daftar":
            st.markdown("<h2 style='text-align: center; color: #10B981;'>📝 DAFTAR AKUN BARU</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #6B7280;'>Gunakan email @gmail.com aktif untuk mendaftar</p>", unsafe_allow_html=True)
            
            with st.form("register_form"):
                new_email = st.text_input("Masukkan Email Gmail")
                new_pwd = st.text_input("Masukkan Password (Min. 6 Karakter)", type="password")
                submit_register = st.form_submit_button("Daftar Sekarang")
                
                if submit_register:
                    try:
                        auth.register_user(new_email, new_pwd)
                        st.success("🎉 Pendaftaran Berhasil! Silakan kembali ke menu login.")
                    except ValueError as e:
                        st.error(f"⚠️ Gagal: {e}")
            
            if st.button("Sudah punya akun? Login di sini"):
                st.session_state.auth_mode = "Login"
                st.rerun()

else:
    active_user = st.session_state.current_user
    user_students = manager.get_students_by_user(active_user)
    
    st.sidebar.markdown(f"<div style='background-color:#E0E7FF; padding:10px; border-radius:5px; margin-bottom:10px; color:#1E3A8A;'>👤 <b>Login sebagai:</b><br>{active_user}</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<h2 style='color: #1E3A8A;'>🎓 PANEL NAVIGASI</h2>", unsafe_allow_html=True)
    menu = st.sidebar.radio("Pilih Menu Tindakan:", ["📊 Dashboard Utama", "➕ Tambah Mahasiswa", "🔍 Cari & Urutkan"])

    if "Dashboard Utama" in menu:
        st.markdown(f"# 📊 Dashboard Utama ({active_user})")
        st.write("---")
        
        total_mhs = len(user_students)
        col1, col2, col3 = st.columns(3)
        with col1: st.metric(label="Data Mahasiswa Anda", value=f"{total_mhs} Orang", delta="Milik Akun Ini")
        with col2: st.metric(label="Status Autentikasi", value="Isolasi Data", delta="Aman & Terpisah")
        with col3: st.metric(label="Database Lokasi", value="JSON System", delta="Connected")
            
        st.write("### 📋 Tabel Data Mahasiswa Anda")
        if user_students:
            df = pd.DataFrame([{
                "NIM": s.get_nim(),
                "Nama Lengkap": s.get_nama(),
                "Email Kontak": s.get_email(),
                "Program Studi": s.jurusan
            } for s in user_students])
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("<div class='card-box'><h4>⚠️ Hapus Data Mahasiswa (CRUD - Delete)</h4></div>", unsafe_allow_html=True)
            nim_hapus = st.selectbox("Pilih NIM Mahasiswa yang ingin dihapus:", df["NIM"])
            if st.button("Hapus Permanen"):
                manager.all_students = [s for s in manager.all_students if not (s.get_nim() == nim_hapus and s.pemilik_akun == active_user)]
                manager.save_data()
                st.warning(f"Data mahasiswa dengan NIM {nim_hapus} telah dihapus dari akun Anda.")
                st.rerun()
        else:
            st.info("Akun Anda belum memiliki data mahasiswa. Silakan tambahkan lewat menu 'Tambah Mahasiswa'.")

    elif "Tambah Mahasiswa" in menu:
        st.markdown("# ➕ Tambah Data Mahasiswa")
        
        st.markdown("<div class='card-box'><h4>📥 Import Data Secara Massal (CSV, JSON, XLSX)</h4><p>Data yang di-upload otomatis dikunci dan hanya bisa dilihat oleh akun Anda.</p></div>", unsafe_allow_html=True)
        
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
                    
                    if df_uploaded is not None:
                        df_uploaded.dropna(how='all', inplace=True)
                        df_uploaded.columns = [str(col).lower().strip() for col in df_uploaded.columns]
                        
                        required_cols = ['nim', 'nama', 'email', 'jurusan']
                        missing_cols = [col for col in required_cols if col not in df_uploaded.columns]
                        if missing_cols:
                            raise ValueError(f"Kolom tidak lengkap! Kolom hilang: {', '.join(missing_cols).upper()}")
                        
                        for _, row in df_uploaded.iterrows():
                            v_nim = str(row['nim']).split('.')[0].strip()
                            v_nama = str(row['nama']).strip()
                            v_email = str(row['email']).strip()
                            v_jurusan = str(row['jurusan']).strip()
                            
                            if not v_nim or v_nim.lower() == 'nan' or not v_nama or v_nama.lower() == 'nan':
                                continue
                            if any(m.get_nim() == v_nim and m.pemilik_akun == active_user for m in manager.all_students):
                                continue 
                            
                            new_student = Mahasiswa(v_nim, v_nama, v_email, v_jurusan, active_user)
                            manager.all_students.append(new_student)
                            count_added += 1
                            
                    elif uploaded_file.name.endswith('.json'):
                        file_data = json.load(uploaded_file)
                        if not isinstance(file_data, list):
                            raise ValueError("Format JSON harus berupa Array/List data!")
                            
                        for index, item in enumerate(file_data):
                            item_clean = {str(k).lower().strip(): str(v).strip() for k, v in item.items()}
                            v_nim = item_clean.get('nim', '').split('.')[0]
                            v_nama = item_clean.get('nama', '')
                            v_email = item_clean.get('email', '')
                            v_jurusan = item_clean.get('jurusan', '')
                            
                            if not v_nim or not v_nama: continue
                            if any(m.get_nim() == v_nim and m.pemilik_akun == active_user for m in manager.all_students):
                                continue
                                
                            new_student = Mahasiswa(v_nim, v_nama, v_email, v_jurusan, active_user)
                            manager.all_students.append(new_student)
                            count_added += 1
                    
                    if count_added > 0:
                        manager.save_data()
                        st.success(f"🎉 Berhasil mengimpor {count_added} data mahasiswa baru ke akun Anda!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Tidak ada data baru yang masuk (Mungkin NIM sudah terdaftar di akun ini).")
                except Exception as e:
                    st.error(f"❌ Gagal memproses file! Penyebab: {e}")
                    
        st.write("---")
        st.write("### 📝 Tambah Data Secara Manual")
        with st.form("tambah_mhs_form"):
            nim = st.text_input("NIM (Harus Angka)")
            nama = st.text_input("Nama Lengkap Mahasiswa")
            email = st.text_input("Email Mahasiswa")
            jurusan = st.selectbox("Jurusan / Prodi", ["Informatika", "Sistem Informasi", "Teknik Elektro"])
            
            if st.form_submit_button("Simpan Data Manual"):
                try:
                    if not nim.isdigit(): raise ValueError("NIM harus berupa angka!")
                    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email): 
                        raise ValueError("Format email mahasiswa tidak valid!")
                    if any(m.get_nim() == nim and m.pemilik_akun == active_user for m in manager.all_students):
                        raise ValueError("NIM tersebut sudah terdaftar di akun Anda!")
                    
                    new_student = Mahasiswa(nim, nama, email, jurusan, active_user)
                    manager.all_students.append(new_student)
                    manager.save_data()
                    st.success(f"Berhasil menambahkan data: {nama}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal Menyimpan: {e}")

    elif "Cari & Urutkan" in menu:
        st.markdown("# 🔍 Fitur Algoritma Searching & Sorting (Data Anda)")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### 🔽 Sorting Data")
            sort_opt = st.selectbox("Metode Pengurutan", ["NIM (Bubble Sort)", "Nama (Selection Sort)"])
            if st.button("Jalankan Sorting"):
                start_time = time.time()
                if "NIM" in sort_opt: manager.bubble_sort_nim(active_user)
                else: manager.selection_sort_nama(active_user)
                st.write(f"⏱️ *Time Complexity Execution:* {time.time() - start_time:.6f} detik")
                st.success("Data Anda berhasil diurutkan! Silakan cek hasilnya di Dashboard.")

        with col2:
            st.write("### 🔍 Searching Data")
            search_nim = st.text_input("Masukkan NIM yang dicari:")
            if st.button("Cari (Binary Search)"):
                res = manager.binary_search_nim(search_nim, active_user)
                if res:
                    st.success(f"✨ **Data Ditemukan!**\n\n**Nama:** {res.get_nama()}\n\n**Prodi:** {res.jurusan}\n\n**Email:** {res.get_email()}")
                else:
                    st.error("❌ Data tidak ditemukan di dalam daftar akun Anda.")

    st.sidebar.write("---")
    if st.sidebar.button("🚪 Keluar / Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.rerun()
