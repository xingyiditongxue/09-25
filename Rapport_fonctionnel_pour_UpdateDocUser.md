QUOI : Créer un script Node.js nommé updateDocUser.js qui met à jour automatiquement la documentation utilisateur (UserDoc.md) en se basant sur les modifications d'une Merge Request, en utilisant le modèle d'IA Gemini 2.5 Pro.

OÙ : Le script updateDocUser.js et le fichier de documentation UserDoc.md seront situés à la racine du projet oxa-pocket.

COMMENT : Le script, destiné à être exécuté dans un environnement de CI/CD GitLab, doit suivre les étapes suivantes :

Accepter les entrées : Le script doit être conçu pour recevoir trois informations de l'environnement d'exécution :

Le contenu complet du code source du projet (basé sur le fichier allCodeFile.txt fourni).

Le "diff" des modifications de la Merge Request en cours.

Une clé d'API pour Google AI Studio.

Appel à l'IA : Le script doit implémenter sa propre logique pour effectuer un appel HTTP à l'API de Google AI Studio, sans réutiliser le code de GeminiApi.executor.ts.

Construction du Prompt : Il doit envoyer un prompt unique au modèle Gemini2.5-Pro qui combine le code source complet, le "diff" de la MR, et un prompt prédéfini (représenté par un placeholder).

Mise à jour du fichier : Le script doit récupérer la réponse textuelle complète du modèle Gemini et remplacer intégralement le contenu du fichier UserDoc.md par cette réponse.
