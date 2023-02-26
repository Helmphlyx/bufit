import logging

import boto3
import json


def get_secret_from_sm(secret_id: str):
    """Returns AWS Secrets Manager value as a dictionary."""
    secret_value = {}
    try:
        client = boto3.client("secretsmanager")
        response = client.get_secret_value(SecretId=secret_id)
        secret_value = json.loads(response["SecretString"])
    except Exception as exc:
        logging.warning(f"Unable to retrieve secret {secret_id} due to: {exc}")
    return secret_value
