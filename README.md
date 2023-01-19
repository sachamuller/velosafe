# velosafe
[![Linter Actions Status](https://github.com/sachamuller/velosafe/actions/workflows/lint.yml//badge.svg?branch=main)](https://github.com/sachamuller/velosafe/actions)

Un projet d'étude de l'impact d'installations cycliste sur l'accidentologie à vélo.

## Installation

Ce package nécessite `python >= 3.10`.
* Clonez le repo.
* Exécutez `pip install .` depuis la racine du projet pour l'installer avec ses dépendances.

## Quickstart
* Commencez par télécharger les données et générer les features: `mkdir data && python -m velosafe datagen ./data`. L'opération peut prendre plusieurs minutes à se terminer.
* Exécutez le code du notebook présent dans `examples` pour mieux comprendre comment utiliser le package.

## Contribuer

Pour contribuer du code à ce projet:

* Installez [`poetry`](https://python-poetry.org/docs/#installation), notre outil de gestion de dépendances.
* Clonez le repo.
* Installez le projet et ses dépendances: `poetry install`.
  
Pour ajouter des dépendances au projet, utilisez `poetry add` (par exemple `poetry add numpy`).
