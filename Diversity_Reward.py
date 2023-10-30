import json
import pandas as pd

with open('movies_cleaned.json', 'r') as f:
    movies_cleaned = json.load(f)

movies = json.dumps(movies_cleaned, indent=4)
# print(movies)

movies_df = pd.DataFrame.from_dict(movies_cleaned)
print(movies_df)