# Kit de démarrage Mintlify

Utilisez le kit de démarrage pour déployer votre documentation et la préparer à la personnalisation.

Cliquez sur le bouton vert **Utiliser ce modèle** en haut de ce dépôt pour copier le kit de démarrage Mintlify. Le kit de démarrage contient des exemples de

- Pages de guide
- Navigation
- Personnalisations
- Pages de référence d’API
- Utilisation de composants populaires

**[Suivez le guide complet de démarrage rapide](https://starter.mintlify.com/quickstart)**

## Rédaction assistée par IA

Configurez votre outil de codage IA pour travailler avec Mintlify :

```bash
npx skills add https://mintlify.com/docs
```

Cette commande installe la skill de documentation de Mintlify pour vos outils IA configurés, tels que Claude Code, Cursor, Windsurf et autres. La skill inclut une référence des composants, des normes de rédaction et des conseils de workflow.

Consultez les [guides des outils IA](/ai-tools) pour une configuration propre à chaque outil.

## Développement

Installez la [CLI Mintlify](https://www.npmjs.com/package/mint) pour prévisualiser localement les modifications apportées à votre documentation. Pour l’installer, utilisez la commande suivante :

```
npm i -g mint
```

Exécutez la commande suivante à la racine de votre documentation, là où se trouve votre fichier `docs.json` :

```
mint dev
```

Consultez votre prévisualisation locale à l’adresse `http://localhost:3000`.

## Publication des modifications

Installez notre application GitHub depuis votre [tableau de bord](https://dashboard.mintlify.com/settings/organization/github-app) pour propager les modifications de votre dépôt vers votre déploiement. Les modifications sont automatiquement déployées en production après leur envoi vers la branche par défaut.

## Besoin d’aide ?

### Dépannage

- Si votre environnement de développement n’est pas en cours d’exécution : exécutez `mint update` pour vous assurer de disposer de la version la plus récente de la CLI.
- Si une page se charge en affichant une erreur 404 : assurez-vous d’exécuter la commande dans un dossier contenant un fichier `docs.json` valide.

### Ressources
- [Documentation Mintlify](https://mintlify.com/docs)
