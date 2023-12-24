from flask import jsonify, current_app, request
from app.api import bp
from config import Config
import pandas as pd

@bp.route('/latest_fires', methods=['GET'])
def get_latest_fires():
    parquet_file_path = current_app.config['PARQUET_FILE_PATH']
    df = pd.read_parquet(parquet_file_path)

    df['acq_date'] = pd.to_datetime(df['acq_date'])
    max_date = df['acq_date'].max()
    df = df[df['acq_date'] >= max_date]
    # Remove low confidence data if any
    df = df[~(df['confidence'] == 'l')]
    latest_fires = df.sort_values(by=['acq_date', 'acq_time'], ascending=True)
    latest_fires['acq_date'] = latest_fires['acq_date'].dt.strftime('%Y-%m-%d')

    result = latest_fires.to_dict(orient='records')
    return jsonify(result)

@bp.route('/fires_by_date', methods=['GET'])
def get_fires_by_date():
    requested_date = request.args.get('date')

    if not requested_date:
        return jsonify({'error': 'Date parameter is missing'}), 400

    try:
        requested_date = pd.to_datetime(requested_date, format='%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD'}), 400

    parquet_file_path = current_app.config['PARQUET_FILE_PATH']
    df = pd.read_parquet(parquet_file_path)

    df['acq_date'] = pd.to_datetime(df['acq_date'])
    selected_fires = df[df['acq_date'] == requested_date]
    # Remove low confidence data if any
    selected_fires = selected_fires[~(selected_fires['confidence'] == 'l')]
    selected_fires = selected_fires.sort_values(by=['acq_time'], ascending=True)
    selected_fires['acq_date'] = selected_fires['acq_date'].dt.strftime('%Y-%m-%d')

    result = selected_fires.to_dict(orient='records')
    return jsonify(result)