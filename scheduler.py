import time
import subprocess
from datetime import datetime

def run_etl_batch(batch_number):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{current_time}] === MEMULAI BATCH KE-{batch_number} ===")
    
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Mengeksekusi Data Scraping...")
        subprocess.run(["python", "scraper.py"], cwd="Data Scraping/src", check=True)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Mengeksekusi Data Preprocessing...")
        subprocess.run(["python", "preprocessor.py"], cwd="Data Scraping/src", check=True)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Mengeksekusi Data Storing...")
        subprocess.run(["python", "storing.py"], cwd="Data Storing/src", check=True)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] === BATCH KE-{batch_number} SELESAI ===\n")
    
    except subprocess.CalledProcessError as e:
        print(f"Terjadi kesalahan pada eksekusi script: {e}")

print("Memulai Automated Scheduling ETL...\n")

run_etl_batch(1)

print("Menunggu 2 menit untuk batch selanjutnya...")
time.sleep(120) 

run_etl_batch(2)

print("Automated Scheduling Selesai.")