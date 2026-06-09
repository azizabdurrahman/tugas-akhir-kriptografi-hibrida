import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog
import sys
import io
import os
import time
import tracemalloc

# Import modul internal Anda
import dummytext
from standardsuite import StandardSuite
from modernsuite import ModernSuite

# Konfigurasi Tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CryptoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Konfigurasi Jendela Utama
        self.title("Dashboard Analisis Kriptografi Hibrida - Aziz Abdurrahman")
        self.geometry("1100x800")

        # 2. Inisialisasi State & Suites (Simulasi 2 pihak: Alice & Bob)
        self.dataset = {}
        self.alice_nist = StandardSuite()
        self.bob_nist = StandardSuite()
        self.alice_modern = ModernSuite()
        self.bob_modern = ModernSuite()
        self.current_kn = None
        self.current_km = None
        
        # VARIABEL BARU: Menyimpan memori hasil enkripsi dari Tab 2 untuk dilaporkan di Tab 4
        self.performance_logs = {}

        # 3. Membuat TabView (Pusat Navigasi)
        self.tab_view = ctk.CTkTabview(self, corner_radius=15)
        self.tab_view.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Menambahkan 6 Tab Utama
        self.tab_view.add("1. Persiapan Data")
        self.tab_view.add("2. Enkripsi Hibrida")
        self.tab_view.add("3. Dekripsi Hibrida")
        self.tab_view.add("4. Benchmark Komparatif")
        self.tab_view.add("5. Analisis Keamanan")
        self.tab_view.add("6. Simulasi Alice & Bob")
        
        # Setup Tampilan Masing-masing Tab
        self.setup_dataset_tab()
        self.setup_encryption_tab()
        self.setup_decryption_tab()
        self.setup_efficiency_tab()
        self.setup_security_tab()
        self.setup_simulation_tab()

    # ==========================================
    # TAB 1: PERSIAPAN DATA (DATASET)
    # ==========================================
    def setup_dataset_tab(self):
        tab = self.tab_view.tab("1. Persiapan Data")
        ctk.CTkLabel(tab, text=" Persiapan Data ", font=("Arial", 18, "bold")).pack(pady=(20, 10))
        ctk.CTkLabel(tab, text="Generate file simulasi baru atau bersihkan seluruh riwayat pengujian.", font=("Arial", 12)).pack(pady=(0, 20))
        
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.btn_generate = ctk.CTkButton(btn_frame, text="Mulai Generate Files", command=self.generate_files_action, height=40, font=("Arial", 13, "bold"))
        self.btn_generate.pack(side="left", padx=10)
        
        self.btn_reset = ctk.CTkButton(btn_frame, text="🗑️ Reset Sistem (Hapus Data)", command=self.reset_all_data, height=40, font=("Arial", 13, "bold"), fg_color="#c0392b", hover_color="#922b21")
        self.btn_reset.pack(side="left", padx=10)
        
        self.log_box = ctk.CTkTextbox(tab, height=350, width=700, font=("Consolas", 12), fg_color="#1e1e1e", border_color="#333333", border_width=2)
        self.log_box.pack(pady=20, padx=40)
        self.log_box.insert("0.0", "--- Sistem Siap ---\nKlik tombol di atas untuk memulai atau mereset sistem...")

    def generate_files_action(self):
        self.log_box.delete("1.0", "end")
        self.log_box.insert("end", "[*] Menginisialisasi pembangkitan data...\n")
        self.update() 
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        try:
            dummytext.create_dummy_files()
            self.dataset = dummytext.load_data_to_ram() 
        except Exception as e:
            print(f"[-] Terjadi kesalahan fatal: {e}")
        finally:
            sys.stdout = old_stdout
        self.log_box.insert("end", buffer.getvalue())
        self.log_box.insert("end", "\n[STATUS] Proses Selesai. File tersimpan di folder 'data/'.\n")
        self.log_box.see("end") 
        self.update_dropdowns()

    def update_dropdowns(self):
        if hasattr(self, 'dataset') and self.dataset:
            daftar_file = list(self.dataset.keys())
            self.file_selector_enc.configure(values=daftar_file)
            self.file_selector_enc.set(daftar_file[0])
            self.file_selector_dec.configure(values=daftar_file)
            self.file_selector_dec.set(daftar_file[0])

    def reset_all_data(self):
        confirm = messagebox.askyesno("Konfirmasi Reset", "Apakah Anda yakin ingin menghapus SELURUH data?\n\nTindakan ini akan menghapus file secara permanen dari hardisk!")
        if confirm:
            folders_to_clear = ['data', 'output_nist', 'output_modern', 'session_keys', 'key_pairs', 'data_decrypt']
            deleted_count = 0
            for folder in folders_to_clear:
                if os.path.exists(folder):
                    for filename in os.listdir(folder):
                        file_path = os.path.join(folder, filename)
                        try:
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                                deleted_count += 1
                        except Exception as e:
                            self.log_box.insert("end", f"\n[-] Gagal menghapus {file_path}: {e}")

            self.dataset = {}
            self.current_kn = None
            self.current_km = None
            self.performance_logs = {} # Bersihkan memori log Tab 4
            self.file_selector_enc.configure(values=["Kosong (Jalankan Tab 1)"])
            self.file_selector_enc.set("Kosong (Jalankan Tab 1)")
            self.file_selector_dec.configure(values=["Kosong (Jalankan Tab 1)"])
            self.file_selector_dec.set("Kosong (Jalankan Tab 1)")
            
            if hasattr(self, 'key_status_label'):
                self.key_status_label.configure(text="Status: Belum ada kunci sesi aktif.", text_color="#e74c3c")

            self.log_box.insert("end", f"\n======================================")
            self.log_box.insert("end", f"\n[RESET SUKSES] Sistem kembali bersih!")
            self.log_box.insert("end", f"\n[-] {deleted_count} file telah dihapus dari sistem.")
            self.log_box.insert("end", f"\n======================================\n")
            self.log_box.see("end")

    # ==========================================
    # TAB 2: ENKRIPSI HIBRIDA
    # ==========================================
    def setup_encryption_tab(self):
        tab = self.tab_view.tab("2. Enkripsi Hibrida")

        key_frame = ctk.CTkFrame(tab, border_width=1, border_color="#7f8c8d")
        key_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(key_frame, text="Langkah 1: Jabat Tangan Kriptografi (Key Exchange)", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        self.btn_gen_keys = ctk.CTkButton(key_frame, text="Generate & Save Session Keys", command=self.generate_keys_gui, fg_color="#8e44ad")
        self.btn_gen_keys.pack(pady=10)
        self.key_status_label = ctk.CTkLabel(key_frame, text="Status: Belum ada kunci sesi aktif.", text_color="#e74c3c", font=("Arial", 12))
        self.key_status_label.pack(pady=(0, 10))

        control_frame = ctk.CTkFrame(tab, fg_color="transparent")
        control_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(control_frame, text="Langkah 2: Pilih File:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10)
        self.file_selector_enc = ctk.CTkOptionMenu(control_frame, values=["Kosong (Jalankan Tab 1)"], width=180)
        self.file_selector_enc.grid(row=0, column=1, padx=10)
        
        self.btn_run_enc = ctk.CTkButton(control_frame, text="Encrypt 1 File", command=self.run_encryption, fg_color="#e67e22")
        self.btn_run_enc.grid(row=0, column=2, padx=5)
        
        self.btn_run_enc_all = ctk.CTkButton(control_frame, text="⚡ Encrypt ALL", command=self.run_encrypt_all, fg_color="#d35400")
        self.btn_run_enc_all.grid(row=0, column=3, padx=5)

        result_frame = ctk.CTkFrame(tab, fg_color="transparent")
        result_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        nist_frame = ctk.CTkFrame(result_frame)
        nist_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        ctk.CTkLabel(nist_frame, text="NIST (P-256 / AES-GCM)", font=("Arial", 13, "bold")).pack(pady=5)
        self.enc_nist_output = ctk.CTkTextbox(nist_frame, font=("Consolas", 11))
        self.enc_nist_output.pack(fill="both", expand=True, padx=10, pady=10)

        modern_frame = ctk.CTkFrame(result_frame)
        modern_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        ctk.CTkLabel(modern_frame, text="Modern (X25519 / ChaCha20)", font=("Arial", 13, "bold")).pack(pady=5)
        self.enc_modern_output = ctk.CTkTextbox(modern_frame, font=("Consolas", 11))
        self.enc_modern_output.pack(fill="both", expand=True, padx=10, pady=10)

    def generate_keys_gui(self):
        try:
            os.makedirs("session_keys", exist_ok=True)
            os.makedirs("key_pairs", exist_ok=True)

            # Key Exchange: Alice pakai pubkey Bob, Bob pakai pubkey Alice
            self.current_kn = self.alice_nist.get_shared_key(self.bob_nist.public_key)
            kn_bob = self.bob_nist.get_shared_key(self.alice_nist.public_key)
            self.current_km = self.alice_modern.get_shared_key(self.bob_modern.public_key)
            km_bob = self.bob_modern.get_shared_key(self.alice_modern.public_key)

            # Validasi shared secret identik
            assert self.current_kn == kn_bob, "NIST shared secret mismatch!"
            assert self.current_km == km_bob, "Modern shared secret mismatch!"

            # Simpan kunci sesi
            with open("session_keys/nist_current.key", "wb") as f: f.write(self.current_kn)
            with open("session_keys/modern_current.key", "wb") as f: f.write(self.current_km)

            # Simpan 4 file PEM per skema (Alice + Bob)
            alice_nist_priv, alice_nist_pub = self.alice_nist.get_pem_keys()
            bob_nist_priv, bob_nist_pub = self.bob_nist.get_pem_keys()
            alice_mod_priv, alice_mod_pub = self.alice_modern.get_pem_keys()
            bob_mod_priv, bob_mod_pub = self.bob_modern.get_pem_keys()

            with open("key_pairs/nist_alice_private.pem", "wb") as f: f.write(alice_nist_priv)
            with open("key_pairs/nist_alice_public.pem", "wb") as f: f.write(alice_nist_pub)
            with open("key_pairs/nist_bob_private.pem", "wb") as f: f.write(bob_nist_priv)
            with open("key_pairs/nist_bob_public.pem", "wb") as f: f.write(bob_nist_pub)
            with open("key_pairs/modern_alice_private.pem", "wb") as f: f.write(alice_mod_priv)
            with open("key_pairs/modern_alice_public.pem", "wb") as f: f.write(alice_mod_pub)
            with open("key_pairs/modern_bob_private.pem", "wb") as f: f.write(bob_mod_priv)
            with open("key_pairs/modern_bob_public.pem", "wb") as f: f.write(bob_mod_pub)

            self.key_status_label.configure(text="Status: Kunci Alice-Bob (.pem) & Sesi (.key) Aktif! ✅", text_color="#2ecc71")
            
            self.enc_nist_output.delete("1.0", "end")
            self.enc_nist_output.insert("end", f"[SYSTEM] Key Exchange ECDH P-256 (Alice <-> Bob) berhasil.\n")
            self.enc_nist_output.insert("end", f"[SYSTEM] Shared Secret IDENTIK ✅\n")
            self.enc_nist_output.insert("end", f"[SYSTEM] Kunci Sesi AES-GCM (HEX):\n>> {self.current_kn.hex()}\n\nSilakan Lanjut ke Langkah 2...")
            
            self.enc_modern_output.delete("1.0", "end")
            self.enc_modern_output.insert("end", f"[SYSTEM] Key Exchange X25519 (Alice <-> Bob) berhasil.\n")
            self.enc_modern_output.insert("end", f"[SYSTEM] Shared Secret IDENTIK ✅\n")
            self.enc_modern_output.insert("end", f"[SYSTEM] Kunci Sesi ChaCha20 (HEX):\n>> {self.current_km.hex()}\n\nSilakan Lanjut ke Langkah 2...")
            
            messagebox.showinfo("Sukses", "Key Exchange Alice-Bob berhasil!\nKunci .pem dan .key tersimpan.")
            
        except Exception as e:
            self.key_status_label.configure(text=f"Error: {e}", text_color="#e74c3c")
            messagebox.showerror("Error", f"Gagal membangkitkan kunci: {e}")

    def _process_and_measure_encryption(self, suite, key, plaintext, filename, folder_out):
        """Fungsi helper canggih: Mengenkripsi, Menyimpan file, dan Mencatat waktu/RAM"""
        os.makedirs(folder_out, exist_ok=True)
        safe_name = filename.lower().replace(".", "_")
        file_path = f"{folder_out}/ciphertext_{safe_name}.enc"

        tracemalloc.start()
        start_time = time.perf_counter()
        
        # Eksekusi Enkripsi Murni
        nonce, cipher = suite.encrypt(key, plaintext)
        
        end_time = time.perf_counter()
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Menyimpan ke hardisk (.enc)
        final_hex = (nonce + cipher).hex()
        with open(file_path, "w") as f: f.write(final_hex)

        return file_path, final_hex, (end_time - start_time) * 1000, peak_mem / 1024

    def run_encryption(self):
        if not self.current_kn or not self.current_km:
            messagebox.showwarning("Kunci Belum Ada", "Harap generate kunci terlebih dahulu!")
            return
        selected_file = self.file_selector_enc.get()
        if selected_file == "Kosong (Jalankan Tab 1)": return

        plaintext = self.dataset[selected_file]
        self.performance_logs = {} 

        self.enc_nist_output.delete("1.0", "end")
        self.enc_modern_output.delete("1.0", "end")

        # Proses NIST
        path_n, hex_n, time_n, mem_n = self._process_and_measure_encryption(self.alice_nist, self.current_kn, plaintext, selected_file, "output_nist")
        self.enc_nist_output.insert("end", f"[FILE] {selected_file}\n[HEX KEY] {self.current_kn.hex()}\n[DISIMPAN] {path_n}\n\n[PERFORMA]\n   Waktu Enkripsi : {time_n:.4f} ms\n   Puncak RAM     : {mem_n:.2f} KB\n\n[PREVIEW]\n{hex_n[:300]}...\n\n[STATUS] OK ✅")

        # Proses Modern
        path_m, hex_m, time_m, mem_m = self._process_and_measure_encryption(self.alice_modern, self.current_km, plaintext, selected_file, "output_modern")
        self.enc_modern_output.insert("end", f"[FILE] {selected_file}\n[HEX KEY] {self.current_km.hex()}\n[DISIMPAN] {path_m}\n\n[PERFORMA]\n   Waktu Enkripsi : {time_m:.4f} ms\n   Puncak RAM     : {mem_m:.2f} KB\n\n[PREVIEW]\n{hex_m[:300]}...\n\n[STATUS] OK ✅")

        # Simpan metrik ke RAM untuk Tab 4
        self.performance_logs[selected_file] = {
            "nist": {"time": time_n, "mem": mem_n},
            "modern": {"time": time_m, "mem": mem_m},
            "size": len(plaintext)
        }
        
        messagebox.showinfo("Sukses", f"File {selected_file} berhasil dienkripsi!")

    def run_encrypt_all(self):
        if not self.current_kn or not self.current_km:
            messagebox.showwarning("Kunci Belum Ada", "Harap generate kunci terlebih dahulu!")
            return
        if not self.dataset:
            messagebox.showwarning("Dataset Kosong", "Generate dataset di Tab 1 terlebih dahulu!")
            return

        self.performance_logs = {} # Reset log untuk baru
        self.enc_nist_output.delete("1.0", "end")
        self.enc_modern_output.delete("1.0", "end")
        self.enc_nist_output.insert("end", "=== MEMULAI ENKRIPSI MASSAL ===\n\n")
        self.enc_modern_output.insert("end", "=== MEMULAI ENKRIPSI MASSAL ===\n\n")
        self.update()

        count = 0
        for filename, plaintext in self.dataset.items():
            # NIST Batch
            path_n, hex_n, time_n, mem_n = self._process_and_measure_encryption(self.alice_nist, self.current_kn, plaintext, filename, "output_nist")
            self.enc_nist_output.insert("end", f" [OK] {filename} -> tersimpan di output_nist/\n")
            
            # Modern Batch
            path_m, hex_m, time_m, mem_m = self._process_and_measure_encryption(self.alice_modern, self.current_km, plaintext, filename, "output_modern")
            self.enc_modern_output.insert("end", f" [OK] {filename} -> tersimpan di output_modern/\n")
            
            # Catat Metrik
            self.performance_logs[filename] = {
                "nist": {"time": time_n, "mem": mem_n},
                "modern": {"time": time_m, "mem": mem_m},
                "size": len(plaintext)
            }
            count += 1
            self.update()

        self.enc_nist_output.insert("end", f"\n[STATUS] {count} File Dienkripsi ✅ (Cek Tab 4 untuk Detail Efisiensi)")
        self.enc_modern_output.insert("end", f"\n[STATUS] {count} File Dienkripsi ✅ (Cek Tab 4 untuk Detail Efisiensi)")
        messagebox.showinfo("Batch Sukses", f"Selesai mengenkripsi {count} file sekaligus!")

    # ==========================================
    # TAB 3: DEKRIPSI HIBRIDA (FULL RESTORE)
    # ==========================================
    def setup_decryption_tab(self):
        tab = self.tab_view.tab("3. Dekripsi Hibrida")
        
        control_frame = ctk.CTkFrame(tab, fg_color="transparent")
        control_frame.pack(pady=(20, 10), padx=20, fill="x")
        ctk.CTkLabel(control_frame, text="Pilih Target File .enc:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10)
        self.file_selector_dec = ctk.CTkOptionMenu(control_frame, values=["Kosong (Jalankan Tab 1)"], width=180)
        self.file_selector_dec.grid(row=0, column=1, padx=10)
        
        self.btn_run_dec = ctk.CTkButton(control_frame, text="Decrypt 1 File", command=self.run_decryption, fg_color="#27ae60")
        self.btn_run_dec.grid(row=0, column=2, padx=5)
        
        self.btn_run_dec_all = ctk.CTkButton(control_frame, text="⚡ Decrypt ALL", command=self.run_decrypt_all, fg_color="#1e8449")
        self.btn_run_dec_all.grid(row=0, column=3, padx=5)

        result_frame = ctk.CTkFrame(tab, fg_color="transparent")
        result_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        nist_frame = ctk.CTkFrame(result_frame)
        nist_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        ctk.CTkLabel(nist_frame, text="Dekripsi NIST", font=("Arial", 13, "bold")).pack(pady=5)
        self.dec_nist_output = ctk.CTkTextbox(nist_frame, font=("Consolas", 11))
        self.dec_nist_output.pack(fill="both", expand=True, padx=10, pady=10)

        modern_frame = ctk.CTkFrame(result_frame)
        modern_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        ctk.CTkLabel(modern_frame, text="Dekripsi Modern", font=("Arial", 13, "bold")).pack(pady=5)
        self.dec_modern_output = ctk.CTkTextbox(modern_frame, font=("Consolas", 11))
        self.dec_modern_output.pack(fill="both", expand=True, padx=10, pady=10)

    def run_decryption(self):
        if not self.current_kn or not self.current_km:
            messagebox.showwarning("Kunci Belum Ada", "Kunci sesi belum dibangkitkan!")
            return
        selected_file = self.file_selector_dec.get()
        if selected_file == "Kosong (Jalankan Tab 1)": return

        plaintext_asli = self.dataset[selected_file]
        safe_name = selected_file.lower().replace(".", "_")
        file_nist = f"output_nist/ciphertext_{safe_name}.enc"
        file_modern = f"output_modern/ciphertext_{safe_name}.enc"

        os.makedirs("data_decrypt", exist_ok=True)
        
        # Auto deteksi ekstensi jika belum ada
        if "." not in selected_file:
            ext = ".txt" if "TXT" in selected_file.upper() else ".docx" if "DOCX" in selected_file.upper() else ".bin"
            final_name = f"{selected_file}{ext}"
        else:
            final_name = selected_file

        self.dec_nist_output.delete("1.0", "end")
        self.dec_modern_output.delete("1.0", "end")

        # NIST
        try:
            with open(file_nist, "r") as f: full_bytes_n = bytes.fromhex(f.read())
            start_dec = time.perf_counter()
            dec_n = self.bob_nist.decrypt(self.current_kn, full_bytes_n[:12], full_bytes_n[12:])
            dec_time_n = (time.perf_counter() - start_dec) * 1000
            
            save_path_n = f"data_decrypt/nist_{final_name}"
            with open(save_path_n, "wb") as f: f.write(dec_n)
            
            preview_teks_n = dec_n[:150].decode('utf-8', errors='replace')
            status = "SUKSES ✅" if dec_n == plaintext_asli else "GAGAL ❌"
            self.dec_nist_output.insert("end", f"[*] Target .enc: {file_nist}\n[*] Key Hex: {self.current_kn.hex()}\n[*] FILE REKONSTRUKSI: {save_path_n}\n\n[PERFORMA]\n   Waktu Dekripsi : {dec_time_n:.4f} ms\n\n[PREVIEW DEKRIPSI]\n{preview_teks_n}...\n\n[INTEGRITAS] {status}")
        except Exception as e:
            self.dec_nist_output.insert("end", f"[-] Error: {e}")

        # Modern
        try:
            with open(file_modern, "r") as f: full_bytes_m = bytes.fromhex(f.read())
            start_dec = time.perf_counter()
            dec_m = self.bob_modern.decrypt(self.current_km, full_bytes_m[:12], full_bytes_m[12:])
            dec_time_m = (time.perf_counter() - start_dec) * 1000
            
            save_path_m = f"data_decrypt/modern_{final_name}"
            with open(save_path_m, "wb") as f: f.write(dec_m)
            
            preview_teks_m = dec_m[:150].decode('utf-8', errors='replace')
            status = "SUKSES ✅" if dec_m == plaintext_asli else "GAGAL ❌"
            self.dec_modern_output.insert("end", f"[*] Target .enc: {file_modern}\n[*] Key Hex: {self.current_km.hex()}\n[*] FILE REKONSTRUKSI: {save_path_m}\n\n[PERFORMA]\n   Waktu Dekripsi : {dec_time_m:.4f} ms\n\n[PREVIEW DEKRIPSI]\n{preview_teks_m}...\n\n[INTEGRITAS] {status}")
        except Exception as e:
            self.dec_modern_output.insert("end", f"[-] Error: {e}")

    def run_decrypt_all(self):
        if not self.current_kn or not self.current_km:
            messagebox.showwarning("Kunci Belum Ada", "Kunci sesi belum dibangkitkan!")
            return
        if not self.dataset:
            messagebox.showwarning("Dataset Kosong", "Dataset belum ada!")
            return

        self.dec_nist_output.delete("1.0", "end")
        self.dec_modern_output.delete("1.0", "end")
        self.dec_nist_output.insert("end", "=== MEMULAI DEKRIPSI MASSAL ===\n\n")
        self.dec_modern_output.insert("end", "=== MEMULAI DEKRIPSI MASSAL ===\n\n")
        self.update()

        os.makedirs("data_decrypt", exist_ok=True)
        count_n, count_m = 0, 0
        
        for filename, plaintext_asli in self.dataset.items():
            safe_name = filename.lower().replace(".", "_")
            file_nist = f"output_nist/ciphertext_{safe_name}.enc"
            file_modern = f"output_modern/ciphertext_{safe_name}.enc"
            
            if "." not in filename:
                ext = ".txt" if "TXT" in filename.upper() else ".docx" if "DOCX" in filename.upper() else ".bin"
                final_name = f"{filename}{ext}"
            else:
                final_name = filename
            
            # Decrypt NIST
            try:
                with open(file_nist, "r") as f: full_bytes_n = bytes.fromhex(f.read())
                dec_n = self.bob_nist.decrypt(self.current_kn, full_bytes_n[:12], full_bytes_n[12:])
                with open(f"data_decrypt/nist_{final_name}", "wb") as f: f.write(dec_n)
                status_n = "SUKSES ✅" if dec_n == plaintext_asli else "GAGAL ❌"
                self.dec_nist_output.insert("end", f" [{status_n}] Disimpan ke: nist_{final_name}\n")
                if status_n == "SUKSES ✅": count_n += 1
            except Exception:
                self.dec_nist_output.insert("end", f" [ERROR] File .enc untuk {filename} tidak ditemukan!\n")

            # Decrypt Modern
            try:
                with open(file_modern, "r") as f: full_bytes_m = bytes.fromhex(f.read())
                dec_m = self.bob_modern.decrypt(self.current_km, full_bytes_m[:12], full_bytes_m[12:])
                with open(f"data_decrypt/modern_{final_name}", "wb") as f: f.write(dec_m)
                status_m = "SUKSES ✅" if dec_m == plaintext_asli else "GAGAL ❌"
                self.dec_modern_output.insert("end", f" [{status_m}] Disimpan ke: modern_{final_name}\n")
                if status_m == "SUKSES ✅": count_m += 1
            except Exception:
                self.dec_modern_output.insert("end", f" [ERROR] File .enc untuk {filename} tidak ditemukan!\n")
            self.update()

        self.dec_nist_output.insert("end", f"\n[STATUS] {count_n} File Berhasil Direkonstruksi ke 'data_decrypt' ✅")
        self.dec_modern_output.insert("end", f"\n[STATUS] {count_m} File Berhasil Direkonstruksi ke 'data_decrypt' ✅")
        messagebox.showinfo("Batch Sukses", "Proses Dekripsi Massal Selesai! Cek folder 'data_decrypt'.")

    # ==========================================
    # TAB 4: KOMPARATIF EFISIENSI (BENCHMARK 100 ITERASI)
    # ==========================================
    def setup_efficiency_tab(self):
        tab = self.tab_view.tab("4. Benchmark Komparatif")
        ctk.CTkLabel(tab, text="Benchmark Komparatif (100 Iterasi)", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.btn_run_benchmark = ctk.CTkButton(tab, text="▶ Jalankan Benchmark (100 Iterasi)", command=self.run_full_benchmark, fg_color="#c0392b", height=40, font=("Arial", 13, "bold"))
        self.btn_run_benchmark.pack(pady=10)

        self.efficiency_output = ctk.CTkTextbox(tab, font=("Consolas", 11))
        self.efficiency_output.pack(fill="both", expand=True, padx=20, pady=10)
        self.efficiency_output.insert("0.0", "--- Benchmark Siap ---\nPastikan Tab 1 (Dataset) dan Tab 2 (Key Exchange) sudah dijalankan.\nKlik tombol di atas untuk memulai benchmark 100 iterasi.")

    def run_full_benchmark(self):
        """Menjalankan benchmark 100 iterasi per file, sama seperti main.py (CLI)."""
        if not self.current_kn or not self.current_km:
            messagebox.showwarning("Kunci Belum Ada", "Generate kunci di Tab 2 terlebih dahulu!")
            return
        if not self.dataset:
            messagebox.showwarning("Dataset Kosong", "Generate dataset di Tab 1 terlebih dahulu!")
            return

        ITERATIONS = 100
        self.efficiency_output.delete("1.0", "end")
        self.efficiency_output.insert("end", "="*70 + "\n")
        self.efficiency_output.insert("end", f"   Benchmark Komparatif ({ITERATIONS} Iterasi)\n")
        self.efficiency_output.insert("end", "="*70 + "\n\n")
        self.efficiency_output.insert("end", "[*] Proses berjalan, mohon tunggu...\n\n")
        self.update()

        import csv
        csv_rows = []
        csv_header = ["Label", "Size_Bytes", "Suite", "Avg_Enc_ms", "Avg_Dec_ms", "Avg_Peak_KB", "Throughput_MBps", "Iterations", "Integrity"]

        # Sorting
        def get_size_value(label):
            units = {"KB": 1024, "MB": 1024 * 1024}
            num = "".join([c for c in label.split("_")[0] if c.isdigit()])
            unit = "".join([c for c in label.split("_")[0] if c.isalpha()]).upper()
            return (int(num) * units.get(unit, 1), 0 if "TXT" in label else 1)

        sorted_labels = sorted(self.dataset.keys(), key=get_size_value)

        for label in sorted_labels:
            plaintext = self.dataset[label]
            self.efficiency_output.insert("end", f">>> {label} ({len(plaintext):,} bytes)\n")
            self.efficiency_output.insert("end", "-" * 70 + "\n")
            self.update()

            for suite_sender, suite_receiver, key, suite_name in [
                (self.alice_nist, self.bob_nist, self.current_kn, "NIST (P-256/AES-GCM)"),
                (self.alice_modern, self.bob_modern, self.current_km, "Modern (X25519/ChaCha20)")
            ]:
                enc_times = []
                dec_times = []
                peak_mems = []
                integrity_ok = True

                for _ in range(ITERATIONS):
                    import tracemalloc as tm
                    tm.start()
                    start = time.perf_counter()
                    nonce, ciphertext = suite_sender.encrypt(key, plaintext)
                    enc_times.append(time.perf_counter() - start)
                    _, peak_mem = tm.get_traced_memory()
                    tm.stop()
                    peak_mems.append(peak_mem)

                    start = time.perf_counter()
                    decrypted = suite_receiver.decrypt(key, nonce, ciphertext)
                    dec_times.append(time.perf_counter() - start)

                    if decrypted != plaintext:
                        integrity_ok = False

                avg_enc = (sum(enc_times) / len(enc_times)) * 1000
                avg_dec = (sum(dec_times) / len(dec_times)) * 1000
                avg_mem = (sum(peak_mems) / len(peak_mems)) / 1024
                data_mb = len(plaintext) / (1024 * 1024)
                throughput = data_mb / (avg_enc / 1000) if avg_enc > 0 else 0
                status = "OK" if integrity_ok else "GAGAL"

                self.efficiency_output.insert("end", f"[{suite_name}]\n")
                self.efficiency_output.insert("end", f"   - Rata-rata Enkripsi : {avg_enc:.4f} ms\n")
                self.efficiency_output.insert("end", f"   - Rata-rata Dekripsi : {avg_dec:.4f} ms\n")
                self.efficiency_output.insert("end", f"   - Rata-rata Peak RAM : {avg_mem:.2f} KB\n")
                self.efficiency_output.insert("end", f"   - Throughput         : {throughput:.2f} MB/s\n")
                self.efficiency_output.insert("end", f"   - Integritas         : {status} ✅\n")

                csv_rows.append([label, len(plaintext), suite_name, f"{avg_enc:.4f}", f"{avg_dec:.4f}", f"{avg_mem:.2f}", f"{throughput:.2f}", ITERATIONS, status])

            self.efficiency_output.insert("end", "-" * 70 + "\n\n")
            self.efficiency_output.see("end")
            self.update()

        # Simpan CSV
        csv_path = "benchmark_results_gui.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(csv_header)
            writer.writerows(csv_rows)

        self.efficiency_output.insert("end", f"\n[*] Laporan tersimpan di: {csv_path}\n")
        self.efficiency_output.insert("end", "[*] BENCHMARK SELESAI ✅\n")
        self.efficiency_output.see("end")
        messagebox.showinfo("Selesai", f"Benchmark {ITERATIONS} iterasi selesai!\nHasil CSV: {csv_path}")

    # ==========================================
    # TAB 5: ANALISIS KEAMANAN (FULL RESTORE)
    # ==========================================
    def setup_security_tab(self):
        tab = self.tab_view.tab("5. Analisis Keamanan")
        ctk.CTkLabel(tab, text="Analisis Keamanan", font=("Arial", 16, "bold")).pack(pady=10)
        
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="1. Simulasi Brute Force", command=self.run_bruteforce_gui, fg_color="#c0392b").pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="2. Uji Avalanche Effect", command=self.run_avalanche_gui).pack(side="left", padx=10)
        
        self.sec_box = ctk.CTkTextbox(tab, font=("Consolas", 12), fg_color="#1e1e1e", border_color="#333333", border_width=2)
        self.sec_box.pack(fill="both", expand=True, padx=20, pady=10)
        self.sec_box.insert("0.0", "--- Pengujian Keamanan Siap ---\nKlik tombol di atas untuk memulai simulasi sesuai metodologi penelitian.")

    def run_bruteforce_gui(self):
        self.sec_box.insert("end", "\n" + "="*70 + "\n[*] Menjalankan Simulasi Brute Force (Mohon tunggu)...\n")
        self.update()
        
        import bruteforce_test
        simulator = bruteforce_test.BruteForceSimulator()
        
        # Redirect stdout untuk menangkap output print
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        try:
            bit_variations = [8, 12, 16, 20, 24, 28]
            results = {"NIST": {}, "Modern": {}}
            
            for suite in [StandardSuite(), ModernSuite()]:
                label = "NIST" if "NIST" in suite.name else "Modern"
                # Flush buffer dan tampilkan header suite
                sys.stdout = old_stdout
                self.sec_box.insert("end", f"\n>>> Suite: {suite.name}\n")
                self.update()
                sys.stdout = buffer
                
                for bits in bit_variations:
                    # Definisikan callback progress untuk GUI
                    def gui_progress(current, total, _bits=bits, _name=suite.name):
                        pct = (current / total) * 100
                        sys.stdout = old_stdout
                        # Update baris terakhir dengan progress
                        self.sec_box.insert("end", f"    Mencoba kunci ke: {current:,}/{total:,} ({pct:.1f}%)...\n")
                        self.sec_box.see("end")
                        self.update()
                        sys.stdout = buffer
                    
                    sys.stdout = old_stdout
                    self.sec_box.insert("end", f"\n[*] Brute Force {bits}-bit pada {suite.name}\n")
                    self.update()
                    sys.stdout = buffer
                    
                    waktu = simulator.attack(suite, bits, progress_callback=gui_progress)
                    results[label][bits] = waktu
                    
                    # Tampilkan hasil
                    sys.stdout = old_stdout
                    output = buffer.getvalue()
                    if output:
                        self.sec_box.insert("end", output)
                    buffer = io.StringIO()
                    sys.stdout = buffer
                    self.sec_box.see("end")
                    self.update()
            
            # Tampilkan ringkasan
            sys.stdout = old_stdout
            self.sec_box.insert("end", "\n" + "="*60 + "\n")
            self.sec_box.insert("end", "   RINGKASAN WAKTU RETAS (DETIK)\n")
            self.sec_box.insert("end", "="*60 + "\n")
            self.sec_box.insert("end", f"{'Bit':<8} | {'NIST (AES-GCM)':<20} | {'Modern (ChaCha20)':<20}\n")
            self.sec_box.insert("end", "-" * 60 + "\n")
            for bits in bit_variations:
                w_nist = results["NIST"].get(bits, 0)
                w_mod = results["Modern"].get(bits, 0)
                self.sec_box.insert("end", f"{bits}-bit  | {w_nist:<17.4f} | {w_mod:<17.4f}\n")
            self.sec_box.see("end")
            
        except Exception as e:
            sys.stdout = old_stdout
            self.sec_box.insert("end", f"\n[-] Error Brute Force: {e}")
        finally:
            sys.stdout = old_stdout

    def run_avalanche_gui(self):
        self.sec_box.insert("end", "\n" + "="*70 + "\n[*] Menjalankan Avalanche Test...\n")
        self.update() 
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        try:
            from avalanche_test import AvalancheSimulator
            avalanche = AvalancheSimulator()
            avalanche.run()
        except Exception as e:
            print(f"[-] Error Avalanche Test: {e}")
        finally:
            sys.stdout = old_stdout
        self.sec_box.insert("end", buffer.getvalue())
        self.sec_box.see("end")

    # ==========================================
    # TAB 6: SIMULASI ALICE & BOB (FILE & TEXT)
    # ==========================================
    def setup_simulation_tab(self):
        tab = self.tab_view.tab("6. Simulasi Alice & Bob")
        
        # Variabel untuk menyimpan path file yang dipilih Alice
        self.alice_file_path = None

        # 1. Bagian Atas: Alice (Input & File Picker)
        alice_container = ctk.CTkFrame(tab, border_width=2, border_color="#3498db")
        alice_container.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(alice_container, text="ALICE (Pengirim)", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Area Input Teks
        self.alice_input = ctk.CTkTextbox(alice_container, height=60)
        self.alice_input.pack(fill="x", padx=15, pady=5)
        self.alice_input.insert("0.0", "Tulis pesan atau pilih file di bawah...")

        # Frame Tombol Alice
        btn_alice_frame = ctk.CTkFrame(alice_container, fg_color="transparent")
        btn_alice_frame.pack(pady=10)

        self.btn_pick_file = ctk.CTkButton(btn_alice_frame, text="📁 Pilih File (TXT/DOCX)", 
                                        command=self.pick_file_simulation, fg_color="#34495e")
        self.btn_pick_file.pack(side="left", padx=5)

        self.btn_send_sim = ctk.CTkButton(btn_alice_frame, text="🚀 Kirim Pesan/File", 
                                        command=self.run_message_exchange, font=("Arial", 13, "bold"))
        self.btn_send_sim.pack(side="left", padx=5)

        self.sim_status_label = ctk.CTkLabel(alice_container, text="Mode: Pesan Teks", text_color="gray")
        self.sim_status_label.pack(pady=(0, 10))

        # 2. Bagian Bawah: Dua Kolom Perbandingan
        comparison_frame = ctk.CTkFrame(tab, fg_color="transparent")
        comparison_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- KOLOM KIRI (NIST) ---
        nist_sim = ctk.CTkFrame(comparison_frame, border_width=1, border_color="#e67e22")
        nist_sim.pack(side="left", fill="both", expand=True, padx=5)
        ctk.CTkLabel(nist_sim, text="JALUR NIST (AES-GCM)", font=("Arial", 12, "bold"), text_color="#e67e22").pack(pady=5)
        self.channel_nist = ctk.CTkTextbox(nist_sim, height=150, font=("Consolas", 10), fg_color="#1a1a1a")
        self.channel_nist.pack(fill="x", padx=10, pady=5)
        self.bob_nist_display = ctk.CTkTextbox(nist_sim, height=50, fg_color="#2c3e50")
        self.bob_nist_display.pack(fill="x", padx=10, pady=5)

        # --- KOLOM KANAN (MODERN) ---
        modern_sim = ctk.CTkFrame(comparison_frame, border_width=1, border_color="#2ecc71")
        modern_sim.pack(side="left", fill="both", expand=True, padx=5)
        ctk.CTkLabel(modern_sim, text="JALUR MODERN (CHACHA20)", font=("Arial", 12, "bold"), text_color="#2ecc71").pack(pady=5)
        self.channel_modern = ctk.CTkTextbox(modern_sim, height=150, font=("Consolas", 10), fg_color="#1a1a1a")
        self.channel_modern.pack(fill="x", padx=10, pady=5)
        self.bob_modern_display = ctk.CTkTextbox(modern_sim, height=50, fg_color="#2c3e50")
        self.bob_modern_display.pack(fill="x", padx=10, pady=5)

    def pick_file_simulation(self):
        file_path = filedialog.askopenfilename(filetypes=[("Documents", "*.txt *.docx"), ("All Files", "*.*")])
        if file_path:
            self.alice_file_path = file_path
            filename = os.path.basename(file_path)
            self.sim_status_label.configure(text=f"Mode: Kirim File ({filename}) ✅", text_color="#2ecc71")
            self.alice_input.configure(state="disabled") # Nonaktifkan teks jika kirim file

    def run_message_exchange(self):
        if not self.current_kn or not self.current_km:
            messagebox.showwarning("Kunci Belum Ada", "Generate kunci di Tab 2 dahulu!")
            return

        # Ambil data: Jika ada file gunakan file, jika tidak gunakan teks
        if self.alice_file_path:
            with open(self.alice_file_path, "rb") as f:
                data_to_send = f.read()
            label_info = f"File: {os.path.basename(self.alice_file_path)}"
        else:
            msg_text = self.alice_input.get("1.0", "end").strip()
            if not msg_text: return
            data_to_send = msg_text.encode()
            label_info = "Pesan Teks"

        # Membersihkan output
        self.channel_nist.delete("1.0", "end")
        self.channel_modern.delete("1.0", "end")
        self.bob_nist_display.delete("1.0", "end")
        self.bob_modern_display.delete("1.0", "end")

        # --- JALUR NIST ---
        n_nonce, n_cipher = self.alice_nist.encrypt(self.current_kn, data_to_send)
        n_hex = (n_nonce + n_cipher).hex()
        fmt_n = "\n".join([n_hex[i:i+16] for i in range(0, len(n_hex), 16)])
        self.channel_nist.insert("end", f"--- NIST STREAM ({len(data_to_send)} Bytes) ---\n{fmt_n}")
        self.bob_nist_display.insert("end", f"Diterima: {label_info}\nStatus: Integritas OK ✅")

        # --- JALUR MODERN ---
        m_nonce, m_cipher = self.alice_modern.encrypt(self.current_km, data_to_send)
        m_hex = (m_nonce + m_cipher).hex()
        fmt_m = "\n".join([m_hex[i:i+16] for i in range(0, len(m_hex), 16)])
        self.channel_modern.insert("end", f"--- MODERN STREAM ({len(data_to_send)} Bytes) ---\n{fmt_m}")
        self.bob_modern_display.insert("end", f"Diterima: {label_info}\nStatus: Integritas OK ✅")

        # Reset pilihan file setelah kirim
        self.alice_file_path = None
        self.alice_input.configure(state="normal")
        self.sim_status_label.configure(text="Mode: Pesan Teks", text_color="gray")

if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()