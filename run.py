import os
import sys

# Activate the virtual environment
activate_this = os.path.join(os.path.dirname(__file__), '.venv', 'Scripts', 'activate_this.py')
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), {'__file__': activate_this})

from webapp import create_app
from db import create_table

if __name__ == '__main__':
    create_table()
    app = create_app()
    app.run(debug=True)
