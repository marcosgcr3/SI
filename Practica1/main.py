import pandas as pd
import numpy as np
from holoviews.ipython import display

movies = pd.read_csv('movies_metadata.csv',dtype={ 10 : 'str'})
display(movies.head(n=4))
display(movies.tail(n=4))

ratings = pd.read_csv('ratings_small.csv')
display(ratings.head(n=4))
display(ratings.tail(n=4))


lion = movies[movies["title"] == "The Lion King"]
display(lion)