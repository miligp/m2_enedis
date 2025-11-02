Write-Host "🚀 Déploiement Docker M2.ENEDIS" -ForegroundColor Green

if (-not (Test-Path "random_forest_dpe_final_weighted.joblib")) {
    Write-Host "❌ ERREUR: random_forest_dpe_final_weighted.joblib non trouvé" -ForegroundColor Red
    exit 1
}

Write-Host "📦 Construction des images Docker..." -ForegroundColor Cyan
docker-compose build

Write-Host "🐳 Lancement des services..." -ForegroundColor Cyan
docker-compose up -d

Start-Sleep -Seconds 15

Write-Host "✅ Déploiement réussi!" -ForegroundColor Green
Write-Host "🌐 Streamlit: http://localhost:8501" -ForegroundColor Cyan
Write-Host "🌐 API Forest: http://localhost:5001" -ForegroundColor Cyan  # ← CORRIGÉ (5001)
Write-Host "🌐 API Linear: http://localhost:5000" -ForegroundColor Cyan  # ← CORRIGÉ (5000)