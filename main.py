import os
import csv
import time
import tracemalloc

# Import modul penelitian
import dummytext
from standardsuite import StandardSuite
from modernsuite import ModernSuite
from avalanche_test import AvalancheSimulator
from bruteforce_test import BruteForceSimulator

# ========================================
# KONFIGURASI PENGUJIAN
# ========================================
ITERATIONS = 100   # Jumlah iterasi per ukuran data (sesuai Bab 3.7.1)
CSV_PATH = "benchmark_results.csv"


def prepare_folders():
    """Menyiapkan direktori output yang dibutuhkan sistem."""
    folders = ['output_nist', 'output_modern', 'session_keys',
               'key_pairs', 'data', 'data_decrypt']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)


def save_pem_keys(suite, prefix, role):
    """Menyimpan pasangan kunci asimetris (.pem) ke direktori key_pairs/."""
    priv_pem, pub_pem = suite.get_pem_keys()
    with open(f"key_pairs/{prefix}_{role}_private.pem", "wb") as f:
        f.write(priv_pem)
    with open(f"key_pairs/{prefix}_{role}_public.pem", "wb") as f:
        f.write(pub_pem)


def save_session_key(prefix, key):
    """Menyimpan kunci sesi simetris (.key) ke direktori session_keys/."""
    filename = f"session_keys/{prefix}_current.key"
    with open(filename, "wb") as f:
        f.write(key)
    return filename


def get_size_value(label):
    """Helper untuk sorting label file berdasarkan ukuran (KB -> MB)."""
    units = {"KB": 1024, "MB": 1024 * 1024}
    num = "".join([c for c in label.split("_")[0] if c.isdigit()])
    unit = "".join([c for c in label.split("_")[0] if c.isalpha()]).upper()
    return (int(num) * units.get(unit, 1), 0 if "TXT" in label else 1)


def benchmark_suite(suite_sender, suite_receiver, key, plaintext, iterations):
    """Menjalankan pengukuran performa dengan N iterasi.

    Parameter yang diukur (sesuai Bab 2.9.1 draf):
    - Waktu Enkripsi rata-rata (Et) dalam milidetik
    - Waktu Dekripsi rata-rata (Dt) dalam milidetik
    - Puncak memori (peak_mem) dalam KB
    - Throughput (Tp = S/Et) dalam MB/s
    - Status integritas
    """
    enc_times = []
    dec_times = []
    peak_mems = []
    integrity_ok = True
    iteration_counter = 0

    for i in range(iterations):
        # --- Pengukuran Enkripsi ---
        tracemalloc.start()
        start = time.perf_counter()
        nonce, ciphertext = suite_sender.encrypt(key, plaintext)
        enc_time = time.perf_counter() - start
        enc_times.append(enc_time)
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak_mems.append(peak_mem)

        # --- Pengukuran Dekripsi ---
        start = time.perf_counter()
        decrypted = suite_receiver.decrypt(key, nonce, ciphertext)
        dec_time = time.perf_counter() - start
        dec_times.append(dec_time)

        if decrypted != plaintext:
            integrity_ok = False

        iteration_counter += 1

        # Progress log per iterasi
        print(f"      [iter {i+1:3d}/{iterations}]", end="\r")

    # Sanity check: pastikan loop benar-benar berjalan N kali
    assert iteration_counter == iterations, \
        f"Loop hanya berjalan {iteration_counter}/{iterations} iterasi!"
    assert len(enc_times) == iterations, \
        f"Data enkripsi terkumpul {len(enc_times)}/{iterations}!"
    print()  # newline setelah progress \r selesai

    avg_enc_ms = (sum(enc_times) / len(enc_times)) * 1000
    avg_dec_ms = (sum(dec_times) / len(dec_times)) * 1000
    avg_peak_kb = (sum(peak_mems) / len(peak_mems)) / 1024

    # Throughput dihitung dari rata-rata waktu enkripsi
    data_size_mb = len(plaintext) / (1024 * 1024)
    throughput_mbps = data_size_mb / (avg_enc_ms / 1000) if avg_enc_ms > 0 else 0

    # Total waktu kumulatif (bukti iterasi benar-benar berjalan)
    total_enc_sec = sum(enc_times)
    total_dec_sec = sum(dec_times)

    # Simpan 1 ciphertext terakhir untuk arsip
    return {
        "avg_enc_ms": avg_enc_ms,
        "avg_dec_ms": avg_dec_ms,
        "avg_peak_kb": avg_peak_kb,
        "throughput_mbps": throughput_mbps,
        "total_enc_sec": total_enc_sec,
        "total_dec_sec": total_dec_sec,
        "iterations_done": iteration_counter,
        "integrity": "OK" if integrity_ok else "GAGAL",
        "last_nonce": nonce,
        "last_ciphertext": ciphertext,
        "last_decrypted": decrypted
    }


def run_efficiency_phase():
    """Fase 1: Benchmark komparatif efisiensi kedua skema hibrida."""
    print("\n" + "=" * 70)
    print("   FASE 1: ANALISIS KOMPARATIF EFISIENSI HIBRIDA")
    print(f"   (Rata-rata {ITERATIONS} iterasi per ukuran data)")
    print("=" * 70)

    # 1. Siapkan dataset
    dummytext.create_dummy_files()
    dataset = dummytext.load_data_to_ram()
    sorted_labels = sorted(dataset.keys(), key=get_size_value)
    prepare_folders()

    # 2. Simulasi pertukaran kunci Alice <-> Bob untuk kedua skema
    print("\n[SETUP] Inisialisasi pasangan kunci Alice dan Bob")
    print("-" * 70)
    alice_nist, bob_nist = StandardSuite(), StandardSuite()
    alice_modern, bob_modern = ModernSuite(), ModernSuite()

    # Simpan pasangan kunci asimetris (.pem) untuk arsip
    save_pem_keys(alice_nist, "nist", "alice")
    save_pem_keys(bob_nist, "nist", "bob")
    save_pem_keys(alice_modern, "modern", "alice")
    save_pem_keys(bob_modern, "modern", "bob")

    # Key exchange dan validasi
    kn_alice = alice_nist.get_shared_key(bob_nist.public_key)
    kn_bob = bob_nist.get_shared_key(alice_nist.public_key)
    km_alice = alice_modern.get_shared_key(bob_modern.public_key)
    km_bob = bob_modern.get_shared_key(alice_modern.public_key)

    assert kn_alice == kn_bob, "NIST: Shared secret tidak sinkron!"
    assert km_alice == km_bob, "Modern: Shared secret tidak sinkron!"
    print("[+] NIST   : Shared Secret Alice IDENTIK dengan Bob ✅")
    print("[+] Modern : Shared Secret Alice IDENTIK dengan Bob ✅")

    # Simpan kunci sesi
    save_session_key("nist", kn_alice)
    save_session_key("modern", km_alice)
    print("[*] Kunci sesi tersimpan di: session_keys/")

    # 3. Inisialisasi CSV logger
    csv_rows = []
    csv_header = [
        "Label", "Size_Bytes", "Suite",
        "Avg_Enc_Time_ms", "Avg_Dec_Time_ms",
        "Avg_Peak_Mem_KB", "Throughput_MBps",
        "Iterations", "Integrity"
    ]

    # 4. Loop pengujian per ukuran data
    for label in sorted_labels:
        plaintext = dataset[label]
        print(f"\n>>> PENGUJIAN DATA: {label} ({len(plaintext):,} bytes)")
        print("-" * 70)

        # --- NIST Suite ---
        result_nist = benchmark_suite(
            alice_nist, bob_nist, kn_alice, plaintext, ITERATIONS
        )
        print(f"[{alice_nist.name}]")
        print(f"   - Iterasi Selesai    : {result_nist['iterations_done']}/{ITERATIONS}")
        print(f"   - Total Waktu Enc    : {result_nist['total_enc_sec']:.4f} detik")
        print(f"   - Rata-rata Enkripsi : {result_nist['avg_enc_ms']:.4f} ms")
        print(f"   - Rata-rata Dekripsi : {result_nist['avg_dec_ms']:.4f} ms")
        print(f"   - Rata-rata Peak RAM : {result_nist['avg_peak_kb']:.2f} KB")
        print(f"   - Throughput         : {result_nist['throughput_mbps']:.2f} MB/s")
        print(f"   - Integritas         : {result_nist['integrity']} ✅")

        safe_name = label.lower().replace(".", "_")
        # Simpan ciphertext
        enc_hex = (result_nist["last_nonce"] + result_nist["last_ciphertext"]).hex()
        with open(f"output_nist/ciphertext_{safe_name}.enc", "w") as f:
            f.write(enc_hex)
        # Simpan hasil dekripsi
        with open(f"data_decrypt/nist_{safe_name}.dec", "wb") as f:
            f.write(result_nist["last_decrypted"])

        csv_rows.append([
            label, len(plaintext), alice_nist.name,
            f"{result_nist['avg_enc_ms']:.4f}",
            f"{result_nist['avg_dec_ms']:.4f}",
            f"{result_nist['avg_peak_kb']:.2f}",
            f"{result_nist['throughput_mbps']:.2f}",
            ITERATIONS, result_nist["integrity"]
        ])

        # --- Modern Suite ---
        result_modern = benchmark_suite(
            alice_modern, bob_modern, km_alice, plaintext, ITERATIONS
        )
        print(f"[{alice_modern.name}]")
        print(f"   - Iterasi Selesai    : {result_modern['iterations_done']}/{ITERATIONS}")
        print(f"   - Total Waktu Enc    : {result_modern['total_enc_sec']:.4f} detik")
        print(f"   - Rata-rata Enkripsi : {result_modern['avg_enc_ms']:.4f} ms")
        print(f"   - Rata-rata Dekripsi : {result_modern['avg_dec_ms']:.4f} ms")
        print(f"   - Rata-rata Peak RAM : {result_modern['avg_peak_kb']:.2f} KB")
        print(f"   - Throughput         : {result_modern['throughput_mbps']:.2f} MB/s")
        print(f"   - Integritas         : {result_modern['integrity']} ✅")

        # Simpan ciphertext
        enc_hex_m = (result_modern["last_nonce"] + result_modern["last_ciphertext"]).hex()
        with open(f"output_modern/ciphertext_{safe_name}.enc", "w") as f:
            f.write(enc_hex_m)
        # Simpan hasil dekripsi
        with open(f"data_decrypt/modern_{safe_name}.dec", "wb") as f:
            f.write(result_modern["last_decrypted"])

        csv_rows.append([
            label, len(plaintext), alice_modern.name,
            f"{result_modern['avg_enc_ms']:.4f}",
            f"{result_modern['avg_dec_ms']:.4f}",
            f"{result_modern['avg_peak_kb']:.2f}",
            f"{result_modern['throughput_mbps']:.2f}",
            ITERATIONS, result_modern["integrity"]
        ])

    # 5. Simpan hasil ke CSV
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        writer.writerows(csv_rows)
    print(f"\n[*] Laporan lengkap tersimpan di: {CSV_PATH}")


def run_security_phase():
    """Fase 2: Pengujian keamanan (Avalanche Effect + Brute Force)."""
    print("\n" + "=" * 70)
    print("   FASE 2: PENGUJIAN KEAMANAN ALGORITMA")
    print("=" * 70)

    # 1. UJI AVALANCHE EFFECT
    print("\n>>> [1/2] MENJALANKAN AVALANCHE EFFECT TEST...")
    try:
        avalanche = AvalancheSimulator()
        avalanche.run()
    except Exception as e:
        print(f"[-] Gagal menjalankan Avalanche Test: {e}")

    # 2. SIMULASI BRUTE FORCE (Partial Key Exposure)
    print("\n>>> [2/2] MENJALANKAN SIMULASI BRUTE FORCE...")
    try:
        bruteforce = BruteForceSimulator()
        bruteforce.run_all_tests()
    except Exception as e:
        print(f"[-] Gagal menjalankan Brute Force: {e}")


if __name__ == "__main__":
    run_efficiency_phase()
    run_security_phase()
