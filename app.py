from src.etl.extract import extract
from src.etl.transform import transform
from src.etl.load import load
from src.visualization.dashboard import show_dashboard  # <-- importa aqui



df = extract()
df = transform(df)
load(df)
show_dashboard(df)