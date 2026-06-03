import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, when

args = getResolvedOptions(sys.argv, ["JOB_NAME", "RAW_BUCKET", "PROCESSED_BUCKET"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

raw_path = f"s3://{args['RAW_BUCKET']}/raw/"
print(f"Reading from: {raw_path}")

raw_df = spark.read.option("recursiveFileLookup", "true").json(raw_path)
print(f"Records read: {raw_df.count()}")

valid_df = raw_df.filter(
    (col("temperature_c") >= 0) &
    (col("temperature_c") <= 200) &
    col("machine_id").isNotNull()
)

enriched_df = valid_df.withColumn(
    "temp_category",
    when(col("temperature_c") > 85, "CRITICAL")
    .when(col("temperature_c") > 75, "HIGH")
    .when(col("temperature_c") > 65, "NORMAL")
    .otherwise("LOW")
).withColumn("ingestion_date", col("timestamp").cast("date"))

processed_path = f"s3://{args['PROCESSED_BUCKET']}/processed/"
print(f"Writing Parquet to: {processed_path}")

enriched_df.write \
    .mode("append") \
    .partitionBy("machine_id", "ingestion_date") \
    .parquet(processed_path)

print("ETL complete.")
job.commit()