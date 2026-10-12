print("hi")
print("test")
print("bonjour")

# Test de l'API MusicBrainz : 
# recherche d'un artiste par son nom et affichage du premier résultat
import requests

url = "https://musicbrainz.org/ws/2/artist/"
params = {"query": "Ninho", "fmt": "json"}
headers = {"User-Agent": "projet-python (alicia.hamdini@ensae.fr)"}

r = requests.get(url, params=params, headers=headers)
data = r.json()
print(data["artists"][0]["name"])