import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import make_pipeline


def stratified_sample(df: pd.DataFrame, test_size: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a dataset while respecting the distribution.

    Args:
        df (pd.DataFrame): The input dataset.
        test_size (float): The fraction of the dataset to use as test data.
        Must be in (0, 1[.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: the train/test dataset tuple.
    """
    hist = np.histogram(df["accident_num"], bins="doane")
    df["bin"] = np.fmin(np.digitize(df["accident_num"], hist[1]), len(hist[0]))
    df_test = df.groupby("bin", group_keys=False).apply(lambda x: x.sample(frac=test_size, random_state=42))
    df_train = df.drop(index=df_test.index)

    # Drop bin col
    df = df.drop(columns="bin")
    df_train = df_train.drop(columns="bin")
    df_test = df_test.drop(columns="bin")
    return df_train, df_test


def grid_search(
    model: BaseEstimator,
    params: dict[str, list],
    X: pd.DataFrame | np.ndarray,
    y: pd.DataFrame | np.ndarray,
    scaler: TransformerMixin | None = None,
    scoring="neg_root_mean_squared_error",
) -> tuple[GridSearchCV, pd.DataFrame]:
    """Perform a grid search.

    Args:
        model (BaseEstimator): The model to run the grid search on.
        params (dict[str, list]): The parameters in the grid search.
        X (pd.DataFrame | np.ndarray): The independant variables.
        y (pd.DataFrame | np.ndarray): The dependant variable.
        scaler (TransformerMixin, optional): a scikit-learn scaler applied before the model. Defaults to None.
        scoring (str, optional): a scikit-learn scoring function. Defaults to "neg_root_mean_squared_error".

    Returns:
        tuple[GridSearchCV, pd.DataFrame]: A tuple containing the fitted GridSearchCV estimator,
        and a formatted dataframe of results.
    """
    if scaler is not None:
        estimator = make_pipeline(scaler, model)
        params = {f"{estimator.steps[-1][0]}__{k}": v for k, v in params.items()}
    else:
        estimator = model

    grid_model = GridSearchCV(
        estimator=estimator, param_grid=params, n_jobs=-1, return_train_score=True, scoring=scoring
    )
    grid_model.fit(X, y)

    # Remove prefix in params dict
    results = pd.DataFrame(grid_model.cv_results_).sort_values("rank_test_score")[
        ["params", "mean_test_score", "std_test_score", "mean_train_score", "std_train_score"]
    ]
    results["params"] = results["params"].apply(
        lambda params: {k.split("__", maxsplit=1)[1]: v for k, v in params.items()}
    )
    return grid_model, results
