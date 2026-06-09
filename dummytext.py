import os
try:
    from docx import Document
except ImportError:
    print("[-] Library python-docx belum terinstall. Ketik: pip install python-docx")
    exit()

BASE_TEXT = (
    "Ini adalah dokumen rahasia simulasi untuk pengujian algoritma kriptografi hibrida. "
    "Penelitian ini bertujuan untuk melakukan analisis komparatif efisiensi dan keamanan "
    "antara standar algoritma NIST (ECDH P-256 dan AES-GCM) dengan algoritma Modern "
    "(X25519 dan ChaCha20-Poly1305) pada pesan teks. Institut Teknologi Sepuluh Nopember "
    "menjadi tempat dilaksanakannya riset keamanan siber ini. Data ini di-generate "
    "secara otomatis untuk memenuhi target ukuran file (size) yang dibutuhkan dalam "
    "pengujian performa (benchmark) penggunaan prosesor dan alokasi memori RAM. "
)

def generate_readable_content(target_bytes):
    content_bytes = BASE_TEXT.encode('utf-8')
    multiplier = (target_bytes // len(content_bytes)) + 1
    final_content = (content_bytes * multiplier)[:target_bytes]
    return final_content.decode('utf-8', errors='ignore')

def create_dummy_files():
    """Membuat file TXT (Raw) dan DOCX (Compressed) untuk perbandingan."""
    variasi_ukuran = {
        "1KB": 1024,
        "10KB": 10 * 1024,
        "100KB": 100 * 1024,
        "500KB": 500 * 1024,
        "1MB": 1024 * 1024,
        "10MB": 10 * 1024 * 1024 
    }

    if not os.path.exists('data'):
        os.makedirs('data')

    print("=== Pembangkitan Dataset: Analisis Kompresi ===")
    for label, size in variasi_ukuran.items():
        text_content = generate_readable_content(size)
        
        # 1. Simpan sebagai TXT (Ukuran Murni / Uncompressed)
        txt_path = f"data/{label}_TXT.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text_content)
        txt_size = os.path.getsize(txt_path)
            
        # 2. Simpan sebagai DOCX Asli (Terkompresi ZIP)
        docx_path = f"data/{label}_DOCX.docx"
        doc = Document()
        doc.add_paragraph(text_content)
        doc.save(docx_path)
        docx_size = os.path.getsize(docx_path)
        
        print(f"[-] Target Logis: {size/1024:,.0f} KB")
        print(f"    > TXT Fisik : {txt_size/1024:,.0f} KB (100% Raw)")
        print(f"    > DOCX Fisik: {docx_size/1024:,.1f} KB (Efek Kompresi ZIP MS Word)")
        print("-" * 45)

def load_data_to_ram():
    dataset = {}
    folder = 'data'
    if not os.path.exists(folder): return {}
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".txt") or filename.endswith(".docx"):
            label = filename.replace(".txt", "").replace(".docx", "").upper()
            with open(os.path.join(folder, filename), "rb") as f:
                dataset[label] = f.read()
    return dataset

if __name__ == "__main__":
    create_dummy_files()