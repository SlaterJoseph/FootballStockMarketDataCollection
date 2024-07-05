from flask import request, Blueprint, jsonify
from Services.Collection import weekly_stats_collection, seasonal_stats_collection, team_defense_collection_seasonal
from datetime import date
import yaml

update_stats_bp = Blueprint('update_stats', __name__)


@update_stats_bp.route('/update_weekly', methods=['POST'])
def update_weekly_stats():
    """
    Updates all CSV stats weekly
    :return: JSON message, return code
    """
    try:
        data = request.json
        required_keys = ['teams', 'season', 'week']
        if not data and not all(key in data for key in required_keys):
            raise ValueError('Invalid JSON payload')
        else:
            teams = set(data.get('teams'))
            season = int(data.get('season'))
            week = int(data.get('week'))
            weekly_stats_collection.update_weekly_stats(teams, season, week)

            response = {'message': 'Processed successfully'}
            return_code = 200

    except ValueError as e:
        response = {'error': str(e)}
        return_code = 422

    except Exception as e:
        response = {'error': 'Internal Server Error'}
        return_code = 500

    return jsonify(response), return_code


@update_stats_bp.route('/update_seasonal', methods=['POST'])
def update_seasonal_stats():
    """
    Updates all seasonal stats at the end of a season
    :return: JSON message, return code
    """
    data = request.json
    try:
        if not data and 'season' not in data:
            raise ValueError('Invalid JSON payload')

        else:
            season = int(data.get('season'))
            seasonal_stats_collection.get_new_season(season)
            team_defense_collection_seasonal.new_seasonal_team_defense(season)

            response = {'message': 'Processed successfully'}
            return_code = 200

    except ValueError as e:
        response = {'error': str(e)}
        return_code = 422

    except Exception as e:
        response = {'error': 'Internal Server Error'}
        return_code = 500

    return jsonify(response), return_code


@update_stats_bp.route('/full_reset', methods=['POST'])
def full_reset():
    """
    This is for completely resting the CSVs
    :return: JSON message, return code
    """
    data = request.json
    yaml_file = '../../../properties.yaml'
    with open(yaml_file, 'r') as f:
        yaml_data = yaml.safe_load(f)

    try:
        # Make sure JSON is valid
        if not data or 'full_reset_password' not in data:
            raise ValueError('Invalid JSON or missing required key')

        # Commit to full reset
        if yaml_data['full_reset_password'] == str(data.get('full_reset_password')):
            year = date.today().year - 1
            years = [year, year - 1, year - 2]
            weekly_stats_collection.collect_weekly_initially(years)
            seasonal_stats_collection.build_csv_seasonal(years)
            team_defense_collection_seasonal.initial_seasonal_team_defense_seasonally(years)
            response = {'message': 'Processed successfully'}
            return_code = 200
        # Incorrect password
        else:
            response = {'error': 'Unauthorized request'}
            return_code = 403

    # Invalid Json
    except ValueError as e:
        response = {'error': str(e)}
        return_code = 422

    # Catch other exceptions
    except Exception as e:
        response = {'error': 'Internal Server Error'}
        return_code = 500

    return jsonify(response), return_code


"""
Sample JSON
Weekly
{
    teams: {
        teams
    }, 
    season: 20##,
    week: ##
}

Seasonal
{
    season: 20##
}

Full Reset
{
    full_reset_password: "password"
}
"""