import os

class Env:
    VERSION:str = os.environ["VERSION"]


env = Env()
