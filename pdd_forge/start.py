#!/usr/bin/env python3
"""
PDD Forge - Tek Tıkla Başlatıcı
Bu script, gerekli bağımlılıkları kontrol eder, kurar ve uygulamayı başlatır.
"""

import os
import sys
import subprocess
import threading
import time
import socket
from pathlib import Path

# Renkli çıktı için ANSI kodları
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {text} ==={Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def run_command(command, cwd=None, shell=False):
    """Komutu çalıştır ve çıktığı anlık göster"""
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in process.stdout:
            print(line, end='')
        process.wait()
        return process.returncode == 0
    except Exception as e:
        print_error(f"Hata: {e}")
        return False

def install_dependencies():
    print_header("Bağımlılıklar Kontrol Ediliyor")
    
    # Python bağımlılıkları
    print_info("Python bağımlılıkları yükleniyor...")
    if not run_command([sys.executable, "-m", "pip", "install", "-e", ".[dev]"]):
        print_error("Python bağımlılıkları yüklenirken hata oluştu!")
        return False
    print_success("Python bağımlılıkları hazır.")

    # Node.js bağımlılıkları
    frontend_path = Path(__file__).parent / "frontend"
    if frontend_path.exists():
        print_info("Frontend bağımlılıkları yükleniyor (bu ilk seferde uzun sürebilir)...")
        # npm install sessizce çalışsın ama hata varsa görelim
        if not run_command(["npm", "install"], cwd=frontend_path):
            print_error("Frontend bağımlılıkları yüklenirken hata oluştu! (Node.js yüklü mü?)")
            return False
        print_success("Frontend bağımlılıkları hazır.")
    
    return True

def start_backend():
    print_header("Backend Başlatılıyor")
    print_info("Backend http://localhost:8000 adresinde çalışacak...")
    
    def run_backend():
        run_command([sys.executable, "-m", "uvicorn", "backend.app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
    
    thread = threading.Thread(target=run_backend, daemon=True)
    thread.start()
    
    # Backend'in ayağa kalkmasını bekle
    print_info("Backend başlatılıyor, lütfen bekleyin...")
    for _ in range(30):  # 30 saniye bekle
        if not is_port_in_use(8000):
            time.sleep(1)
        else:
            print_success("Backend başarıyla başlatıldı!")
            return True
    
    print_error("Backend başlatılamadı.")
    return False

def start_frontend():
    print_header("Frontend Başlatılıyor")
    print_info("Frontend tarayıcınızda açılacak...")
    
    frontend_path = Path(__file__).parent / "frontend"
    if not frontend_path.exists():
        print_error("Frontend klasörü bulunamadı!")
        return False

    # Frontend'i başlat (bloklayıcı, ana thread'de kalsın ki uygulama kapanmasın)
    print_info("Vite sunucusu başlatılıyor...")
    run_command(["npm", "run", "dev"], cwd=frontend_path)

def main():
    print_header("PDD FORGE - Başlatıcı")
    print("Uygulamaya hoş geldiniz! Sistem hazırlanıyor...")
    
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    
    # 1. Bağımlılıkları Yükle
    if not install_dependencies():
        print_error("Kurulum başarısız. Lütfen hata mesajlarını kontrol edin.")
        sys.exit(1)
    
    # 2. Backend'i Başlat (Arka planda)
    if not start_backend():
        sys.exit(1)
        
    # 3. Frontend'i Başlat (Ön planda)
    start_frontend()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nUygulama kapatıldı. Hoşçakalın!")
    except Exception as e:
        print_error(f"Beklenmeyen hata: {e}")
        sys.exit(1)
