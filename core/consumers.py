# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime, timezone

class CuisineConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accepter la connexion WebSocket
        await self.accept()

    async def disconnect(self, close_code):
        # Se déconnecter
        pass

    async def receive(self, text_data):
        # Recevoir un message du client
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')

        # Exemple : envoyer les informations des tournées à la connexion
        if message == 'load_tournees':
            await self.send_tournees_data()

    async def send_tournees_data(self):
        # Simuler une récupération des tournées et envoyer les données en temps réel
        now = datetime.now(timezone.utc)
        
        # Exemple de données
        tournees_commandes = [
            {
                'tournee_nom': 'A',
                'heure_cloture': now.isoformat(),
                'recently_closed': True,
                'commandes': [
                    {'commande_id': 1, 'articles': [{'nom': 'Plat 1', 'quantite': 2}]},
                    {'commande_id': 2, 'articles': [{'nom': 'Plat 2', 'quantite': 1}]}
                ],
            },
            # Ajouter d'autres tournées...
        ]

        # Envoyer les données des tournées au client
        await self.send(text_data=json.dumps({
            'tournees_commandes': tournees_commandes
        }))
