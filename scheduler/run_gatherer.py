from app.tasks import gatherer
from io import StringIO
import pandas as pd


result = gatherer()
data = StringIO(result)
cols = ["domains", "censys", "dap", "eot", "parents"]
df = pd.read_csv(data, sep=",", index_col=0)
df = df[cols]
df.to_csv("results.csv", index=False)
