from ast import alias
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
from datetime import date
import os
os.environ['JAVA_HOME'] = '/usr/local/opt/openjdk@21'

spark = SparkSession.builder \
    .appName("user_sessions") \
    .config("spark.jars.packages", "org.apache.spark:spark-avro_2.13:4.0.1") \
    .getOrCreate()

path_log_file = "activity_log.avro"

df = spark.read.format("avro").load(path_log_file)
df.printSchema()
df.show()

df_timestamp = df.withColumn("event_time", F.to_timestamp(df.timestamp, "dd-MMM-yyyy HH:mm")).drop("timestamp")

df_timestamp.printSchema()
df_timestamp.show()


# 1. Ежедневная Активность: Посчитайте общее количество событий (event_id) для каждого дня.
# Вывод: дата (date), общее количество событий (total_events). Отсортируйте по дате по возрастанию.

daily_activity_df = df_timestamp.groupBy(F.to_date("event_time").alias("date")) \
    .agg(F.count("event_id").alias("total_events")) \
    .sort("date")
print("Общее количество событий (event_id) для каждого дня")
daily_activity_df.show()

# 2. Анализ Пользователей и Сессий: Найдите всех уникальных пользователей.
# Посчитайте общее количество уникальных сессий во всём наборе данных. 
# И посчитайте количество уникальных сессий для каждого отдельного пользователя. 

# Вывод 1: список идентификаторов пользователя (user_id). Отсортируйте по user_id по возрастанию.

user_id_df = df_timestamp.select("user_id").distinct().sort("user_id")
print("Уникальные пользователи")
user_id_df.show()

# Вывод 2: одно число - общее количество уникальных сессий.

total_unique_session = df_timestamp.select("session_id").distinct().count()
print("Общее количество уникальных сессий:\t", total_unique_session)

# Вывод 3: идентификатор пользователя (user_id), количество уникальных сессий (unique_sessions_count). 
# Отсортируйте по user_id по возрастанию.

users_unique_sessions = df_timestamp.groupBy("user_id") \
    .agg(F.countDistinct("session_id").alias("unique_sessions_count")) \
    .sort("user_id")
print("Количество уникальных сессий для каждого отдельного пользователя")
users_unique_sessions.show()

# 3. Детализация Сессий: Определите количество событий, произошедших в каждой уникальной пользовательской сессии.
# Вывод: идентификатор пользователя (user_id), идентификатор сессии (session_id), 
# количество событий в сессии (count_events_in_session). 
# Отсортируйте по count_events_in_session по возрастанию.

events_in_unique_sessions = df_timestamp.groupBy("user_id", "session_id") \
    .agg(F.count("event_id").alias("count_events_in_session")) \
    .sort("count_events_in_session")
print("Количество событий в каждой уникальной пользовательской сессии")
events_in_unique_sessions.show()

#4. Анализ Покупок: Посчитайте общее количество событий типа "purchase" (покупок). 
# Найдите общую сумму всех покупок. И посчитайте среднюю сумму одной покупки, 
# округлите результат до двух знаков после запятой.
# Вывод 1: Одно число - общее количество покупок (count_purchase_amount).
# Вывод 2: Одно число - общая сумма покупок (sum_purchase_amount).
# Вывод 3: Одно число - средняя сумма покупки (average_purchase_amount).

purchase_amount = df_timestamp.filter(df_timestamp.event_type == "purchase") \
    .agg(F.count("event_id").alias("count_purchase_amount")) 
purchase_amount.show()

sum_purchase_amount = df_timestamp.filter(df_timestamp.event_type == "purchase") \
    .agg(F.sum(df_timestamp.amount).alias("sum_purchase_amount"))
sum_purchase_amount.show()

average_purchase_amount = df_timestamp.filter(df_timestamp.event_type == "purchase") \
    .agg(F.avg(df_timestamp.amount).alias("average_purchase_amount"))
average_purchase_amount.show()

# 5. Анализ Продолжительности: Для каждой уникальной сессии (user_id, session_id) 
# найдите самое раннее (min_time) и самое позднее (max_time) время события. 
# Вычислите продолжительность сессии в секундах (session_duration_seconds). 
# Также вычислите среднюю продолжительность сессии по всем сессиям и округлите 
# результат до двух знаков после запятой.
# Вывод 1: Идентификатор пользователя (user_id), идентификатор сессии (session_id), 
# время начала сессии (min_time), время окончания сессии (max_time), 
# продолжительность сессии в секундах (session_duration_seconds). 
# Отсортируйте по user_id и session_id.
# Вывод 2: Одно число - средняя продолжительность сессии в секундах (average_session_duration_seconds).

session_duration_df = df_timestamp.groupBy("user_id", "session_id") \
    .agg(
        F.min("event_time").alias("min_time"),
        F.max("event_time").alias("max_time")
    ) \
    .withColumn("session_duration_seconds", F.unix_timestamp("max_time") - F.unix_timestamp("min_time")) \
    .sort("user_id", "session_id")
session_duration_df.show()

average_session_duration_seconds = session_duration_df.agg(F.avg("session_duration_seconds").alias("average_session_duration_seconds"))
average_session_duration_seconds.show()

spark.stop()