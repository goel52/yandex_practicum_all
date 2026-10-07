class DependencyConfig:
    # Start the existing Spark runtime only when a DataFrame endpoint needs it.
    @staticmethod
    def spark():
        from sprint_7_check_service.spark_tools.init_spark import spark
        return spark

    @staticmethod
    def spark_tag_tops():
        from sprint_7_check_service.spark_tools.init_spark import spark_tag_tops
        return spark_tag_tops

    @staticmethod
    def spark_reaction_tag_tops():
        from sprint_7_check_service.spark_tools.init_spark import spark_reaction_tag_tops
        return spark_reaction_tag_tops
