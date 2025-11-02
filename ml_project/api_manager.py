import subprocess
import time
import os
import sys
import socket
import threading
import requests

def is_port_in_use(port):
    """Verifie si un port est deja utilise"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(('localhost', port)) == 0

def is_api_ready(port):
    """Verifie si l'API est vraiment prete en testant la route health"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_single_api(api_file, port):
    """Demarre une API specifique"""
    try:
        api_path = os.path.join(os.path.dirname(__file__), api_file)
        
        print(f"Demarrage de {api_file} sur le port {port}...")
        
        # Demarrer le processus avec encodage UTF-8 pour Windows
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        process = subprocess.Popen([
            sys.executable, api_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, env=env)
        
        # Lire la sortie en temps reel
        def read_output(pipe, pipe_name):
            for line in pipe:
                print(f"[{api_file} {pipe_name}] {line.strip()}")
        
        # Demarrer les threads pour lire stdout et stderr
        stdout_thread = threading.Thread(target=read_output, args=(process.stdout, "STDOUT"), daemon=True)
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr, "STDERR"), daemon=True)
        stdout_thread.start()
        stderr_thread.start()
        
        # ATTENDRE PLUS LONGTEMPS - 60 secondes maximum
        start_time = time.time()
        max_wait_time = 60
        
        while time.time() - start_time < max_wait_time:
            if is_port_in_use(port):
                # Le port est ouvert, mais verifions si l'API est vraiment prete
                if is_api_ready(port):
                    print(f"SUCCES: {api_file} demarre sur le port {port} (temps: {time.time() - start_time:.1f}s)")
                    return process
                else:
                    print(f"EN COURS: {api_file} - Port {port} ouvert, attente initialisation...")
            else:
                print(f"EN COURS: {api_file} - Attente demarrage sur le port {port}...")
            
            time.sleep(2)
        
        print(f"TIMEOUT: {api_file} apres {max_wait_time} secondes")
        return process
        
    except Exception as e:
        print(f"ERREUR: Demarrage de {api_file}: {e}")
        return None

def start_apis():
    """Demarre les APIs de prediction"""
    print("Demarrage des APIs en arriere-plan...")
    
    processes = []
    
    # Demarrer les deux APIs en parallele
    if not is_api_ready(5000):
        process_5000 = start_single_api("API_Lineaire_Reg.py", 5000)
        if process_5000:
            processes.append(process_5000)
    else:
        print("API Consommation (5000) deja demarree")
    
    if not is_api_ready(5001):
        process_5001 = start_single_api("API_Random_Forest.py", 5001)
        if process_5001:
            processes.append(process_5001)
    else:
        print("API DPE (5001) deja demarree")
    
    return processes

def stop_apis(processes):
    """Arrete les processus API"""
    print("Arret des APIs...")
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=10)
            print(f"Processus {process.pid} arrete")
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"Processus {process.pid} force a s'arreter")
        except Exception as e:
            print(f"Erreur arret processus: {e}")

def monitor_apis():
    """Surveillance legere des APIs"""
    def monitor():
        while True:
            time.sleep(30)
            if not is_api_ready(5000):
                print("API 5000 non detectee")
            if not is_api_ready(5001):
                print("API 5001 non detectee")
    
    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()
    print("Surveillance des APIs activee")