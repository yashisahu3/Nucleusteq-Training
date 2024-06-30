from pyspark.sql import SparkSession

spark=SparkSession.builder.master("local[1]").appName("ReadTextFile").getOrCreate()
df2=spark.read.json("C:/Users/dell/Downloads/sample1.json")
df2.printSchema()
df2.dtypes
