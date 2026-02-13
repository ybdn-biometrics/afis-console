# AFIS Console - Tri Automatique FAED

Outil développé par YBDN Biometrics pour automatiser le tri des rapports de signalisation FAED (PDF).

## 📋 Description

Ce script analyse la première page des rapports PDF pour vérifier la mention "Homonymes".

- Si la mention est suivie de "non" (sur la même ligne) → Le fichier est déplacé dans `Pas_d_homonyme/`.
- Sinon (ou en cas de doute) → Le fichier est déplacé dans `Homonymes_detectes/` pour une vérification manuelle.

Le projet inclut une interface graphique (GUI) moderne et fonctionne également en ligne de commande (CLI).

## 🚀 Installation

1. Assurez-vous d'avoir **Python 3.10+** installé.
2. Clonez ce dépôt.
3. Installez les dépendances (et le package en mode développement) :

```bash
pip install -r requirements.txt
pip install -e .
```

## 🖥️ Utilisation

### Interface Graphique (Recommandé)

Lancez l'application avec :

```bash
python start_app.py
```
ou si le package est installé :
```bash
afis-console
```

Une fenêtre s'ouvrira pour vous permettre de sélectionner le dossier contenant les PDF à trier.

### Ligne de Commande

Vous pouvez également utiliser le script directement dans un terminal :

```bash
python start_app.py /chemin/vers/dossier/pdfs
```

## 📦 Compilation (Exécutable)

### Via GitHub Actions (Automatique)

Chaque push sur la branche `main` déclenche automatiquement une GitHub Action qui :
1. Lit la version depuis `src/afis_console/__init__.py`
2. Compile l'application en **fichier unique** (PyInstaller `--onefile`) pour **Windows (.exe)** et **Linux**
3. Crée une **Release GitHub** avec un tag `vX.Y.Z` et les exécutables en téléchargement

Pour publier une nouvelle release, il suffit de **modifier la version** dans `src/afis_console/__init__.py` et de pusher sur `main`.
Les releases sont disponibles sur la [page Releases](../../releases) du dépôt.

### Compilation Locale

Pour créer l'exécutable sur votre machine :

```bash
python build_app.py
```

L'exécutable sera généré dans le dossier `dist/`.

## 🛠️ Architecture du Projet

Le projet suit une structure modulaire standard :

- `src/afis_console/core/` : Logique métier (tri des PDF).
- `src/afis_console/gui/` : Interface graphique (CustomTkinter).
- `src/afis_console/main.py` : Point d'entrée principal.
- `tests/` : Tests unitaires.

## 📝 Licence

Propriété exclusive de **YBDN Biometrics**.
Ce logiciel est protégé par le droit d'auteur (Code de la Propriété Intellectuelle, France).

L'utilisation de ce logiciel est soumise aux termes du fichier [LICENSE](./LICENSE).
Toute redistribution, modification ou usage commercial sans autorisation écrite est interdite.

© 2026 YBDN Biometrics. Tous droits réservés.
