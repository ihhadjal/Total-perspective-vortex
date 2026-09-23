COMPRENDRE LE DATA SET

le dataset contient des mesures d'ondes cerebrales provennates de personnes aux quelles ont leur a dit
de bouger/penser de bouger leur mains ou pieds en rapport a un symbole sur un ecran devant eux.

donc les resultats ce sont des mesures (ondes) avec des labels (etiquettes) indicant les moments ou les
sujets de l'experience ont fait une action


ETAPES DU PROJET

1-> parser le data-set avec la librairie "MNE"

2 -> implementer l'algorithme "dimensionality reduction"

3-> utiliser l'objet "pipeline" de scikit-learn

4-> classer un flux de donne en "temps reel"


ETAPE 1: PARSER LE DATA SET

notre dataset est le EEG Motor/Imagery dataset de PhysioNet, il contient les EEG de 109 sujets,
enregistrees avec 64 electrodes a 160hz, chaque sujet effectue 14 runs

immaginons un EEG comme ceic:

temps ---------------------------------------------------->

Fp1 :  ~~~~~~~/\~~~~\~~~~/\~~~~~~
Fp2 :  ~~\~~~~~~/\~~~~~~\~~~~~~~~
C3  :  ~~~~~/\~~~~~~~~/\~~~~~~~~~
C4  :  ~~\~~~~~~~~/\~~~~~~~~~~~~~
...
64 électrodes

a chaque instant les 64 electrodes donnent une mesure electrique

donc mathematiquement un enregistrement ressemble a une matrice

              temps

channel 1     x x x x x x x x ...
channel 2     x x x x x x x x ...
channel 3     x x x x x x x x ...
...
channel 64    x x x x x x x x ...

avec une frequence de 160hz, ce qui veut dire que 160 veleurs sont produites par un 
electrode toutes les secondes

donc une seconde de mesure represente deja 64 x 160 = 10 240 mesures


EXPLICATION DES RUNS

chaque sujet fait 14 runs:

| Runs      | Ce que fait la personne                           |
| --------- | ------------------------------------------------- |
| 1         | repos, yeux ouverts                               |
| 2         | repos, yeux fermés                                |
| 3, 7, 11  | bouge réellement main gauche vs main droite       |
| 4, 8, 12  | **imagine** main gauche vs main droite            |
| 5, 9, 13  | bouge réellement les deux mains vs les deux pieds |
| 6, 10, 14 | **imagine** les deux mains vs les deux pieds      |


les enregistrements contiennet egalement des annotations:

T0: repos
T1: mouvement de type1
T2: mouvement de type2

par contre T1 et T2 ne signifient pas toujours la meme chose:

pour un run gauche/drote: t1 = main gauche, t2 = main droite

pour un run main/pieds: t1 = deux mains, t2 = deux pieds

donc IL FAUT INTERPRETER T1 ET T2 EN FONCTION DU RUN


MOTOR EXECUTION vs MOTOR IMAGERY

le dataset contien deux types de donnees:

le motor execution -> on dit au sujet de bouger sa main ou son pieds (il effectue le mouvement)

le motor imagery -> on dit au sujet de immaginer de bouger sa main ou son pieds (le mouvement n'est pas effectue)

lors du motor imagery le mouvement nest pas effectue, pourtant l'activite cerebrale lie au mouvement change quand meme


RAW vs EPOCH vs EVENT

raw = enregistremnet EEG continu:

0 sec                                      120 sec
|----------------------------------------------|

EEG EEG EEG EEG EEG EEG EEG EEG EEG EEG EEG EEG

pas encore decoupe

Event: pendant l'enregistrement on marque certain moments:

0s        10s       20s       30s
|----------|---------|---------|

           T1        T0        T2

Epoch: une epoch est un morceau de l'eeg autour dun evenement:

                 T1
                  ↓
EEG ------------------------------------

              |-------|
                epoch

par exemple: prendre les 4 secondes d'eeg qui suivenet chaque apparition de T1 ou T2


QUEST CE QUE UN CHANNEL

un channel correspond a un signal provenant dune electrode EEG

ici on a donc 64 signaux enregistrees au meme temps


QUEST CE QUE UN SAMPLE

un sample est une mesure dun signal a un moment donee



le run dure 125 secondes, mais pendant tout ce temps differentres actions sont faites
pas que un mouvement de la main ou du oieds mais une combinaison, c'est donc pour ca que les annotations
rentrent en jeu


chaque electrode est mesuree 160 fois / s

donc l'intervale entre deux samples est 1 / 160 = 0.00625s = 6.25ms


QUEST CE QUE LE HIGPASS FILTER

un signal EEG est constitue de plusieures frequences superposees (oscillation lente + moyenne + rapide + bruit)

le higpass filter va enlever les signaux en dessous dune certaine valeur


DANS NOTRE DATASET POUR LENTRAINEMENT

actuellement nous avons 125s d'enregistrement, lire la totalite de ces 125 secondes pour entrainer le model serait inutile

ce que on veut faire c'est extraire touts les signaux des moments dans l'enregistremnet quand quelque chose se passe

par exemple: 

                    T1
                      ↓
EEG ──────────────────────────────────

                   |------|
                   morceau

on recupere ce morceau et il deviendra une epoch

puis

epoch 1 → T1 → gauche
epoch 2 → T2 → droite
epoch 3 → T1 → gauche
epoch 4 → T2 → droite

et la ca commencera a ressembleer a un vrai dataset de ML

X                  y

EEG epoch 1      gauche
EEG epoch 2      droite
EEG epoch 3      gauche
EEG epoch 4      droite


COMPRENDRE LES FREQUENCES DANS NOTRE DATASET

un signal dune electrode ressemble a ca

C3

    /\      /\      /\
___/  \____/  \____/  \___


si un motif complet se repete 10 fois en une seconde on dit que le signal a une frequence de 10Hz donc 10 oscillations
par seconde

malheuresment notre EEG nest pas compose dune seule frequence mais de plusieurs conceptuellement il y a:

singal lent

signal moyen

signal rapide

bruit

toutes ces frequences sont reproduite dans le raw, notre but dans un premier temps est de "nettoyer" le raw
pour recuperer seulement les frequences qui nous sont vraiment utiles


en neuroscience on distingue les bandes comme:

Delta     ~ 0.5 - 4 Hz
Theta     ~ 4 - 8 Hz
Alpha     ~ 8 - 13 Hz
Beta      ~ 13 - 30 Hz


pour notre projet deux bandes sont interessantes:

le rythme Mu: 8-13HZ -> il est particulierement present autours des zones sensorimotrices

le rythme Beta: 13-30Hz -> egalement lie a l'activite motrice


lorsque une perosnne fait/immagine un mouvemnet la puissance de ces rythmes peut changer autours du
cortex moteur

donc la plage qui nous interesse est de 8 a 30hz car ce sont ces plages la qui sont actives autours des zones
sensorimotrices


GRAPHE PSD -> graphe pour voir quelles frequences ont plus de puissance dans le EEG

ce graphe nous sert notamment a choisir quelles bandes frequentielles ont doit garder pour le filtrage
si on voit par exemple que les basses frequences sont celles qui ont le plus de puissance, on va filtrer pour recuperer
que les plages necessaires (ici 8 a 30hz)


{'T0': 1, 'T1': 2, 'T2': 3}

1 = T0 = repos
2 = T1 = main gauche
3 = T2 = main droite