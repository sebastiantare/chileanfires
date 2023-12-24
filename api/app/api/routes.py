from flask import jsonify, current_app
from app.api import bp
from config import Config
import pandas as pd

@bp.route('/latest_fires', methods=['GET'])
def get_latest_fires():
    parquet_file_path = current_app.config['PARQUET_FILE_PATH']
    # Assuming your Parquet file has a 'fires' table
    df = pd.read_parquet(parquet_file_path)

    # Get the latest fires, adjust as per your data structure
    latest_fires = df.sort_values(by=['acq_date'], ascending=False).head(10)

    # Convert to JSON and return
    result = latest_fires.to_dict(orient='records')
    return jsonify(result)
