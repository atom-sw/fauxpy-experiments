from pathlib import Path


def main():
    testing_file_path = Path("testing_file.py")
    with testing_file_path.open() as file:
        content = file.read()
    print(content)
    print(content.splitlines())
    print(content.split("\n"))


if __name__ == '__main__':
    main()
