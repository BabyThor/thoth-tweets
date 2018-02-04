from flask import Flask

import settings

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('map.html', google_api_key=settings.GOOGLE_API_KEY)