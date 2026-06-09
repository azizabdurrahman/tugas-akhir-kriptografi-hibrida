import os
from standardsuite import StandardSuite
from modernsuite import ModernSuite


class AvalancheSimulator:
    def __init__(self):
        """Inisialisasi parameter pengujian Avalanche Effect.
        Pengujian dilakukan dengan membalik 1 bit pada kunci sesi,
        menggunakan plaintext dan nonce yang sama untuk kedua enkripsi,
        sehingga perbedaan ciphertext murni berasal dari perubahan kunci.
        """
        self.plaintext = b"Pesan untuk Uji Avalanche Effect 2026"

    def load_key_from_session(self, suite_name):
        """Memuat kunci aktif dari direktori session_keys/."""
        clean_name = "nist" if "NIST" in suite_name else "modern"
        filepath = f"session_keys/{clean_name}_current.key"

        if not os.path.exists(filepath):
            return None

        with open(filepath, "rb") as f:
            return f.read()

    def flip_single_bit(self, data: bytes, bit_position: int) -> bytes:
        """Membalik satu bit spesifik menggunakan operasi XOR."""
        byte_array = bytearray(data)
        byte_index = bit_position // 8
        bit_index = bit_position % 8
        byte_array[byte_index] ^= (1 << bit_index)
        return bytes(byte_array)

    def count_bit_difference(self, data1: bytes, data2: bytes):
        """Menghitung Hamming Distance (perbedaan bit) antara dua dataset."""
        diff_count = 0
        for b1, b2 in zip(data1, data2):
            xor_result = b1 ^ b2
            diff_count += bin(xor_result).count('1')
        return diff_count

    def test_avalanche(self, suite):
        """Menjalankan analisis sensitivitas bit pada kunci sesi.

        Metode sesuai Bab 3.7.2:
        (a) Enkripsi plaintext P dengan kunci asli K1 dan nonce tetap N -> C1
        (b) Flip 1 bit pada K1 menjadi K2, enkripsi P dengan K2 dan nonce N -> C2
        (c) Hitung Hamming Distance antara C1 dan C2
        Target: nilai AE mendekati 50% (sifat difusi yang baik).
        """
        print(f"\n" + "="*55)
        print(f" UJI AVALANCHE EFFECT: {suite.name} ")
        print("="*55)

        # 1. Muat kunci asli (K1) dari session
        original_key = self.load_key_from_session(suite.name)
        if original_key is None:
            print(f"[-] Error: Kunci {suite.name} tidak ditemukan.")
            print(f"    Jalankan suite yang sesuai (standardsuite.py / modernsuite.py) dahulu.")
            return

        # 2. Modifikasi 1 bit pertama pada kunci (K2)
        modified_key = self.flip_single_bit(original_key, 0)

        print(f"[*] Kunci Asli K1 (Hex) : {original_key.hex()[:32]}...")
        print(f"[*] Kunci Modif K2 (Hex): {modified_key.hex()[:32]}...")
        print(f"[*] Selisih Kunci       : 1 bit")

        # 3. Bangkitkan nonce TETAP untuk kedua enkripsi
        #    Ini memastikan perbedaan ciphertext murni karena perubahan kunci,
        #    bukan karena randomness nonce.
        fixed_nonce = os.urandom(12)
        print(f"[*] Nonce Tetap (Hex)   : {fixed_nonce.hex()}")

        # 4. Enkripsi dengan nonce yang sama (isolasi variabel)
        c1 = suite.encrypt_with_nonce(original_key, fixed_nonce, self.plaintext)
        c2 = suite.encrypt_with_nonce(modified_key, fixed_nonce, self.plaintext)

        print("\n[PERBANDINGAN CIPHERTEXT]")
        print(f" >> C1 : {c1.hex()[:60]}...")
        print(f" >> C2 : {c2.hex()[:60]}...")

        # 5. Kalkulasi persentase perubahan bit pada CIPHERTEXT saja
        #    (sesuai rumus AE di Bab 2.9.2: AE = HD(C1, C2) / N * 100%)
        min_len = min(len(c1), len(c2))
        bits_changed = self.count_bit_difference(c1[:min_len], c2[:min_len])
        total_bits = min_len * 8
        ae_pct = (bits_changed / total_bits) * 100

        print("\n[HASIL ANALISIS]")
        print(f" - Total Bit Ciphertext : {total_bits} bit")
        print(f" - Bit Berubah          : {bits_changed} bit")
        print(f" - Persentase (AE)      : {ae_pct:.2f} %")

        status = "SANGAT BAIK" if 45 <= ae_pct <= 55 else "KURANG OPTIMAL"
        print(f" - Kesimpulan           : {status}")

    def run(self):
        """Eksekusi pengujian untuk suite NIST dan Modern."""
        self.test_avalanche(StandardSuite())
        self.test_avalanche(ModernSuite())


if __name__ == "__main__":
    tester = AvalancheSimulator()
    tester.run()
