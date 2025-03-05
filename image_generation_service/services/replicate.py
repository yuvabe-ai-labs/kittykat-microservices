import time
from config.replicate import client


def generate_prediction(model: str, prompt: str):
    """
    Generate a prediction using the Replicate API.
    """
    try:
        if (
            model
            == "kittykat-ai/swyft:b819072f68811372560fe983c7fbc7921a2386d9a42cb1e35c203fb62799014e"
        ):
            # Use direct run syntax if model matches
            output = client.run(model, input={"prompt": prompt})
            return output[-1].url
        else:
            # Use the polling method for other models
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
