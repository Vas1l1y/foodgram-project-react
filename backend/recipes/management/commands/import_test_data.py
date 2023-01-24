import pandas as pd

from recipes.models import Ingredient

df = pd.read_csv('../data/ingredients.csv', sep=',')
ingredients = []
for i in range(len(df)):
    ingredients.append(
        Ingredient(
            name=df.iloc[i][0],
            measurement_unit=df.iloc[i][1],
        )
    )
Ingredient.objects.bulk_create(ingredients)
