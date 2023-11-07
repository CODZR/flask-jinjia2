from manage import render_template
from app import app, db

@app.errorhandler(404)
def page_not_found(error="Page Not Found"):
    return render_template('404.html', error=error), 404