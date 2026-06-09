import os
import time
import tracemalloc
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Import modul dummytext HANYA untuk memuat data
import dummytext


class StandardSuite:
    def __init__(self):
        """Inisialisasi suite standar NIST menggunakan ECDH P-256 dan AES-GCM."""
        self.name = "NIST (P-256/AES-GCM)"
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()

    def get_pem_keys(self):
        """Mengekspor kunci asimetris ke format PEM untuk disimpan sebagai file."""
        priv_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        pub_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return priv_pem, pub_pem

    def get_shared_key(self, peer_public_key):
        """Proses Key Exchange ECDH dan Derivasi Kunci menggunakan HKDF."""
        shared_secret = self.private_key.exchange(ec.ECDH(), peer_public_key)
        return HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"hybrid_encryption_session",
        ).derive(shared_secret)

    def encrypt(self, key, plaintext):
        """Enkripsi data menggunakan algoritma AEAD AES-GCM."""
        aes = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aes.encrypt(nonce, plaintext, None)
        return nonce, ciphertext

    def encrypt_with_nonce(self, key, nonce, plaintext):
        """Enkripsi dengan nonce yang ditentukan (untuk pengujian Avalanche Effect)."""
        aes = AESGCM(key)
        return aes.encrypt(nonce, plaintext, None)

    def decrypt(self, key, nonce, ciphertext):
        """Dekripsi data menggunakan algoritma AEAD AES-GCM."""
        aes = AESGCM(key)
        return aes.decrypt(nonce, ciphertext, None)


if __name__ == "__main__":
    print("======================================================")
    print("   NIST ENCRYPTION (P-256/AES-GCM)")
    print("   Simulasi Pertukaran Kunci Alice <-> Bob")
    print("======================================================")

    # 1. Menyiapkan folder penyimpanan
    os.makedirs("output_nist", exist_ok=True)
    os.makedirs("session_keys", exist_ok=True)
    os.makedirs("key_pairs", exist_ok=True)

    # 2. Inisialisasi dua entitas: Alice (pengirim) dan Bob (penerima)
    print("\n[FASE 1] Inisialisasi Pasangan Kunci Asimetris")
    print("-" * 54)
    alice = StandardSuite()
    bob = StandardSuite()
    print("[*] Alice berhasil membangkitkan pasangan kunci P-256.")
    print("[*] Bob   berhasil membangkitkan pasangan kunci P-256.")

    # 3. Ekspor dan simpan kunci asimetris kedua pihak (.pem)
    alice_priv_pem, alice_pub_pem = alice.get_pem_keys()
    bob_priv_pem, bob_pub_pem = bob.get_pem_keys()

    with open("key_pairs/nist_alice_private.pem", "wb") as f:
        f.write(alice_priv_pem)
    with open("key_pairs/nist_alice_public.pem", "wb") as f:
        f.write(alice_pub_pem)
    with open("key_pairs/nist_bob_private.pem", "wb") as f:
        f.write(bob_priv_pem)
    with open("key_pairs/nist_bob_public.pem", "wb") as f:
        f.write(bob_pub_pem)
    print("[*] Kunci Asimetris tersimpan di: key_pairs/nist_alice_*.pem & nist_bob_*.pem")

    # 4. Pertukaran Kunci Diffie-Hellman (ECDH)
    print("\n[FASE 2] Pertukaran Kunci ECDH dan Derivasi HKDF")
    print("-" * 54)
    key_alice = alice.get_shared_key(bob.public_key)    
    key_bob = bob.get_shared_key(alice.public_key)      

    # 5. Validasi matematis: shared secret Alice dan Bob harus identik
    if key_alice == key_bob:
        print("[+] Shared Secret Alice IDENTIK dengan Shared Secret Bob ✅")
        print(f"    Kunci Sesi (Hex): {key_alice.hex()[:32]}...")
    else:
        print("[-] ERROR: Shared Secret Alice dan Bob TIDAK IDENTIK!")
        exit()

    # 6. Simpan kunci sesi untuk digunakan modul lain (avalanche, brute force, dll)
    session_key = key_alice
    key_path = "session_keys/nist_current.key"
    with open(key_path, "wb") as f:
        f.write(session_key)
    print(f"[*] Kunci Sesi Simetris tersimpan di: {key_path}")

    # 7. Memuat dataset hasil dari dummytext.py
    try:
        dataset = dummytext.load_data_to_ram()
    except Exception:
        dataset = {}

    if not dataset:
        print("\n[-] ERROR: Dataset kosong. Jalankan 'dummytext.py' dulu!")
        exit()

    def get_size_value(label):
        units = {"KB": 1024, "MB": 1024 * 1024}
        num = "".join([c for c in label.split("_")[0] if c.isdigit()])
        unit = "".join([c for c in label.split("_")[0] if c.isalpha()]).upper()
        return int(num) * units.get(unit, 1)

    sorted_labels = sorted(dataset.keys(), key=get_size_value)

    # 8. Loop Enkripsi dan Pengukuran Performa
    print("\n[FASE 3] Enkripsi Data oleh Alice untuk Bob")
    print("-" * 54)
    for label in sorted_labels:
        plaintext = dataset[label]
        print(f"\n>>> PENGUJIAN DATA: {label} ({len(plaintext):,} bytes)")
        print("-" * 54)

        tracemalloc.start()
        start_time = time.perf_counter()

        nonce, ciphertext = alice.encrypt(session_key, plaintext)

        end_time = time.perf_counter()
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        final_hex = (nonce + ciphertext).hex()
        safe_name = label.lower().replace(".", "_")
        with open(f"output_nist/ciphertext_{safe_name}.enc", "w") as f:
            f.write(final_hex)

        # Verifikasi integritas: Bob mendekripsi untuk memastikan pesan valid
        decrypted = bob.decrypt(session_key, nonce, ciphertext)
        integrity_status = "Integritas OK ✅" if decrypted == plaintext else "GAGAL ❌"

        print(f"[{alice.name}]")
        print(f"   - Waktu Enkripsi : {(end_time - start_time) * 1000:.3f} ms")
        print(f"   - Puncak RAM     : {peak_mem / 1024:.2f} KB")
        print(f"   - Status         : {integrity_status}")
