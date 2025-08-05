"""
Generate example data files.

`train.parquet` and `test.parquet` can be used to train a model and make
predictions.

`BAD_train.parquet` and `BAD_test.parquet` are examples of incorrect files
(missing a column) to test the behavior of the system on bad user data.
"""
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import polars as pl

X, y = make_classification(n_samples=100_000, n_features=50)
df = pl.DataFrame(X, schema=[f"col_{i}" for i in range(X.shape[1])]).with_columns(y=y)
df_train, df_test = train_test_split(df)
df_train.write_parquet("train.parquet")
df_train.drop("y").write_parquet("BAD_train.parquet")
df_test.write_parquet("test.parquet")
df_test.drop("col_0").write_parquet("BAD_test.parquet")
