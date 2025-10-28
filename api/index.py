@"
# api/index.py
# Vercel Python Functions entrypoint. Imports Flask app from joystick_poc/app.py
from joystick_poc.app import app  # 'app' must be defined in joystick_poc/app.py
"@ | Out-File -Encoding utf8 .\api\index.py

git add .\api\index.py
git commit -m "Route Vercel to joystick_poc Flask app"
