# Jeedom API pour Home Assistant

Intégration personnalisée Home Assistant permettant d'importer une sélection
d'équipements Jeedom via l'API HTTP locale.

> Version expérimentale : commencez avec quelques équipements essentiels.

## Fonctionnalités actuelles

- Configuration depuis l'interface Home Assistant.
- Sélection des équipements Jeedom à importer.
- Modification de cette sélection dans **Configurer**.
- Lumières marche/arrêt avec luminosité.
- Capteurs numériques et texte.
- Capteurs binaires.
- Rafraîchissement groupé via `fullData`.
- Intervalle de rafraîchissement configurable.

## Installation avec HACS

1. Publiez ce dossier dans un dépôt GitHub **public**.
2. Dans HACS, ouvrez **Intégrations**.
3. Ouvrez le menu en haut à droite puis **Dépôts personnalisés**.
4. Ajoutez l'adresse du dépôt.
5. Sélectionnez la catégorie **Intégration**.
6. Installez **Jeedom API**.
7. Redémarrez Home Assistant.
8. Ajoutez l'intégration depuis **Paramètres → Appareils et services**.

## Configuration

Saisissez l'URL locale de Jeedom, par exemple :

```text
http://jeedom-master.local
```

Puis saisissez une clé API Jeedom valide et sélectionnez les équipements à importer.

## Mise à jour de la sélection

Dans Home Assistant :

```text
Paramètres → Appareils et services → Jeedom API → Configurer
```

## Journaux détaillés

```yaml
logger:
  default: warning
  logs:
    custom_components.jeedom_api: debug
```

## Sécurité

Ne publiez jamais une clé API dans GitHub, un ticket ou un journal. L'intégration
demande la clé durant la configuration et aucune clé n'est incluse dans ce dépôt.

## État du projet

Les prochaines plateformes prévues sont `switch`, `button`, `cover`, `number`
et `select`.
