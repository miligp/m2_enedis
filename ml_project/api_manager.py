import subprocess
import time
import os
import sys
import socket
import requests
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CloudAPIManager:
    """Gestionnaire d'APIs optimisé pour le cloud"""
    
    def __init__(self):
        self.is_cloud = self._detect_cloud_environment()
        logger.info(f"Environnement détecté: {'Cloud' if self.is_cloud else 'Local'}")
    
    def _detect_cloud_environment(self):
        """Détecte si on est dans un environnement cloud"""
        cloud_indicators = [
            'RENDER' in os.environ,
            'HEROKU' in os.environ,
            'AWS_' in os.environ,
            'CLOUD_' in os.environ,
            'DYNO' in os.environ  # Heroku
        ]
        return any(cloud_indicators)
    
    def check_api_health(self, port):
        """Vérifie la santé d'une API"""
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_apis_if_needed(self):
        """Démarre les APIs seulement en environnement local"""
        if self.is_cloud:
            logger.info("Mode cloud: les APIs externes ne sont pas démarrées")
            return []
        
        # Code pour démarrer les APIs en local seulement
        processes = []
        try:
            # Votre code de démarrage d'APIs local ici
            logger.info("Démarrage des APIs en mode local...")
        except Exception as e:
            logger.error(f"Erreur démarrage APIs: {e}")
        
        return processes
    
    def get_api_status(self):
        """Retourne le statut des APIs"""
        if self.is_cloud:
            return {
                'environment': 'cloud',
                'apis_available': False,
                'message': 'Mode simulation activé pour le cloud'
            }
        else:
            # Vérifier le statut des APIs en local
            api_5000 = self.check_api_health(5000)
            api_5001 = self.check_api_health(5001)
            
            return {
                'environment': 'local',
                'apis_available': api_5000 or api_5001,
                'api_5000': api_5000,
                'api_5001': api_5001
            }

# Instance globale
api_manager = CloudAPIManager()