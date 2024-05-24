from flask import request, jsonify, Blueprint
from Services.Collection.weekly_stats_collection import update_weekly_stats
from Services.Collection.seasonal_stats_collection import update_seasonal_stats

update_stats = Blueprint('update_stats', __name__)


@update_stats.route('/update_weekly', methods=['POST'])
def update_weekly_stats():
    pass


@update_stats.route('/update_seasonal', methods=['POST'])
def update_seasonal_stats():
    pass


@update_stats.route('/update_depth_charts', methods=['POST'])
def update_depth_charts():
    pass

