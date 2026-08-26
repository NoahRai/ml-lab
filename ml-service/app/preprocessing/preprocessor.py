import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class DataPreprocessor:
    """Fits tabular transformations on training features and reuses them for test features."""

    def __init__(self) -> None:
        self.transformer: ColumnTransformer | None = None

    def fit_transform(self, features: pd.DataFrame):
        numeric_columns = features.select_dtypes(include="number").columns.tolist()
        categorical_columns = [column for column in features.columns if column not in numeric_columns]
        transformers = []
        if numeric_columns:
            transformers.append(
                ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric_columns)
            )
        if categorical_columns:
            transformers.append(
                (
                    "categorical",
                    Pipeline(
                        [
                            ("imputer", SimpleImputer(strategy="most_frequent")),
                            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                        ]
                    ),
                    categorical_columns,
                )
            )
        self.transformer = ColumnTransformer(transformers=transformers, remainder="drop")
        return self.transformer.fit_transform(features)

    def transform(self, features: pd.DataFrame):
        if self.transformer is None:
            raise RuntimeError("DataPreprocessor must be fit before transforming test data.")
        return self.transformer.transform(features)

    def get_feature_names(self) -> list[str]:
        if self.transformer is None:
            raise RuntimeError("DataPreprocessor must be fit before reading feature names.")
        return [name.replace("numeric__", "").replace("categorical__", "") for name in self.transformer.get_feature_names_out()]
