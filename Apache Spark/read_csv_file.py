from pyspark.sql import SparkSession

spark=SparkSession.builder.master("local[1]").appName("ReadTextFile").getOrCreate()
df1=spark.read.csv("C:/Users/dell/Downloads/industry.csv")
df1.printSchema()
df1.dtypes
