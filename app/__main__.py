from flask import Flask
from Controllers.updating_stats import update_stats_bp

app = Flask(__name__)
app.register_blueprint(update_stats_bp)

if __name__ == '__main__':
    app.run(debug=True)
