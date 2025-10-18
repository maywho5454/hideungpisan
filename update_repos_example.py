import os
import re
import requests
from github import Github

# --- KONFIGURASI ---
# Token dengan izin menulis ke 10 repo ini, disimpan di environment variable
GITHUB_TOKEN = os.getenv("GITHUB_PAT")

# File sumber (tanpa footer)
SOURCE_URL = "https://raw.githubusercontent.com/maywho5454/hideungpisan/refs/heads/main/hideungpisan.m3u"

# Branch dan nama file target di tiap repo
BRANCH = "main"
TARGET_FILE = "hideungpisan.m3u"

# 10 repositori contoh
USERNAME = "maywho5454"
REPO_LIST = [
    "19oktober2025",
    "20oktober2025",
    "21oktober2025",
    "22oktober2025",
    "23oktober2025",
    "24oktober2025",
    "25oktober2025",
    "26oktober2025",
    "27oktober2025",
    "28oktober2025",
]

# --- FUNGSI ---
def clean_and_add_footer(content, tanggal):
    """Hapus footer lama dan tambahkan footer baru sesuai tanggal."""
    content = re.sub(r'#EXTM3U billed-msg=.*', '', content).strip()
    footer = f'#EXTM3U billed-msg="😎{tanggal} | lynk.id/magelife😎"'
    return f"{content}\n\n{footer}\n"

def main():
    if not GITHUB_TOKEN:
        print("❌ Environment variable GITHUB_PAT belum diatur.")
        return

    # Ambil konten master
    print("📥 Mengambil file sumber...")
    r = requests.get(SOURCE_URL)
    r.raise_for_status()
    base_content = r.text

    # Koneksi ke GitHub
    g = Github(GITHUB_TOKEN)

    for repo_name in REPO_LIST:
        tanggal = repo_name.replace(USERNAME+"/", "")  # "19oktober2025"
        repo_fullname = f"{USERNAME}/{repo_name}"
        print(f"\n🔄 Memproses: {repo_fullname}")

        try:
            repo = g.get_repo(repo_fullname)
        except Exception as e:
            print(f"  ❌ Tidak bisa mengakses {repo_fullname}: {e}")
            continue

        # Buat konten baru
        final_content = clean_and_add_footer(base_content, tanggal)

        try:
            contents = repo.get_contents(TARGET_FILE, ref=BRANCH)
            sha = contents.sha
            old = contents.decoded_content.decode("utf-8")
            if old.strip() == final_content.strip():
                print("  ✅ Sudah versi terbaru, dilewati.")
                continue

            repo.update_file(
                TARGET_FILE,
                f"Auto update footer untuk {tanggal}",
                final_content,
                sha,
                branch=main,
            )
            print("  ✅ Berhasil diperbarui.")
        except Exception as e:
            # Jika file belum ada
            print("  ⚠️ File belum ada, mencoba membuat baru...")
            try:
                repo.create_file(
                    TARGET_FILE,
                    f"Auto create dengan footer {tanggal}",
                    final_content,
                    branch=main,
                )
                print("  ✅ File baru berhasil dibuat.")
            except Exception as inner:
                print(f"  ❌ Gagal membuat file: {inner}")

if __name__ == "__main__":
    main()
