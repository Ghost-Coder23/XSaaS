#!/bin/bash
echo "==============================="
echo "  EduCore Setup"
echo "==============================="

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
echo "Edit .env with your settings if needed."

python manage.py migrate
python manage.py collectstatic --noinput

echo ""
echo "Creating superuser (EduCore platform admin)..."
python manage.py createsuperuser

echo ""
echo "==============================="
echo "  Setup complete!"
echo "  Run: source venv/bin/activate && python manage.py runserver"
echo "  Then visit: http://localhost:8000"
echo "==============================="
