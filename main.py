import os
from backend.app_service import AppService

def main():
    AppService().start()
    print(os.getenv("MY_API_KEY"))


if __name__ == "__main__":
    main()
