import sys
import subprocess
from scraper import get_samehadaku_video, resolve_gofile_url

def play_video(url):
    print(f"Playing: {url}")
    try:
        subprocess.run(['mpv', url], check=True)
    except FileNotFoundError:
        print("Error: MPV not found. Please install mpv.")
    except Exception as e:
        print(f"Error playing video: {e}")

def main():
    print("=== Samehadaku Addon Tester ===")
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Masukkan URL Episode Samehadaku: ").strip()

    if not url:
        print("URL tidak boleh kosong.")
        return

    print(f"Scraping URL: {url}...")
    video_url = get_samehadaku_video(url)

    if not video_url:
        print("Gagal mendapatkan link video. Pastikan URL benar atau coba episode lain.")
        return

    print(f"Link Video Ditemukan: {video_url}")

    if 'gofile.io/d/' in video_url:
        print("Mencoba resolve Gofile URL...")
        video_url = resolve_gofile_url(video_url)
        print(f"Resolved URL: {video_url}")

    choice = input("Putar di MPV? (y/n): ").lower()
    if choice == 'y':
        play_video(video_url)
    else:
        print("Selesai.")

if __name__ == "__main__":
    main()
