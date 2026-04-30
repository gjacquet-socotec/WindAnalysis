#!/bin/bash
# Script pour redémarrer le backend FastAPI (Linux/Mac/Git Bash)

echo "=== Redémarrage du backend FastAPI ==="

# Arrêter les processus Python existants sur le port 8000
echo "Arrêt des processus sur le port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 2

# Lancer le backend
echo "Démarrage du backend..."
python main.py > /tmp/fastapi_restart.log 2>&1 &
BACKEND_PID=$!

# Attendre que le backend soit prêt
echo "Attente du démarrage (3 secondes)..."
sleep 3

# Vérifier le health check
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✓ Backend démarré avec succès (PID: $BACKEND_PID)"
    echo "  - API: http://localhost:8000"
    echo "  - Docs: http://localhost:8000/docs"
    echo "  - Logs: /tmp/fastapi_restart.log"
else
    echo "✗ Échec du démarrage du backend"
    echo "Logs:"
    tail -20 /tmp/fastapi_restart.log
    exit 1
fi
