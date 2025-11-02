import subprocess
import time
import os
import sys
import socket
import threading
import requests

def is_port_in_use(port):
    """Vérifie si un port est déjà utilisé"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            return s.connect_ex(('0.0.0.0', port)) == 0
    except:
        return False

def is_api_ready(port):
    """Vérifie si l'API est vraiment prête"""
    try:
        response = requests.get(f"http://0.0.0.0:{port}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_single_api(api_file, port):
    """Démarre une API spécifique - Version cloud compatible"""
    try:
        api_path = os.path.join(os.path.dirname(__file__), api_file)
        
        print(f"Démarrage de {api_file} sur le port {port}...")
        
        # Démarrer le processus
        process = subprocess.Popen([
            sys.executable, api_file  # Utiliser le fichier directement
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Attendre le démarrage
        start_time = time.time()
        max_wait_time = 120  # 2 minutes pour le cloud
        
        while time.time() - start_time < max_wait_time:
            if is_port_in_use(port) and is_api_ready(port):
                print(f"SUCCES: {api_file} démarré sur le port {port}")
                return process
            time.sleep(3)
            print(f"En attente de {api_file}... {int(time.time() - start_time)}s")
        
        print(f"TIMEOUT: {api_file} après {max_wait_time} secondes")
        return process
        
    except Exception as e:
        print(f"ERREUR: Démarrage de {api_file}: {e}")
        return None

def start_apis():
    """Démarre les APIs de prédiction - Version cloud"""
    print("Démarrage des APIs en arrière-plan...")
    
    processes = []
    
    # Démarrer API Consommation (5000)
    if not is_api_ready(5000):
        process_5000 = start_single_api("API_Lineaire_Reg.py", 5000)
        if process_5000:
            processes.append(process_5000)
    
    # Démarrer API DPE (5001)  
    if not is_api_ready(5001):
        process_5001 = start_single_api("API_Random_Forest.py", 5001)
        if process_5001:
            processes.append(process_5001)
    
    return processes

def stop_apis(processes):
    """Arrête les processus API"""
    for process in processes:
        try:
            process.terminate()
        except:
            pass