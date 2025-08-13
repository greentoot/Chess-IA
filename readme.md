# ♟ Chess-IA

Un projet Python combinant plusieurs approches d’intelligence artificielle pour jouer aux échecs ou à des variantes simplifiées, avec une interface graphique en **pygame**.

## 📌 Fonctionnalités

- **Moteur Minimax** classique avec élagage alpha-bêta (dossier `IAminimax`)
- **Agent Q-Learning** pour apprendre par renforcement (`agent_qlearning.py`)
- **Environnements Minichess** (`env_minichess.py` et `env_minichessv2.py`) pour tester plus rapidement les algorithmes
- **Interface graphique** en Pygame pour jouer contre l’IA ou observer ses parties
- **Plusieurs modes de jeu** :
  - Humain vs IA
  - IA vs IA
  - Minichess expérimental

## 📂 Structure du projet

```
Chess-IA/
│
├── IAminimax/              # Moteur d'échecs basé sur Minimax
├── assets/                 # Images des pièces et ressources graphiques
│
├── agent_qlearning.py      # Agent IA utilisant Q-learning
├── env_minichess.py        # Version simple du jeu pour entraînement rapide
├── env_minichessv2.py      # Variante améliorée du minichess
│
├── play.py                 # Lancer une partie standard avec IA
├── play_huma.py            # Mode joueur humain contre IA
├── playv2.py               # Variante alternative de partie
│
└── .gitattributes
```

## 🚀 Installation

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/greentoot/Chess-IA.git
   cd Chess-IA
   ```

2. **Installer les dépendances** :
   ```bash
   pip install pygame
   ```

## 🎮 Utilisation

### Lancer une partie standard avec IA Minimax :
```bash
python IAminimax/IA_chess.py
```

### Lancer l'entrainement de L'IA contre elle même :
```bash
python play.py
```

### Tester le mode minichess :
```bash
python play_huma.py```
ou


## ⚙ Paramètres intéressants

- **Profondeur de recherche** (`ai_depth`) pour ajuster la force de l’IA Minimax.
- **Épisodes et taux d’apprentissage** pour le Q-Learning.
- **Choix du joueur humain** (Blanc ou Noir) dans les scripts `play_*.py`.

## 🧠 Algorithmes implémentés

- **Minimax avec élagage alpha-bêta** : cherche le meilleur coup en explorant les possibilités à profondeur fixe.
- **Q-Learning** : apprentissage par renforcement en utilisant un environnement réduit (minichess).

