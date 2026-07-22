# Journal des modifications

## 0.5.3

- Initialisation explicite des attributs de classe des capteurs.
- Le code ne lit plus `_attr_device_class` avant de l'avoir affecté.
- Ajout d'un marqueur de version dans les journaux :
  `Chargement de jeedom_api.sensor version 0.5.3`.
- Correction défensive de toute occurrence résiduelle de `__attr_device_class`.

## 0.5.2

- Correction de la faute de frappe sur `_attr_device_class`.
