from flask import request, jsonify, Blueprint
from Services.Collection import weekly_stats_collection, seasonal_stats_collection
from datetime import date

update_stats = Blueprint('update_stats', __name__)


@update_stats.route('/update_weekly', methods=['POST'])
def update_weekly_stats():
    data = request.json
    teams = set(data.get('teams'))
    season = int(data.get('season'))
    week = int(data.get('season'))
    weekly_stats_collection.update_weekly_stats(teams, season, week)


@update_stats.route('/update_seasonal', methods=['POST'])
def update_seasonal_stats():
    pass


@update_stats.route('/update_depth_charts', methods=['POST'])
def update_depth_charts():
    pass


@update_stats.route('/full_reset', methods=['POST'])
def full_reset():
    """
    This is for completely resting the CSVs
    :return: None
    """
    year = date.today().year - 1
    years = [year, year - 1, year - 2]
    weekly_stats_collection.collect_weekly_initially(years)
    seasonal_stats_collection.build_csv_seasonal(years)
