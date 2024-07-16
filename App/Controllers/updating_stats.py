import os

from flask import request, Blueprint, jsonify
from datetime import date
import yaml

from App.Services import player_collection, weekly_stats_collection, seasonal_stats_collection, \
    team_defense_collection_seasonal
from App.Controllers.utils.functions import yaml_lookup
from App.Controllers.utils.exceptions import AuthorizationError

update_stats_bp = Blueprint('update_stats', __name__)


@update_stats_bp.route('/update_weekly', methods=['POST'])
def update_weekly_stats():
    """
    Updates all CSV stats weekly
    :return: JSON message, return code
    """
    try:
        data = request.json
        password = yaml_lookup('password.weekly_update')
        required_keys = ['teams', 'season', 'week', 'password']

        if not data and not all(key in data for key in required_keys):
            raise ValueError('Invalid JSON payload')

        elif password != str(data.get('password')):
            raise AuthorizationError('Failed Authentication')

        else:
            teams = set(data.get('teams'))
            season = int(data.get('season'))
            week = int(data.get('week'))
            weekly_stats_collection.update_weekly_stats(teams, season, week)

            response = {'message': 'Processed successfully'}
            return_code = 201

    # Incorrect JSON
    except ValueError as e:
        response = {'error': str(e)}
        return_code = 400

    # Incorrect Password
    except AuthorizationError as e:
        response = {'error': str(e)}
        return_code = 401

    # Other Exceptions
    except Exception:
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
    password = yaml_lookup('password.seasonal_update')

    try:
        if not data and 'season' not in data:
            raise ValueError('Invalid JSON payload')

        elif password != str(data.get('password')):
            raise AuthorizationError('Failed Authentication')

        else:
            season = int(data.get('season'))
            seasonal_stats_collection.get_new_season(season)
            team_defense_collection_seasonal.new_seasonal_team_defense(season)

            response = {'message': 'Processed successfully'}
            return_code = 201

    # Incorrect Json
    except ValueError as e:
        response = {'error': str(e)}
        return_code = 400

    # Incorrect Password
    except AuthorizationError as e:
        response = {'error': str(e)}
        return_code = 401

    except Exception:
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
    password = yaml_lookup('password.full_reset')

    try:
        # Make sure JSON is valid
        if not data or 'password' not in data:
            raise ValueError('Invalid JSON or missing required key')

        # Commit to full reset
        if password == str(data.get('password')):
            year = date.today().year - 1
            years = [year, year - 1, year - 2]
            weekly_stats_collection.collect_weekly_initially(years)
            seasonal_stats_collection.build_csv_seasonal(years)
            team_defense_collection_seasonal.initial_seasonal_team_defense_seasonally(years)
            response = {'message': 'Processed successfully'}
            return_code = 201

        else:
            raise AuthorizationError('Failed Authentication')

    # Invalid Json
    except ValueError as e:
        response = {'error': str(e)}
        return_code = 400

    # Incorrect Password
    except AuthorizationError as e:
        response = {'error': str(e)}
        return_code = 401

    # Catch other exceptions
    except Exception as e:
        response = {'error': 'Internal Server Error'}
        return_code = 500

    return jsonify(response), return_code


@update_stats_bp.route('/update_players', methods=['POST'])
def update_players():
    """
    Function which updates the player CSV
    :return:
    """

    data = request.json
    password = yaml_lookup('password.update_players')

    try:
        if not data or 'password' not in data:
            raise ValueError('Invalid JSON or missing required key')

        elif password != str(data.get('password')):
            raise AuthorizationError('Failed Authorization')

        else:
            player_collection.create_player_csv()
            response = {'message': 'Processed successfully'}
            return_code = 201

    except ValueError as e:
        response = {'error': str(e)}
        return_code = 400

    except AuthorizationError as e:
        response = {'error': str(e)}
        return_code = 401

    except Exception:
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
    week: ##,
    password: "password"
}

Seasonal
{
    season: 20##
    password: "password"
}

Full Reset
{
    password: "password"
}

Update Players
{
    password: "password"
}
"""
