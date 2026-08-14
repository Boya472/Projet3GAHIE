# Projet3GAHIE — Setup rapide

Ces scripts aident à installer les dépendances du projet sur Windows.

Prerequis:
- Python 3.8+ installé.
- Il est fortement recommandé d'utiliser un virtualenv (`python -m venv venv`) puis d'activer l'environnement.

Scripts fournis:
- `env_setup.bat` — installe `requirements.txt` en utilisant `python -m pip` (double-cliquez ou exécutez depuis CMD/PowerShell).
- `setup.ps1` — même fonction pour PowerShell, accepte un paramètre optionnel `-PythonPath` si vous voulez forcer un exécutable Python (ex: `-PythonPath C:\Python312\python.exe`).

Exemples:
```powershell
# Avec l'interpréteur par défaut (PowerShell)
.\setup.ps1

# En précisant le chemin vers Python
.\setup.ps1 -PythonPath "C:\Users\Lenovo\AppData\Local\Programs\Python\Python312\python.exe"
```

```cmd
:: Depuis l'invite de commandes
env_setup.bat
```

Après installation:
```bash
python manage.py migrate
python manage.py runserver
```

Conseils:
- Préférez `python -m pip` plutôt que `pip` pour éviter d'installer les paquets dans un autre interpréteur.
- Si `python` n'est pas dans le `PATH`, fournissez le chemin complet avec `-PythonPath` pour `setup.ps1`.
