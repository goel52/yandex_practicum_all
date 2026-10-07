from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame

from .event_df import event_user_tag_tops, event_user_reaction_tag_tops


class MockDataFrameReaderUserTagTops:
    def __init__(self, mock_spark: ...):
        self._spark = mock_spark

    def parquet(self, *paths: str) -> DataFrame:
        return event_user_tag_tops(spark)

    def option(self, key: str, value: str):
        return self


class MockSparkSessionUserTagTops:
    @property
    def read(self) -> DataFrame:
        return MockDataFrameReaderUserTagTops(self)


class MockDataFrameReaderReactionUserTagTops:
    def __init__(self, mock_spark: ...):
        self._spark = mock_spark

    def parquet(self, *paths: str) -> DataFrame:
        return event_user_reaction_tag_tops(spark)

    def option(self, key: str, value: str):
        return self


class MockSparkSessionUserReactionTagTops:
    @property
    def read(self) -> DataFrame:
        return MockDataFrameReaderReactionUserTagTops(self)


spark = (SparkSession
         .builder
         .master("local")
         .appName("Checkers")
         .getOrCreate())

spark_tag_tops = MockSparkSessionUserTagTops()

spark_reaction_tag_tops = MockSparkSessionUserReactionTagTops()
