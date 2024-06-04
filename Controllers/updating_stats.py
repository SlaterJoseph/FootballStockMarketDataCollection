from flask import request, Blueprint
from Services.Collection import weekly_stats_collection, seasonal_stats_collection
from datetime import date

update_stats_bp = Blueprint('update_stats', __name__)


@update_stats_bp.route('/update_weekly', methods=['POST'])
def update_weekly_stats():
    data = request.json
    teams = set(data.get('teams'))
    season = int(data.get('season'))
    week = int(data.get('season'))
    weekly_stats_collection.update_weekly_stats(teams, season, week)


@update_stats_bp.route('/update_seasonal', methods=['POST'])
def update_seasonal_stats():
    data = request.json
    season = int(data.get('season'))
    seasonal_stats_collection.get_new_season(season)


@update_stats_bp.route('/full_reset', methods=['POST'])
def full_reset():
    """
    This is for completely resting the CSVs
    :return: None
    """
    year = date.today().year - 1
    years = [year, year - 1, year - 2]
    weekly_stats_collection.collect_weekly_initially(years)
    seasonal_stats_collection.build_csv_seasonal(years)
