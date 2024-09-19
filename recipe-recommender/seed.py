import sqlite3
import json
import os

import pandas as pd

df = pd.read_csv('./RAW_recipes.csv')

# Expand Nutrition data into their own columns 
df[['calories','total fat (PDV)','sugar (PDV)','sodium (PDV)','protein (PDV)','saturated fat (PDV)','carbohydrates (PDV)']] \
    = df.nutrition.str.split(",",expand=True) 
df['calories'] =  df['calories'].apply(lambda x: x.replace('[','')) 
df['carbohydrates (PDV)'] =  df['carbohydrates (PDV)'].apply(lambda x: x.replace(']','')) 
df[['calories','total fat (PDV)','sugar (PDV)','sodium (PDV)','protein (PDV)','saturated fat (PDV)','carbohydrates (PDV)']] \
    = df[['calories','total fat (PDV)','sugar (PDV)','sodium (PDV)','protein (PDV)','saturated fat (PDV)','carbohydrates (PDV)']] \
        .astype('float')

# Remove unused columns
df.drop(['id', 'contributor_id','submitted','nutrition', ], axis=1,inplace = True)

# Convert string representations of lists into actual lists
df['tags'] = df['tags'].apply(lambda x: eval(x))
df['steps'] = df['steps'].apply(lambda x: eval(x))
df['ingredients'] = df['ingredients'].apply(lambda x: eval(x))

# Define the path to the SQLite database
db_path = os.path.join(os.getcwd(), 'recipes.db')

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Recipes table with steps stored as a JSON array in a text field
cursor.execute('''
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY,
    name TEXT,
    minutes INTEGER,
    description TEXT,
    steps TEXT,
    n_steps INTEGER,
    n_ingredients INTEGER,
    calories REAL,
    total_fat_pdv REAL,
    sugar_pdv REAL,
    sodium_pdv REAL,
    protein_pdv REAL,
    saturated_fat_pdv REAL,
    carbohydrates_pdv REAL
)
''')

# Tags table
cursor.execute('''
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT UNIQUE
)
''')

# Ingredients table
cursor.execute('''
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name TEXT UNIQUE
)
''')

# Recipes-Tags table (junction table for many-to-many relationship)
cursor.execute('''
CREATE TABLE IF NOT EXISTS recipe_tags (
    recipe_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (recipe_id, tag_id),
    FOREIGN KEY(recipe_id) REFERENCES recipes(id),
    FOREIGN KEY(tag_id) REFERENCES tags(id)
)
''')

# Recipes-Ingredients table (junction table for many-to-many relationship)
cursor.execute('''
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id INTEGER,
    ingredient_id INTEGER,
    PRIMARY KEY (recipe_id, ingredient_id),
    FOREIGN KEY(recipe_id) REFERENCES recipes(id),
    FOREIGN KEY(ingredient_id) REFERENCES ingredients(id)
)
''')

# Insert all unique tags from the CSV file to the Tags table
unique_tags = set(tag for tags_list in df['tags'] for tag in tags_list)
for tag in unique_tags:
    cursor.execute('''
    INSERT OR IGNORE INTO tags (tag_name) VALUES (?)
    ''', (tag,))
conn.commit()

# Insert all unique ingredients from the CSV file to the Ingredients table
unique_ingredients = set(ingredient for ingredients_list in df['ingredients'] for ingredient in ingredients_list)
for ingredient in unique_ingredients:
    cursor.execute('''
    INSERT OR IGNORE INTO ingredients (ingredient_name) VALUES (?)
    ''', (ingredient,))
conn.commit()

# Insert all recipes from the CSV file (every row) to the Recipes table
for index, row in df.iterrows():
    cursor.execute('''
    INSERT INTO recipes (name, minutes, description, steps, n_steps, n_ingredients, calories, total_fat_pdv, sugar_pdv, sodium_pdv, protein_pdv, saturated_fat_pdv, carbohydrates_pdv)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (row['name'], row['minutes'], row['description'], json.dumps(row['steps']), row['n_steps'], row['n_ingredients'], row['calories'], row['total fat (PDV)'], row['sugar (PDV)'], row['sodium (PDV)'], row['protein (PDV)'], row['saturated fat (PDV)'], row['carbohydrates (PDV)']))
    recipe_id = cursor.lastrowid
    
    # Insert junction table data for Recipes-Tags
    for tag in row['tags']:
        cursor.execute('''
        INSERT INTO recipe_tags (recipe_id, tag_id)
        VALUES (?, (SELECT id FROM tags WHERE tag_name = ?))
        ''', (recipe_id, tag))
    
    # Insert junction table data for Recipes-Ingredients
    for ingredient in row['ingredients']:
        cursor.execute('''
        INSERT INTO recipe_ingredients (recipe_id, ingredient_id)
        VALUES (?, (SELECT id FROM ingredients WHERE ingredient_name = ?))
        ''', (recipe_id, ingredient))

# Commit and close DB connection
conn.commit()
conn.close()

print(f"Database has been created and populated at {db_path}")