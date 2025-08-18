import pytest
from make_data import generate_data


class TestClientExample1:
    @pytest.fixture(scope="session", autouse=True)
    def generate_test_data(self):
        """Generate test data once per session, automatically."""
        generate_data(output_dir="tests/integration/data")
        print("Test data generated in 'tests/integration/data' directory.")

    @pytest.mark.integration
    def test_client_example1(self, client):
        dataset_id = client.upload("tests/integration/data/train.parquet")

        print("--- fit ---")
        model_id = client.fit(dataset_id, timeout=120)
        assert model_id is not None, "Model ID should not be None after fitting"
        print(f"Model ID: {model_id}")

        test_dataset_id = client.upload("tests/integration/data/test.parquet")
        print("--- predict ---")
        assert test_dataset_id is not None, "Test dataset ID should not be None after upload"
        print(f"Test Dataset ID: {test_dataset_id}")

        prediction_id = client.predict(test_dataset_id, model_id, timeout=120)
        assert prediction_id is not None, "Prediction ID should not be None after prediction"

        prediction = client.download(prediction_id)
        assert prediction is not None, "Prediction should not be None after prediction"