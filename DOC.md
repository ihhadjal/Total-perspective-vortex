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

