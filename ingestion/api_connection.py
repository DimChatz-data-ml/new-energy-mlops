import os
from dotenv import load_dotenv
from entsoe import EntsoePandasClient

load_dotenv()

def api_con_func():

    api_key=os.getenv("ENTSOE_API_KEY")

    if not api_key:
        raise ValueError('api key was not found! ')

    client=EntsoePandasClient(api_key=api_key)
    return client