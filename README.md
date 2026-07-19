# Jeedom API pour Home Assistant

Intégration personnalisée Home Assistant permettant d'importer une sélection
d'équipements Jeedom via l'API HTTP locale.

> Version expérimentale : commencez avec quelques équipements essentiels.

## Fonctionnalités actuelles

- Configuration depuis l'interface Home Assistant.
- Sélection des équipements Jeedom à importer.
- Modification de cette sélection dans **Configurer**.
- Lumières marche/arrêt avec luminosité.
- Interrupteurs marche/arrêt.
- Volets avec ouverture, fermeture, arrêt et position.
- Boutons pour les actions Jeedom restantes.
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


## Équipements BLEA

Les thermomètres et hygromètres du plugin Jeedom BLEA sont reconnus spécialement.
Pour un équipement tel que `Bureau`, Home Assistant crée notamment :

- un capteur de température en °C ;
- un capteur d'humidité en % ;
- un capteur de batterie en % ;
- un capteur RSSI en dBm ;
- un ou plusieurs diagnostics de connectivité.

La température et l'humidité restent les mesures principales de l'appareil.
La batterie, le RSSI et la connectivité sont rangés dans la section diagnostics.

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

## Réparer une mise à jour BLEA

Après installation de la version 0.3.1 :

1. Redémarrez complètement Home Assistant.
2. Ouvrez **Paramètres → Appareils et services → Jeedom API → Configurer**.
3. Laissez les équipements BLEA cochés puis enregistrez.
4. Attendez le rechargement de l'intégration.
5. Ouvrez l'appareil BLEA et vérifiez également la section **Entités désactivées**.

Pour diagnostiquer :

```yaml
logger:
  default: warning
  logs:
    custom_components.jeedom_api: debug
    custom_components.jeedom_api.sensor: debug
```

Les journaux doivent contenir une ligne comme :

```text
Équipement Jeedom Bureau (blea): 6 capteur(s) info détecté(s)
```

