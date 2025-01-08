# Projet Django - Transcription en Temps Réel avec Whisper

Ce projet implémente un service de transcription en temps réel en utilisant le modèle Whisper d'OpenAI. Il permet de transcrire des fichiers audio en texte en temps réel, grâce à une API RESTful construite avec Django. L'application est conçue pour être flexible, scalable et facile à intégrer dans des environnements de production.

## Fonctionnalités

- Transcription en temps réel de fichiers audio
- Utilisation du modèle Whisper pour la conversion audio -> texte
- Interface simple pour démarrer une transcription et récupérer les résultats

## Prérequis

Avant de commencer, vous devez installer et configurer les éléments suivants :

- **Python 3.9+** : Assurez-vous que Python est installé sur votre machine.
- **Django** : Le framework web utilisé pour ce projet.
- **Whisper** : Le modèle de transcription développé par OpenAI.
- **Dépendances supplémentaires** : Pour gérer l'audio, la gestion des API et d'autres fonctions.

## Installation

1. **Clonez le dépôt** :

   Clonez ce projet sur votre machine locale en utilisant Git :

   ```bash
   git clone https://github.com/Benjamin-Poutout/whisper-transcription-french-django.git
   cd whisper-transcription-french-django
   ```

2. **Installer les bibliothèques nécesaires** :

   ```bash
   pip install -r requirements.txt
   ```
