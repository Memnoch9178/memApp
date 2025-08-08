# memApp

Application modulaire pour la gestion de mémoire et d’installation automatique.

## Installation

Voir la documentation dans `docs/` pour les instructions détaillées.

## Structure
- `src/` : code source principal
- `tests/` : tests unitaires et d’intégration
- `docs/` : documentation, mémoire projet, changelog, ADR

## Configuration
Copiez `.env.example` en `.env` et adaptez les variables selon votre environnement.

## Convention de configuration YAML

Chaque fichier de configuration doit regrouper les paramètres par section, selon le service ou module concerné :

```yaml
memApp:
  watchdog:
    enabled: true
    interval: 5
  database:
    host: localhost
    port: 5432
```

- Les sections racines correspondent au nom du service/module/plugin.
- Tous les paramètres d’un élément sont regroupés dans sa section.
- Cette convention s’applique à tous les fichiers `config.yml` du projet.
