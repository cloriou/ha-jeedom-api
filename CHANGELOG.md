# Journal des modifications

## 0.3.0

- Prise en charge dédiée des thermomètres et hygromètres Jeedom BLEA.
- Détection de la température avec la classe Home Assistant `temperature`.
- Détection de l'humidité avec la classe `humidity`.
- Détection du niveau de batterie avec la classe `battery`.
- Détection du RSSI BLEA avec la classe `signal_strength` et l'unité `dBm`.
- Les états `Present` et `Present OctoPi` deviennent des diagnostics de connectivité.
- Batterie, RSSI et connectivité sont classés comme diagnostics afin de garder
  température et humidité au premier plan.
- Métadonnées BLEA améliorées : modèle et fabricant lorsque disponibles.
- Ajout d'attributs de diagnostic avec l'identifiant équipement, le plugin et l'objet Jeedom.

## 0.2.0

- Ajout des interrupteurs, volets et boutons.
- Nouveau moteur commun de découverte.

## 0.1.1

- Lumières, capteurs et capteurs binaires.
- Sélection des équipements et options de polling.
