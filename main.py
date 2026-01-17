from src.etl.extract import extract
from src.etl.transform import transform
from src.etl.load import load

def main():
    df = extract()
    df = transform(df)
    load(df)

if __name__ == "__main__":
    main()
