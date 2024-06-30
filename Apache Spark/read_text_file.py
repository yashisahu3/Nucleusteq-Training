from pyspark.sql import SparkSession

spark=SparkSession.builder.master("local[1]").appName("ReadTextFile").getOrCreate()
rdd=spark.sparkContext.textFile("C:/Users/dell/Downloads/data.txt")
rdd.collect()
