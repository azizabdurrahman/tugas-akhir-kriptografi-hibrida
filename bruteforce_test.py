import time
import os
from cryptography.exceptions import InvalidTag
from standardsuite import StandardSuite
from modernsuite import ModernSuite

class BruteForceSimulator:
    def __init__(self):
        """Inisialisasi target serangan simulasi brute force."""
        self.target_plaintext = b"Pesan Rahasia Simulasi Brute Force 2026"

    def load_key_from_session(self, suite_name):
        """Memuat kunci sesi aktif dari folder session_keys/."""
        clean_name = "nist" if "NIST" in suite_name else "modern"
        filepath = f"session_keys/{clean_name}_current.key"
        
        if not os.path.exists(filepath):
            return None
            
        with open(filepath, "rb") as f:
            return f.read()

    def attack(self, suite, bit_length, progress_callback=None):
        """Simulasi serangan Brute Force dengan skenario Partial Key Exposure."""
        max_keys = 2 ** bit_length
        print(f"\n[*] Menjalankan Brute Force {bit_length}-bit pada {suite.name}")
        
        real_key = self.load_key_from_session(suite.name)
        if real_key is None:
            print(f"    [-] ERROR: File kunci tidak ditemukan. Jalankan main.py dahulu.")
            return 0

        # Persiapan masking bit untuk mensimulasikan pencarian sisa bit kunci
        real_key_int = int.from_bytes(real_key, byteorder='big')
        mask = ((1 << 256) - 1) - ((1 << bit_length) - 1)
        fixed_part_int = real_key_int & mask
        
        nonce, ciphertext = suite.encrypt(real_key, self.target_plaintext)
        
        # Tentukan interval progress berdasarkan ukuran ruang kunci
        progress_interval = max(1, max_keys // 20)  
        
        start_time = time.perf_counter()
        cracked = False
        guess_int = 0
        found_key = None

        for i in range(max_keys):
            guess_int = i
            guess_key_int = fixed_part_int | guess_int
            guess_key = guess_key_int.to_bytes(32, byteorder='big')
            
            # Progress callback untuk GUI
            if progress_callback and (i % progress_interval == 0) and i > 0:
                progress_callback(i, max_keys)
            
            try:
                decrypted = suite.decrypt(guess_key, nonce, ciphertext)
                if decrypted == self.target_plaintext:
                    cracked = True
                    found_key = guess_key
                    break
            except InvalidTag:
                pass

        elapsed_time = time.perf_counter() - start_time

        if cracked:
            print(f"    [+] Berhasil pada iterasi ke: {guess_int}")
            print(f"    [+] Waktu: {elapsed_time:.4f} detik")
            
            # --- PEMBUKTIAN VISUAL HEXADECIMAL ---
            hex_chars = bit_length // 4
            masked_guess = ("*" * (64 - hex_chars)) + found_key.hex()[-hex_chars:]
            
            print(f"    [PEMBUKTIAN VISUAL]")
            print(f"    >> Asli   : {real_key.hex()}")
            print(f"    >> Retas  : {masked_guess}")
            print(f"    >> Status : IDENTIK (Kunci Sesi Berhasil Ditembus)")
        else:
            print(f"    [-] Gagal menemukan kunci.")

        return elapsed_time

    def run_all_tests(self):
        """Menjalankan serangkaian pengujian brute force pada berbagai variasi bit."""
        print("="*60)
        print("   SIMULASI KEAMANAN: PARTIAL KEY EXPOSURE ATTACK   ")
        print("="*60)
        
        bit_variations = [8, 12, 16, 20, 24, 28]
        results = {"NIST": {}, "Modern": {}}

        for suite in [StandardSuite(), ModernSuite()]:
            print(f"\n>>> Suite: {suite.name}")
            for bits in bit_variations:
                waktu = self.attack(suite, bits)
                label = "NIST" if "NIST" in suite.name else "Modern"
                results[label][bits] = waktu
                
        print("\n" + "="*60)
        print("   RINGKASAN WAKTU RETAS (DETIK)   ")
        print("="*60)
        print(f"{'Bit':<8} | {'NIST (AES-GCM)':<20} | {'Modern (ChaCha20)':<20}")
        print("-" * 60)
        for bits in bit_variations:
            w_nist = results["NIST"].get(bits, 0)
            w_mod = results["Modern"].get(bits, 0)
            print(f"{bits}-bit  | {w_nist:<17.4f} | {w_mod:<17.4f}")

if __name__ == "__main__":
    simulator = BruteForceSimulator()
    simulator.run_all_tests()