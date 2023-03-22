import os
from dotenv import load_dotenv

def pytest_generate_tests(metafunc):
    load_dotenv()
    print("hello world!")
    print("hello world!")
    print(os.getenv('HASH_MIN_LEN'))
