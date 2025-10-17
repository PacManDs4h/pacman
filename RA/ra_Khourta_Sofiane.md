3/10 :
    - Lecture du livre, compréhension et assimilation des caractèristiques des différents algo
      de génération
    - Penchant pour un algo de génération de maze parfait, comme recursive backtracking ou Wilson,
      en modifiant ensuite l'algo pour ajouter des cycles, des wrap-arrounds et la cage des fantômes
      pour rendre le labyrinthe plus 'pacman-like'

10/10 : 
    - Choix de l'algo parfait recursive backtracking
    - Base du code de l'algorithme en python, pris depuis : https://inventwithpython.com/recursion/chapter11.html
    - Ajout de cycles, suppression des culs-de-sac, symétrie
    - Création de tests connexité, pourcentage de cellules vides par rapport aux murs
    - Réflexion sur les données du json

17/10 : 
    - Création du json avec les données :
        - largeur, hauteur, pourcentage connexité, nombres cellules vides, nombres cellules mur,
          tableau 2d du maze, nombres cycles, nombres "wrap-arrounds, 
          nombres connexion milieu (espace vide dù à la symétrie)
