import os

def main(**kwargs):
    print(os.getenv("MY_API_KEY"))


if __name__ == "__main__":
    main()
