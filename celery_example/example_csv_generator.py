import pandas as pd

df = pd.DataFrame()
df = df.append({"domain": "standards.usa.gov"}, ignore_index=True)

df.to_csv("example.csv")
