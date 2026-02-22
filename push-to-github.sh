#!/bin/bash
# Script pour pousser le projet Revit Agents vers GitHub
# Usage: ./push-to-github.sh <URL_DU_REPO>

set -e

REPO_URL=$1

if [ -z "$REPO_URL" ]; then
    echo "❌ Erreur: URL du repo GitHub manquante"
    echo ""
    echo "Usage:"
    echo "  ./push-to-github.sh https://github.com/ton-user/revit-bim-agents.git"
    echo ""
    echo "Ou avec token:"
    echo "  ./push-to-github.sh https://TOKEN@github.com/ton-user/revit-bim-agents.git"
    exit 1
fi

echo "🚀 Préparation du projet Revit BIM Agents pour GitHub"
echo "============================================================"
echo ""

# Vérifie si git est initialisé
if [ ! -d ".git" ]; then
    echo "📦 Initialisation du repo git..."
    git init
    git branch -M main
else
    echo "✅ Repo git déjà initialisé"
fi

echo ""
echo "📋 Fichiers à pousser:"
git ls-files 2>/dev/null || find . -type f -not -path './.git/*' -not -path './__pycache__/*' | head -20

echo ""
echo "🔗 Configuration du remote..."
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

echo ""
echo "💾 Ajout des fichiers..."
git add -A

# Commit
if git diff --cached --quiet; then
    echo "⚠️  Rien à committer (déjà à jour)"
else
    echo "📝 Commit..."
    git commit -m "Initial commit: Revit BIM Agents

- Orchestrateur multi-agents
- 5 agents spécialisés (Beam, Column, Wall, Roof, Floor)
- Extension pyRevit complète
- Intégration OpenClaw"
fi

echo ""
echo "🚀 Push vers GitHub..."
if git push -u origin main; then
    echo ""
    echo "✅ SUCCÈS ! Projet poussé sur GitHub"
    echo ""
    echo "🔗 URL: $REPO_URL"
    echo ""
    echo "Prochaines étapes:"
    echo "1. Va sur GitHub pour voir ton repo"
    echo "2. Ajoute une description et des tags"
    echo "3. Partage le lien avec ton équipe"
else
    echo ""
    echo "❌ ERREUR lors du push"
    echo ""
    echo "Solutions possibles:"
    echo "1. Vérifie l'URL du repo"
    echo "2. Vérifie ton token d'authentification"
    echo "3. Vérifie ta connexion internet"
    echo ""
    echo "Pour utiliser un token GitHub:"
    echo "  ./push-to-github.sh https://TOKEN@github.com/user/repo.git"
fi

echo ""
echo "============================================================"
echo "Terminé."
