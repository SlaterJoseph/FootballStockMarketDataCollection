from flask import Flask, current_app, abort
from Controllers.updating_stats import update_stats_bp
from functools import wraps

app = Flask(__name__)
app.register_blueprint(update_stats_bp)


def debug_only(f):
    """
    Decorator for debug only routes
    :param f: The function to make a debug route
    :return:
    """
    @wraps(f)
    def wrapped(**kwargs):
        if not current_app.debug:
            abort(404)

        return f(**kwargs)

    return wrapped


@app.route('/')
@debug_only
def testing():
    """
    Routing to main page to make sure the service is running
    :return:
    """
    return 'Collection Up and Running'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
