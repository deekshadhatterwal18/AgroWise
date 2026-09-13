import os

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

from xgboost import XGBRegressor


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "Crop_Yield_Data.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "model"
)

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


df = pd.read_csv(DATASET_PATH)


print("=" * 60)
print("DATASET INFORMATION")
print("=" * 60)

print("Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:", df.duplicated().sum())


features = [
    "Crop",
    "Season",
    "State",
    "Area",
    "Annual_Rainfall",
    "Fertilizer",
    "Pesticide",
    "Avg_Temperature",
    "Max_Temperature",
    "Min_Temperature"
]

target = "Yield"


X = df[features]
y = df[target]


valid_rows = y.notna() & (y >= 0)

X = X.loc[valid_rows]
y = y.loc[valid_rows]


print("\nSamples after cleaning:", len(X))


categorical_features = [
    "Crop",
    "Season",
    "State"
]

numerical_features = [
    "Area",
    "Annual_Rainfall",
    "Fertilizer",
    "Pesticide",
    "Avg_Temperature",
    "Max_Temperature",
    "Min_Temperature"
]


preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        ),
        (
            "numerical",
            "passthrough",
            numerical_features
        )
    ]
)


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


X_train_processed = preprocessor.fit_transform(
    X_train
)

X_test_processed = preprocessor.transform(
    X_test
)


rf_model = RandomForestRegressor(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(
    X_train_processed,
    y_train
)

rf_predictions = rf_model.predict(
    X_test_processed
)


rf_mae = mean_absolute_error(
    y_test,
    rf_predictions
)

rf_rmse = mean_squared_error(
    y_test,
    rf_predictions
) ** 0.5

rf_r2 = r2_score(
    y_test,
    rf_predictions
)


print("\n" + "=" * 60)
print("RANDOM FOREST REGRESSOR")
print("=" * 60)

print(f"MAE:  {rf_mae:.4f}")
print(f"RMSE: {rf_rmse:.4f}")
print(f"R²:   {rf_r2:.4f}")


xgb_model = XGBRegressor(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)

xgb_model.fit(
    X_train_processed,
    y_train
)

xgb_predictions = xgb_model.predict(
    X_test_processed
)


xgb_mae = mean_absolute_error(
    y_test,
    xgb_predictions
)

xgb_rmse = mean_squared_error(
    y_test,
    xgb_predictions
) ** 0.5

xgb_r2 = r2_score(
    y_test,
    xgb_predictions
)


print("\n" + "=" * 60)
print("XGBOOST REGRESSOR")
print("=" * 60)

print(f"MAE:  {xgb_mae:.4f}")
print(f"RMSE: {xgb_rmse:.4f}")
print(f"R²:   {xgb_r2:.4f}")


if rf_rmse <= xgb_rmse:

    best_model = rf_model
    best_model_name = "Random Forest"
    best_mae = rf_mae
    best_rmse = rf_rmse
    best_r2 = rf_r2

else:

    best_model = xgb_model
    best_model_name = "XGBoost"
    best_mae = xgb_mae
    best_rmse = xgb_rmse
    best_r2 = xgb_r2


model_path = os.path.join(
    MODEL_DIR,
    "yield_model.pkl"
)

joblib.dump(
    best_model,
    model_path
)


preprocessor_path = os.path.join(
    MODEL_DIR,
    "yield_preprocessor.pkl"
)

joblib.dump(
    preprocessor,
    preprocessor_path
)


encoded_feature_names = (
    preprocessor
    .get_feature_names_out()
)


feature_groups = {}


for original_feature in features:

    related_features = []

    for index, encoded_name in enumerate(
        encoded_feature_names
    ):

        clean_name = encoded_name

        if clean_name.startswith(
            "categorical__"
        ):

            clean_name = clean_name.replace(
                "categorical__",
                "",
                1
            )

        elif clean_name.startswith(
            "numerical__"
        ):

            clean_name = clean_name.replace(
                "numerical__",
                "",
                1
            )

        if (
            clean_name == original_feature
            or clean_name.startswith(
                original_feature + "_"
            )
        ):

            related_features.append(
                index
            )

    feature_groups[
        original_feature
    ] = related_features


encoded_importances = (
    best_model.feature_importances_
)


global_feature_importance = {}


for feature, indices in feature_groups.items():

    importance = sum(
        encoded_importances[index]
        for index in indices
    )

    global_feature_importance[
        feature
    ] = float(importance)


total_importance = sum(
    global_feature_importance.values()
)


if total_importance > 0:

    global_feature_importance = {
        feature: importance / total_importance
        for feature, importance
        in global_feature_importance.items()
    }


metadata = {
    "features": features,
    "target": target,
    "model_name": best_model_name,
    "mae": best_mae,
    "rmse": best_rmse,
    "r2": best_r2,
    "encoded_feature_names": encoded_feature_names.tolist(),
    "feature_groups": feature_groups,
    "global_feature_importance": global_feature_importance
}


metadata_path = os.path.join(
    MODEL_DIR,
    "yield_model_metadata.pkl"
)

joblib.dump(
    metadata,
    metadata_path
)


print("\n" + "=" * 60)
print("GLOBAL FEATURE IMPORTANCE")
print("=" * 60)


sorted_importance = sorted(
    global_feature_importance.items(),
    key=lambda item: item[1],
    reverse=True
)


for feature, importance in sorted_importance:

    print(
        f"{feature}: {importance * 100:.2f}%"
    )


print("\n" + "=" * 60)
print("FINAL MODEL")
print("=" * 60)

print("Selected model:", best_model_name)
print(f"MAE:  {best_mae:.4f}")
print(f"RMSE: {best_rmse:.4f}")
print(f"R²:   {best_r2:.4f}")

print("\nSaved files:")
print(model_path)
print(preprocessor_path)
print(metadata_path)