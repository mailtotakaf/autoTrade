# https://qiita.com/harukikaneko/items/b004048f8d1eca44cba9

import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

COINCHECK_API_KEY = os.environ.get("COINCHECK_API_KEY")
COINCHECK_SECRET = os.environ.get("COINCHECK_SECRET")

BITFLYER_API_KEY = os.environ.get("BITFLYER_API_KEY")
BITFLYER_SECRET = os.environ.get("BITFLYER_SECRET")

BITTRADE_API_KEY = os.environ.get("BITTRADE_API_KEY")
BITTRADE_SECRET = os.environ.get("BITTRADE_SECRET")