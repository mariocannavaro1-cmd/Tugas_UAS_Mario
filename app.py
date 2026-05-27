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
    def __init__(self, nim, nama, email, jurusan):
        super().__init__(nama)
        self.__nim = nim          # Private
        self.__email = email      # Private
        self.jurusan = jurusan    # Public

    def get_nim(self): return self.__nim
    def get_email(self): return self.__email
    def get_nama(self): return self._nama
    
    def tampilkan_peran(self):
        return f"Mahasiswa: {self._nama}"

# ==========================================
# 2. MANAGER DATA & SISTEM AUTENTIKASI
# ==========================================

class AuthManager:
    """Mengelola pendaftaran dan login akun menggunakan file JSON"""
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
    """Mengelola CRUD Mahasiswa"""
    def __init__(self):
        self.file_path = "students.json"
        self.load_data()

    def load_data(self):
        try:
            with open(self.file_path, "r") as f:
                self.students = [Mahasiswa(**d) for d in json.load(f)]
        except (FileNotFoundError, json.JSONDecodeError):
            self.students = []

    def save_data(self):
        with open(self.file_path, "w") as f:
            data = [{"nim": m.get_nim(), "nama": m.get_nama(), "email": m.get_email(), "jurusan": m.jurusan} for m in self.students]
            json.dump(data, f, indent=4)

    def bubble_sort_nim(self):
        n = len(self.students)
        for i in range(n):
            for j in range(0, n-i-1):
                if self.students[j].get_nim() > self.students[j+1].get_nim():
                    self.students[j], self.students[j+1] = self.students[j+1], self.students[j]

    def selection_sort_nama(self):
        n = len(self.students)
        for i in range(n):
            min_idx = i
            for j in range(i+1, n):
                if self.students[j].get_nama().lower() < self.students[min_idx].get_nama().lower():
                    min_idx = j
            self.students[i], self.students[min_idx] = self.students[min_idx], self.students[i]

    def binary_search_nim(self, target_nim):
        self.bubble_sort_nim()
        low, high = 0, len(self.students) - 1
        while low <= high:
            mid = (low + high) // 2
            if self.students[mid].get_nim() == target_nim: return self.students[mid]
            elif self.students[mid].get_nim() < target_nim: low = mid + 1
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
    st.sidebar.markdown("<h2 style='color: #1E3A8A;'>🎓 PANEL NAVIGASI</h2>", unsafe_allow_html=True)
    menu = st.sidebar.radio("Pilih Menu Tindakan:", ["📊 Dashboard Utama", "➕ Tambah Mahasiswa", "🔍 Cari & Urutkan"])

    if "Dashboard Utama" in menu:
        st.markdown("# 📊 Dashboard Utama")
        st.write("---")
        
        total_mhs = len(manager.students)
        col1, col2, col3 = st.columns(3)
        with col1: st.metric(label="Total Mahasiswa", value=f"{total_mhs} Orang", delta="Aktif")
        with col2: st.metric(label="Status Autentikasi", value="Secure", delta="Regex Validated")
        with col3: st.metric(label="Database Lokasi", value="JSON System", delta="Connected")
            
        st.write("### 📋 Tabel Data Mahasiswa")
        if manager.students:
            df = pd.DataFrame([{
                "NIM": s.get_nim(),
                "Nama Lengkap": s.get_nama(),
                "Email Kontak": s.get_email(),
                "Program Studi": s.jurusan
            } for s in manager.students])
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("<div class='card-box'><h4>⚠️ Hapus Data Mahasiswa (CRUD - Delete)</h4></div>", unsafe_allow_html=True)
            nim_hapus = st.selectbox("Pilih NIM Mahasiswa yang ingin dihapus:", df["NIM"])
            if st.button("Hapus Permanen"):
                manager.students = [s for s in manager.students if s.get_nim() != nim_hapus]
                manager.save_data()
                st.warning(f"Data mahasiswa dengan NIM {nim_hapus} telah dihapus dari sistem.")
                st.rerun()
        else:
            st.info("Belum ada data mahasiswa dalam database.")

    elif "Tambah Mahasiswa" in menu:
        st.markdown("# ➕ Tambah Data Mahasiswa")
        
        # --- FITUR IMPORT DATA MASSAL (Mendukung CSV, JSON, XLSX) ---
        st.markdown("<div class='card-box'><h4>📥 Import Data Secara Massal (Upload File CSV, JSON, atau XLSX)</h4><p>Pilih file dengan format .csv, .json, atau file Excel asli .xlsx</p></div>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Pilih file data mahasiswa", type=["csv", "json", "xlsx"])
        if uploaded_file is not None:
            if st.button("Proses & Tambah Data File"):
                try:
                    count_added = 0
                    df_uploaded = None
                    
                    # 1. LOGIKA PROSES FILE CSV
                    if uploaded_file.name.endswith('.csv'):
                        try:
                            # Menggunakan sep=None agar otomatis mendeteksi pemisah koma (,) atau titik koma (;) dari Excel
                            df_uploaded = pd.read_csv(uploaded_file, sep=None, engine='python')
                        except Exception as csv_err:
                            raise ValueError(f"File CSV rusak atau strukturnya tidak terbaca. Detail: {csv_err}")
                    
                    # 2. LOGIKA PROSES FILE EXCEL (.xlsx)
                    elif uploaded_file.name.endswith('.xlsx'):
                        try:
                            df_uploaded = pd.read_excel(uploaded_file)
                        except Exception as xlsx_err:
                            raise ValueError(f"Gagal membaca file Excel (.xlsx). Pastikan file tidak corrupt. Detail: {xlsx_err}")
                    
                    # PROSES DATA JIKA BERASAL DARI CSV ATAU EXCEL
                    if df_uploaded is not None:
                        df_uploaded.dropna(how='all', inplace=True) # Bersihkan baris kosong di dasar excel
                        
                        # Ubah judul kolom menjadi huruf kecil semua dan hapus spasi samping
                        df_uploaded.columns = [str(col).lower().strip() for col in df_uploaded.columns]
                        
                        required_cols = ['nim', 'nama', 'email', 'jurusan']
                        
                        # CEK APAKAH ADA KOLOM YANG KURANG
                        missing_cols = [col for col in required_cols if col not in df_uploaded.columns]
                        if missing_cols:
                            raise ValueError(f"Judul kolom tidak lengkap! Kolom yang tidak ditemukan: {', '.join(missing_cols).upper()}. Periksa kembali judul tabel Anda.")
                        
                        for index, row in df_uploaded.iterrows():
                            # Konversi ke string bersih
                            v_nim = str(row['nim']).split('.')[0].strip()
                            v_nama = str(row['nama']).strip()
                            v_email = str(row['email']).strip()
                            v_jurusan = str(row['jurusan']).strip()
                            
                            # Lewati jika baris data kosong
                            if not v_nim or v_nim.lower() == 'nan' or not v_nama or v_nama.lower() == 'nan':
                                continue
                            
                            # KASIH TAHU JIKA ADA NIM YANG SUDAH TERDAFTAR (DUPLIKAT)
                            if any(m.get_nim() == v_nim for m in manager.students):
                                # Kita skip namun beri log peringatan di console atau tetap lanjut proses sisanya
                                continue 
                            
                            new_student = Mahasiswa(v_nim, v_nama, v_email, v_jurusan)
                            manager.students.append(new_student)
                            count_added += 1
                            
                    # 3. LOGIKA PROSES FILE JSON
                    elif uploaded_file.name.endswith('.json'):
                        try:
                            file_data = json.load(uploaded_file)
                        except Exception as json_err:
                            raise ValueError(f"Format penulisan sintaks JSON salah/corrupt. Detail: {json_err}")
                            
                        if not isinstance(file_data, list):
                            raise ValueError("Struktur data file JSON salah! Harus berupa Array/List data (diawali tanda [ dan diakhiri ] ).")
                            
                        for index, item in enumerate(file_data):
                            # Ubah semua key JSON menjadi huruf kecil
                            item_clean = {str(k).lower().strip(): str(v).strip() for k, v in item.items()}
                            
                            required_cols = ['nim', 'nama', 'email', 'jurusan']
                            missing_json_cols = [col for col in required_cols if col not in item_clean]
                            if missing_json_cols:
                                raise ValueError(f"Data JSON pada indeks ke-{index} tidak valid. Kunci data berikut hilang: {', '.join(missing_json_cols).upper()}")
                            
                            v_nim = item_clean.get('nim', '').split('.')[0]
                            v_nama = item_clean.get('nama', '')
                            v_email = item_clean.get('email', '')
                            v_jurusan = item_clean.get('jurusan', '')
                            
                            if not v_nim or v_nim.lower() == 'nan' or not v_nama or v_nama.lower() == 'nan':
                                continue
                            if any(m.get_nim() == v_nim for m in manager.students):
                                continue
                                
                            new_student = Mahasiswa(v_nim, v_nama, v_email, v_jurusan)
                            manager.students.append(new_student)
                            count_added += 1
                    
                    # VALIDASI KELUARAN AKHIR SISTEM
                    if count_added > 0:
                        manager.save_data()
                        st.success(f"🎉 Berhasil! Sebanyak {count_added} data mahasiswa baru dari file telah ditambahkan ke database.")
                        st.rerun()
                    else:
                        st.warning("⚠️ Tidak ada data baru yang masuk. Kemungkinan semua NIM di dalam file sudah terdaftar di sistem (Data Duplikat).")
                        
                except Exception as e:
                    # MENAMPILKAN PESAN SEBAB KEGAGALAN SECARA SPESIFIK KEPADA USER
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
                    if any(m.get_nim() == nim for m in manager.students):
                        raise ValueError("NIM tersebut sudah terdaftar di sistem!")
                    
                    new_student = Mahasiswa(nim, nama, email, jurusan)
                    manager.students.append(new_student)
                    manager.save_data()
                    st.success(f"Berhasil menambahkan data: {nama}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal Menyimpan: {e}")

    elif "Cari & Urutkan" in menu:
        st.markdown("# 🔍 Fitur Algoritma Searching & Sorting")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### 🔽 Sorting Data")
            sort_opt = st.selectbox("Metode Pengurutan", ["NIM (Bubble Sort)", "Nama (Selection Sort)"])
            if st.button("Jalankan Sorting"):
                start_time = time.time()
                if "NIM" in sort_opt: manager.bubble_sort_nim()
                else: manager.selection_sort_nama()
                manager.save_data()
                st.write(f"⏱️ *Time Complexity Execution:* {time.time() - start_time:.6f} detik")
                st.success("Tabel berhasil diurutkan! Silakan cek hasilnya di Dashboard.")

        with col2:
            st.write("### 🔍 Searching Data")
            search_nim = st.text_input("Masukkan NIM yang dicari:")
            if st.button("Cari (Binary Search)"):
                res = manager.binary_search_nim(search_nim)
                if res:
                    st.success(f"✨ **Data Ditemukan!**\n\n**Nama:** {res.get_nama()}\n\n**Prodi:** {res.jurusan}\n\n**Email:** {res.get_email()}")
                else:
                    st.error("❌ Data mahasiswa tidak ditemukan.")

    st.sidebar.write("---")
    if st.sidebar.button("🚪 Keluar / Logout"):
        st.session_state.logged_in = False
        st.rerun()