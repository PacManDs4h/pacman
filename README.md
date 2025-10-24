# pacman

khourta Sofiane
el moussaoui Adel
andre Mathis


Lancement du serveur en local avec docker :
```docker build -t maze-server .```
```docker run -p 8080:8080 maze-server```

lien du web-service :
https://pacman-kw23.onrender.com/generate

On peut préciser ces paramètres dans la génération du labyrinthe lors de la requète,
si non précisés, elles auront les valeurs de base mises entre parenthèses :
- height (19)
- width (39)
- nb_cycles (10)
- num_tunnels_wrap (2)
- num_tunnels_centre (5) # Reliant les deux parties symétriques

Il faut rajouter un '?' après le lien, et séparer les paramètres avec des '&'.
Exemple :
```curl https://pacman-kw23.onrender.com/generate?height=23&width=40&nb_cycles=5```
