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

－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－

Automatisation de la mise à jour de la documentation utilisateur via l'IA
Description du besoin

Actuellement, la documentation utilisateur (UserDoc.md) est maintenue manuellement. Ce processus est chronophage et sujet aux erreurs ou aux oublis, en particulier lorsque de nouvelles fonctionnalités sont ajoutées ou que des comportements existants sont modifiés via des Merge Requests (MR). Il est nécessaire d'automatiser ce processus pour garantir que la documentation soit toujours synchronisée avec l'état actuel du code, améliorant ainsi sa fiabilité et sa pertinence pour les utilisateurs et les développeurs.

Objectif

L'objectif principal est de créer un système automatisé qui analyse les changements de code dans chaque Merge Request et met à jour la documentation utilisateur en conséquence. Ce système utilisera un modèle d'intelligence artificielle pour générer le nouveau contenu, assurant ainsi que la documentation reste précise et à jour avec une intervention humaine minimale.

Valeur métier

Impact utilisateur : Les développeurs et les utilisateurs auront accès à une documentation constamment à jour et précise, ce qui réduira la confusion, facilitera l'intégration des nouveaux membres et améliorera l'utilisation globale du produit.

Impact métier : Réduction significative de l'effort manuel consacré à la maintenance de la documentation, libérant ainsi du temps pour les développeurs qui pourront se concentrer sur des tâches à plus forte valeur ajoutée. Amélioration de la qualité et de la maintenabilité du code en intégrant la documentation comme une partie intégrante du cycle de vie du développement.

Métriques attendues :

Réduction du temps passé sur les mises à jour manuelles de la documentation.

Augmentation de la corrélation entre le contenu de UserDoc.md et les fonctionnalités du code.

Spécifications fonctionnelles

En tant que développeur, je veux qu'un script soit déclenché automatiquement par le pipeline de CI/CD GitLab à chaque nouvelle Merge Request.

En tant que développeur, je veux que ce script puisse lire l'intégralité du code source du projet.

En tant que développeur, je veux que le script puisse lire le "diff" (les modifications) de la Merge Request en cours.

En tant que développeur, je veux que le script envoie ce contexte de code (source complet + diff) à un modèle d'IA (Gemini 2.5 Pro) pour générer une documentation utilisateur mise à jour.

En tant que développeur, je veux que le script remplace entièrement le contenu du fichier UserDoc.md par la réponse générée par l'IA.

Parcours utilisateur
Parcours principal

Un développeur crée et pousse une Merge Request sur GitLab.

Le pipeline de CI/CD de GitLab se déclenche et exécute le script updateDocUser.js.

Le script collecte le code source complet du projet, le "diff" de la MR et la clé d'API nécessaire.

Le script envoie une requête à l'API de Google AI Studio avec les données collectées et un prompt prédéfini.

Le script reçoit en retour un texte complet représentant la nouvelle documentation.

Le script écrase le contenu du fichier UserDoc.md avec le texte reçu.

Le fichier UserDoc.md mis à jour est inclus dans les changements de la Merge Request ou dans un commit ultérieur.

Parcours alternatifs

Si la Merge Request ne contient aucune modification de code (ex: modification de la documentation uniquement), le script s'exécute quand même. Le modèle d'IA devrait idéalement déterminer qu'aucune mise à jour de la documentation fonctionnelle n'est nécessaire.

Règles métier

Le script doit être un fichier Node.js autonome nommé updateDocUser.js.

Le script et le fichier UserDoc.md doivent être situés à la racine du projet.

Le script ne doit pas réutiliser le service GeminiApi.executor.ts existant et doit gérer ses propres appels HTTP.

Le contenu entier du fichier UserDoc.md doit être remplacé à chaque exécution. Aucune mise à jour partielle ne doit être effectuée.

La clé d'API pour Google AI Studio doit être gérée de manière sécurisée, en étant fournie comme une variable d'environnement dans le contexte de la CI/CD.

Critères d'acceptation

✅ Lorsque le pipeline CI/CD s'exécute, le script updateDocUser.js est lancé avec succès.

✅ Le script appelle correctement l'API de Google AI Studio avec la charge utile attendue (code source + diff + prompt).

✅ Le fichier UserDoc.md est entièrement remplacé par le contenu textuel reçu du modèle d'IA.

✅ Le script gère les erreurs d'API (ex: clé invalide, erreur du modèle) de manière appropriée, en enregistrant une erreur dans les logs de la CI/CD sans nécessairement faire échouer tout le pipeline.

Cas d'usage et scénarios de test
Cas nominal

Scénario : Une MR avec des modifications de code est créée.

Données d'entrée : Code source, diff de la MR, clé API valide.

Résultat attendu : Le script s'exécute, appelle l'IA et met à jour UserDoc.md avec un nouveau contenu pertinent.

Cas limites

Scénario : Une MR ne contient que des modifications dans des fichiers de commentaires ou de documentation (autre que UserDoc.md).

Résultat attendu : Le script s'exécute, et le contenu de UserDoc.md est potentiellement inchangé ou légèrement ajusté par l'IA.

Cas d'erreur

Scénario : La clé d'API Google AI Studio est invalide ou manquante.

Résultat attendu : Le script échoue et affiche un message d'erreur clair dans les logs de la CI/CD.

Scénario : Le modèle d'IA retourne une erreur ou une réponse vide.

Résultat attendu : Le script enregistre l'erreur et ne modifie pas le fichier UserDoc.md existant.

Interface utilisateur (mockups/wireframes)

Non applicable. Cette fonctionnalité est un processus backend automatisé sans interface utilisateur directe.

Dépendances fonctionnelles

Une configuration du pipeline CI/CD de GitLab est nécessaire pour exécuter le script updateDocUser.js lors des événements de Merge Request.

Une clé d'API valide pour Google AI Studio, avec les droits d'accès au modèle Gemini 2.5 Pro, doit être disponible en tant que variable d'environnement dans le pipeline.
  
