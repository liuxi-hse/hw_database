# 1.
import mysql.connector
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import re
import os
import matplotlib.pyplot as plt

# 2 connect Database and MySQL
# mydb = mysql.connector.connect(
#     host = 'localhost',
#     port = '3306',
#     user = "root",
#     password = 'srythisisasecret'
# )

# # 3. show databases
# mycursor = mydb.cursor()
# mycursor.execute("SHOW DATABASES")
#
# for database in mycursor:
#   print(database)

# 4.
path = 'C:/Users/86188/Downloads/metadata.tsv' #измените путь на свой
meta = pd.read_csv(path, sep='\t') #пушкинский дом выкладывает файлы в  tsv (tab separated values), поэтому надо указать правильный делиметер
# print(meta.head())

# 5. create database
# mycursor = mydb.cursor()
# mycursor.execute("CREATE DATABASE db_0515")

# 6.
# Since some of the data of years in the table are ambiguous, preprocessing is required
def clean_numeric(value):
    if pd.isna(value) or str(value).lower() in ['nan', 'none', '']:
        return None
    try:
        if isinstance(value, str) and 'или' in value:
            return int(value.split('или')[0].strip())
        return int(float(value))
    except:
        return None

for_db = []
for ind in meta.index:
    birth_year = clean_numeric(meta.loc[ind, 'author_birth_year'])
    death_year = clean_numeric(meta.loc[ind, 'author_death_year'])
    pub_year = clean_numeric(meta.loc[ind, 'year'])

    record = (
        str(meta.loc[ind, 'filename']),
        str(meta.loc[ind, 'author']),
        birth_year,
        death_year,
        str(meta.loc[ind, 'title']),
        str(meta.loc[ind, 'source_title']),
        pub_year
    )
    for_db.append(record)

## 7. check tables
# mycursor = mydb.cursor()
# mycursor.execute("SHOW TABLES")
# for table in mycursor:
#   print(table)

## 8. create tables and insert data to meta
# mydb = mysql.connector.connect(
#     host = "localhost",
#     user = "root",
#     port = ('3306'),
#     password = ('srythisisasecret'),
#     database = "db_0515"
# )
# mycursor = mydb.cursor()
# mycursor.execute("""CREATE TABLE IF NOT EXISTS meta (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     filename VARCHAR(255) NOT NULL AFTER id,
#     author VARCHAR(255),
#     author_birth_year SMALLINT NULL,
#     author_death_year SMALLINT NULL,
#     title VARCHAR(500),
#     source_title VARCHAR(500),
#     year SMALLINT NULL
# );"""
# )
# mycursor.execute("""CREATE TABLE texts (
#     id INT PRIMARY KEY,
#     content LONGTEXT NOT NULL,
#     FOREIGN KEY (id) REFERENCES meta(id)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""
# )

# sql = """
# INSERT INTO meta
# (filename, author, author_birth_year, author_death_year, title, source_title, year)
# VALUES (%s, %s, %s, %s, %s, %s, %s)
# """
# mycursor.executemany(sql, for_db)
# mydb.commit()

# 9. insert data to Table text
# TEXT_DIR = r'C:\Users\86188\Downloads\text_corpus' #не забудьте поменять на путь, где лежат ваши тексты
# DB_CONFIG = {
#     'host': 'localhost',
#     'user': 'root',
#     'password':  'srythisisasecret',
#     'database': 'db_0515',
#     'charset': 'utf8mb4'
# }
#
# def get_clean_connection():
#     return mysql.connector.connect(**DB_CONFIG)
#
# def insert_texts():
#     conn = get_clean_connection()
#     cursor = conn.cursor()
#
#     try:
#         cursor.execute("SELECT id FROM texts")
#         existing_ids = {row[0] for row in cursor.fetchall()}
#
#         for filename in os.listdir(TEXT_DIR):
#             if not filename.endswith('.txt'):
#                 continue
#
#             # Use new connections to avoid conflicts
#             with get_clean_connection() as meta_conn:
#                 meta_cursor = meta_conn.cursor()
#                 meta_cursor.execute(
#                     "SELECT id FROM meta WHERE filename = %s",
#                     (filename,)
#                 )
#                 result = meta_cursor.fetchone()
#                 meta_cursor.close()
#
#             if not result:
#                 continue
#
#             meta_id = result[0]
#
#             if meta_id in existing_ids:
#                 continue
#
#             file_path = os.path.join(TEXT_DIR, filename)
#             try:
#                 with open(file_path, 'r', encoding='utf-8') as f:
#                     content = f.read()
#             except Exception as e:
#                 continue
#
#             try:
#                 cursor.execute(
#                     """INSERT INTO texts (id, content)
#                        VALUES (%s, %s)
#                        ON DUPLICATE KEY UPDATE content = VALUES(content)""",
#                     (meta_id, content)
#                 )
#                 conn.commit()
#             except mysql.connector.Error as e:
#                 conn.rollback()
#
#     finally:
#       cursor.close()
#       conn.close()
#
# if __name__ == '__main__':
#     insert_texts()

# 10. Little research ---
# Analyze the relationship between the author's age (at the time of publication) and the length of the text
import matplotlib.pyplot as plt
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "Freedom512391535",
    database = "db_0515"
)

# Get creation age and text length
query = """
SELECT 
    (m.year - m.author_birth_year) AS creation_age,
    CHAR_LENGTH(t.content) AS text_length
FROM meta m
JOIN texts t ON m.id = t.id
WHERE 
    m.author_birth_year IS NOT NULL
    AND m.year > m.author_birth_year  -- Filter unreasonable ages
    AND CHAR_LENGTH(t.content) > 1000 -- Filter too short text
"""

mycursor = mydb.cursor()
mycursor.execute(query)
data = mycursor.fetchall()

ages = [x[0] for x in data]
lengths = [x[1]/1000 for x in data]

corr = np.corrcoef(ages, lengths)[0,1]

plt.figure(figsize=(10,6))
plt.scatter(ages, lengths, alpha=0.5, color='#3498db')
plt.title('Связь возраста автора и длины текста (n={})'.format(len(ages)))
plt.xlabel('Возраст автора при публикации', fontsize=12)
plt.ylabel('Длина текста (тыс. символов)', fontsize=12)
plt.grid(linestyle='--', alpha=0.7)
plt.text(25, max(lengths)*0.9,
         f'Коэффициент корреляции: {corr:.2f}',
         fontsize=12,
         bbox=dict(facecolor='white', alpha=0.8))
plt.show()
# Little Conclusion:
# Weak correlation:
# Middle-aged writers (30-50 years old) tend to produce longer works
# Younger writers (<25 years old) and older writers (>60 years old) generally produce shorter works

## 11. комбинаторные запросы
# -- Count the average text length of each author
# query = """
# SELECT
#     m.author,
#     AVG(LENGTH(t.content)) AS avg_length
# FROM meta m
# JOIN texts t ON m.id = t.id
# GROUP BY m.author
# ORDER BY avg_length DESC
# """

# -- Search for works containing "любовь" and with a length > 5000 characters
# query = """
# SELECT
#     m.author,
#     m.title,
#     m.year,
#     CHAR_LENGTH(t.content) AS text_length
# FROM meta m
# JOIN texts t ON m.id = t.id
# WHERE
#     t.content LIKE '%любовь%'
#     AND CHAR_LENGTH(t.content) > 5000
# ORDER BY m.year DESC;
# """

# -- Find works with the same name but different authors
# query = """
# SELECT
#     title,
#     COUNT(DISTINCT author) AS authors_count,
#     GROUP_CONCAT(DISTINCT author SEPARATOR '; ') AS authors
# FROM meta
# GROUP BY title
# HAVING COUNT(DISTINCT author) > 1
# ORDER BY COUNT(DISTINCT author) DESC;
# """

# -- Statistics by length
# query = """
# SELECT
#     CASE
#         WHEN CHAR_LENGTH(content) < 2000 THEN 'short'
#         WHEN CHAR_LENGTH(content) BETWEEN 2000 AND 10000 THEN 'medium'
#         ELSE 'long'
#     END AS length_category,
#     COUNT(*) AS count,
#     ROUND(COUNT(*)/(SELECT COUNT(*) FROM texts)*100,1) AS percentage
# FROM texts
# GROUP BY length_category;
# """

# -- Analyze the characteristics of the text during the author's life span
# query = """
# SELECT
#     CASE
#         WHEN author_death_year - author_birth_year < 50 THEN 'Short-lived writers'
#         WHEN author_death_year - author_birth_year BETWEEN 50 AND 70 THEN 'Medium-lived writers'
#         ELSE 'Long-lived writers'
#     END AS lifespan_group,
#     MAX(CHAR_LENGTH(t.content)) AS max_length,
#     MIN(CHAR_LENGTH(t.content)) AS min_length
# FROM meta m
# JOIN texts t ON m.id = t.id
# WHERE author_death_year IS NOT NULL
# GROUP BY lifespan_group;
# """

## 12 . вложенный запрос
# -- Find works with above-average text length
# query = """
# SELECT
#     author,
#     title,
#     CHAR_LENGTH(content) AS length
# FROM meta m
# JOIN texts t ON m.id = t.id
# WHERE CHAR_LENGTH(content) > (
#     SELECT AVG(CHAR_LENGTH(content))
#     FROM texts
# );
# """

## 13. Join
# Count the total number of lines and average line length for each script
# main_query = """
# SELECT
#     m.author,
#     COUNT(*) AS works_count,
#     AVG(CHAR_LENGTH(t.content)) AS avg_length,
#     MAX(m.year) - MIN(m.year) AS active_years
# FROM meta m
# JOIN texts t ON m.id = t.id  -- 关键JOIN
# WHERE m.year IS NOT NULL
# GROUP BY m.author
# HAVING works_count >= 3
# ORDER BY active_years DESC;
# """

# validation - random sampling inspection
# query = """
# SELECT
#     m.id,
#     m.author,
#     m.title,
#     CHAR_LENGTH(t.content) AS length
# FROM meta m
# JOIN texts t ON m.id = t.id
# ORDER BY RAND()
# LIMIT 5;
#"""