"""
Responsibilities:
1. Load the trained XGBoost model.
2. Load the SAME preprocessing pipeline used during training.
3. Look up product/category information from the inventory database.
4. Validate incoming forecasting inputs.
5. Transform raw features using the saved encoder.
6. Return numerical demand predictions.

"""

from pathlib import Path
from typing import Optional
import json

import joblib
import pandas as pd
import xgboost as xgb
from db.session import SessionLocal

MODEL_DIR = Path("models")

PREPROCESSOR_PATH = MODEL_DIR / "demand_preprocessor.joblib"
MODEL_PATH = MODEL_DIR / "demand_xgboost.json"
METADATA_PATH = MODEL_DIR / "demand_model_metadata.json"



class ForecastService:
    """Demand forecasting service."""

    def __init__(self) -> None:
        if not PREPROCESSOR_PATH.exists():
            raise FileNotFoundError(
                f"Forecast preprocessor not found: {PREPROCESSOR_PATH}"
            )

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Forecast model not found: {MODEL_PATH}"
            )

        if not METADATA_PATH.exists():
            raise FileNotFoundError(
                f"Model metadata not found: {METADATA_PATH}"
            )

        self.preprocessor = joblib.load(PREPROCESSOR_PATH)

        self.model = xgb.XGBRegressor()
        self.model.load_model(MODEL_PATH)

        with open(METADATA_PATH, "r") as file:
            self.metadata = json.load(file)

        one_hot_encoder = (
            self.preprocessor.named_transformers_["categorical"]
        )

        categorical_features = self.metadata["categorical_features"]

        self.valid_categories = {
            feature: {str(value) for value in values}
            for feature, values in zip(
                categorical_features,
                one_hot_encoder.categories_,
            )
        }
