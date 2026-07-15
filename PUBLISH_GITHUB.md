# Publication sur GitHub

## Méthode depuis le navigateur

1. Connectez-vous à GitHub.
2. Créez un dépôt public nommé `ha-jeedom-api`.
3. Ne demandez pas à GitHub de créer un README ou une licence.
4. Ouvrez le dépôt vide puis choisissez **uploading an existing file**.
5. Glissez-déposez tout le contenu de ce dossier, y compris :
   - `.github`
   - `custom_components`
   - `hacs.json`
   - `README.md`
   - `LICENSE`
6. Validez avec **Commit changes**.
7. Remplacez `VOTRE_COMPTE` dans :
   `custom_components/jeedom_api/manifest.json`.
8. Créez une release GitHub portant le tag `0.1.1`.

## Installation comme dépôt HACS personnalisé

Dans HACS :

1. **Intégrations**
2. Menu en haut à droite
3. **Dépôts personnalisés**
4. URL : `https://github.com/VOTRE_COMPTE/ha-jeedom-api`
5. Catégorie : **Intégration**
6. **Ajouter**, puis installer l'intégration.
