import time
from config.replicate import client


def generate_prediction(model: str, prompt: str):
    """
    Generate a prediction using the Replicate API.
    """
    try:
        prediction = client.predictions.create(
            model=model,
            input={"prompt": prompt},
        )

        # Poll for prediction completion
        while prediction.status not in ["succeeded", "failed", "canceled"]:
            time.sleep(2)
            prediction = client.predictions.get(prediction.id)

        return prediction
    except Exception as e:
        raise Exception(f"Failed to generate prediction: {str(e)}")
