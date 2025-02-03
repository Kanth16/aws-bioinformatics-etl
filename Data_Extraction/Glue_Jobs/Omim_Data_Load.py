import sys
import hashlib
import time
from pyspark.sql import functions as F
from pyspark.sql.functions import expr, col, concat_ws, sha2, lit
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
import time
import logging
from pyspark.sql.utils import AnalysisException

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Initialize Glue Context
    logger.info("Initializing Glue Context...")
    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session

    # Read data from Glue Data Catalog
    logger.info("Reading data from Glue Catalog...")
    glue_df = glueContext.create_dynamic_frame.from_catalog(
        database="neurological diseases",
        table_name="omim"
    )

    # Convert Glue DynamicFrame to Spark DataFrame
    logger.info("Converting DynamicFrame to DataFrame...")
    df = glue_df.toDF()
    
    # Rename partition_0 to Disease_Name
    df = df.withColumnRenamed("preferredtitle", "preferred_title") \
       .withColumnRenamed("mimnumber", "Omim_ID") \
       .withColumnRenamed("phenotype", "Phenotype") \
       .withColumnRenamed("mutations", "Mutation") \
       .withColumnRenamed("dbsnps", "SNPs") \
       .withColumnRenamed("BioGRID_ID", "Biogrid_id") \
       .withColumnRenamed("partition_0", "Disease_Name")
    
    df = df.withColumn("Biogrid_id", col("BioGRID_ID").cast("bigint"))
    df = df.withColumn("Omim_ID", col("Omim_ID").cast("bigint"))
    df = df.withColumn("Omim_Key", sha2(
    concat_ws("|", col("preferred_title"), col("Omim_ID"), col("Phenotype"),col("Mutation"), col("SNPs"), col("Biogrid_id"), col("Disease_Name")), 256))

    # Generate Load_Key (Timestamp without delimiters)
    df = df.withColumn("Load_Key", lit(int(time.time())).cast("bigint")) 

    # Show first few rows (for debugging)
    logger.info("Previewing first few rows:")
    df.show(5)

    # MySQL Connection Details
    mysql_url = "jdbc:mysql://neurological-diseases.ckz6q8wguj2u.us-east-1.rds.amazonaws.com:3306/NeurologicalDiseases"
    db_table = "omim"
    db_user = "admin"
    db_password = "Devilcant123$"

    # Attempt to write to MySQL with retry logic
    retry_attempts = 3
    for attempt in range(1, retry_attempts + 1):
        try:
            logger.info(f"Attempt {attempt}: Writing data to MySQL table {db_table}...")
            df.write \
            .format("jdbc") \
            .option("url", "jdbc:mysql://neurological-diseases.ckz6q8wguj2u.us-east-1.rds.amazonaws.com:3306/NeurologicalDiseases") \
            .option("dbtable", "Omim") \
            .option("user", "glue_user") \
            .option("password", "GluePassword123!") \
            .option("driver", "com.mysql.cj.jdbc.Driver") \
            .mode("append") \
            .save()

            
            logger.info("✅ Data successfully written to MySQL!")
            break  # Exit loop on success
        
        except AnalysisException as e:
            logger.error(f"❌ AnalysisException encountered: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Error writing to MySQL (Attempt {attempt}/{retry_attempts}): {str(e)}")
            if attempt == retry_attempts:
                logger.error("❌ Maximum retry attempts reached. Exiting.")
                sys.exit(1)  # Exit with failure code
        else:
            break  # Exit loop if write is successful

except Exception as e:
    logger.error(f"❌ Fatal error in Glue job: {str(e)}")
    sys.exit(1)  # Exit with failure code

logger.info("✅ Glue job completed successfully!")