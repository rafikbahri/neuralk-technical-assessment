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
import os

from logger import get_logger

logger = get_logger('make_data')

def generate_data(output_dir='.'):
    """
    Generate example data files for training and testing.
    
    Parameters:
    -----------
    output_dir : str
        Directory where the output files will be saved
    """
    logger.info("Starting data generation process")
    
    try:
        logger.info("Generating classification dataset with 100,000 samples and 50 features")
        X, y = make_classification(n_samples=100_000, n_features=50)
        logger.debug(f"Dataset shape: X={X.shape}, y={len(y)}")
        
        logger.info("Creating DataFrame from generated data")
        df = pl.DataFrame(X, schema=[f"col_{i}" for i in range(X.shape[1])]).with_columns(y=y)
        logger.debug(f"DataFrame shape: {df.shape}")
        
        logger.info("Splitting data into train and test sets")
        df_train, df_test = train_test_split(df)
        logger.debug(f"Train set shape: {df_train.shape}, Test set shape: {df_test.shape}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        train_path = os.path.join(output_dir, "train.parquet")
        test_path = os.path.join(output_dir, "test.parquet")
        logger.info(f"Saving train dataset to {train_path}")
        df_train.write_parquet(train_path)
        logger.info(f"Saving test dataset to {test_path}")
        df_test.write_parquet(test_path)
        
        bad_train_path = os.path.join(output_dir, "BAD_train.parquet")
        bad_test_path = os.path.join(output_dir, "BAD_test.parquet")
        
        logger.info(f"Creating BAD train dataset (missing target column 'y') to {bad_train_path}")
        df_train.drop("y").write_parquet(bad_train_path)
        
        logger.info(f"Creating BAD test dataset (missing feature column 'col_0') to {bad_test_path}")
        df_test.drop("col_0").write_parquet(bad_test_path)
        
        logger.info("Data generation completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error generating data: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    generate_data()
