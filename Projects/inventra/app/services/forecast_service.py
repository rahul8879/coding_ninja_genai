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
from db.models import Inventory

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

    def _validate_category(
        self,
        feature: str,
        value: str,
    ) -> Optional[str]:
        valid_values = self.valid_categories.get(feature, set())

        if value not in valid_values:
            return (
                f"Unknown {feature} '{value}'. "
                f"Model was trained on: {sorted(valid_values)}"
            )

        return None

    def predict(
        self,
        sku: str,
        region: str,
        weather_condition: str,
        temperature: float,
        rainfall: float,
        humidity: float,
        month: int,
        day_of_week: int,
        is_weekend: int,
    ) -> dict:
        """
        Predict demand for a SKU.

        SKU is NOT used directly as an ML feature.
        It is used as a business identifier to retrieve the
        product category from the inventory database.
        """

        if not 1 <= month <= 12:
            return {"error": "month must be between 1 and 12."}

        if not 0 <= day_of_week <= 6:
            return {"error": "day_of_week must be between 0 and 6."}

        if is_weekend not in (0, 1):
            return {"error": "is_weekend must be either 0 or 1."}

        db = SessionLocal()

        try:
            item = (
                db.query(Inventory)
                .filter(Inventory.sku == sku)
                .first()
            )

            if item is None:
                return {"error": f"Unknown SKU '{sku}'."}

            product_name = item.name
            category = item.category

        finally:
            db.close()

        for feature, value in [
            ("category", category),
            ("region", region),
            ("weather_condition", weather_condition),
        ]:
            error = self._validate_category(feature, value)

            if error:
                return {"error": error}

        model_input = pd.DataFrame(
            [
                {
                    "category": category,
                    "region": region,
                    "weather_condition": weather_condition,
                    "temperature": float(temperature),
                    "rainfall": float(rainfall),
                    "humidity": float(humidity),
                    "month": int(month),
                    "day_of_week": int(day_of_week),
                    "is_weekend": int(is_weekend),
                }
            ]
        )

        encoded_input = self.preprocessor.transform(model_input)

        prediction = self.model.predict(encoded_input)[0]

        predicted_qty = max(0.0, float(prediction))

        return {
            "sku": sku,
            "product_name": product_name,
            "category": category,
            "region": region,
            "weather_condition": weather_condition,
            "temperature": float(temperature),
            "rainfall": float(rainfall),
            "humidity": float(humidity),
            "month": int(month),
            "day_of_week": int(day_of_week),
            "is_weekend": int(is_weekend),
            "predicted_qty": round(predicted_qty, 2),
            "model": "XGBoost",
        }


_forecast_service_instance: Optional[ForecastService] = None


def get_forecast_service() -> ForecastService:
    """Return one shared ForecastService instance."""

    global _forecast_service_instance

    if _forecast_service_instance is None:
        _forecast_service_instance = ForecastService()

    return _forecast_service_instance

