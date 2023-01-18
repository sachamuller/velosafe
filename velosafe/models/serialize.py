import pickle
from pathlib import Path

from sklearn.base import BaseEstimator


def save_model(model: BaseEstimator, file: str | Path):
    """
    Serialize a model to file
    """
    file = Path(file)
    if hasattr(model, "best_estimator_"):
        model = model.best_estimator_
    with file.open("wb") as f:
        pickle.dump(model, f)


def load_model(file: str | Path) -> BaseEstimator:
    """
    Load a model from file
    """
    file = Path(file)
    with file.open("rb") as f:
        return pickle.load(f)
