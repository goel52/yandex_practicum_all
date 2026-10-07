from fastapi import APIRouter

from .checks import (de07030601_create_sparksession,
                     de07030602_create_sparksession_yarn,
                     de07040401_create_data_frame,
                     de07040402_read_json, de07040603_join_title,
                     de07040403_write_parquet,
                     de07040601_join_leftanti,
                     de07040602_join_leftanti_count,
                     de07040604_union_by_name,
                     de07040701_cache_explain,
                     de07040702_cache_checkpoint,
                     de07040801_hour_min_sec,
                     de07040802_filter_is_not_null,
                     de07040803_max_count_reaction,
                     de07040901_window_orderby_pa,
                     de07040902_events_print_schema,
                     de07040903_message_from_lag,
                     de07040904_purchase_amount_max_min,
                     de07041001_json_to_parquet,
                     de07041002_jobs_with_params,
                     de07041101_spark_submit_python_scripts,
                     de07041102_spark_submit_partition,
                     de07041201_job_bash_or_spark_operator,
                     de07050201_def_input_paths,
                     de07050202_find_new_tags,
                     de07050203_find_new_tags_84,
                     de07050204_joba_find_new_tags,
                     de07050205_dag_joba_find_new_tags,
                     de07050301_tag_tops,
                     de07050302_reaction_tag_tops,
                     de07050303_calculate_user_interests,
                     de07050304_compare_df,
                     de07050305_pyspark_job,
                     de07050306_airflow_dag,
                     de07050401_connection_interests
                     )

router = APIRouter()

router.include_router(de07030601_create_sparksession.router,
                      prefix="/de07030601_create_sparksession",
                      tags=["de07030601"])
router.include_router(de07030602_create_sparksession_yarn.router,
                      prefix="/de07030602_create_sparksession_yarn",
                      tags=["de07030602"])

router.include_router(de07040401_create_data_frame.router,
                      prefix="/de07040401_create_data_frame",
                      tags=["de07040401"])
router.include_router(de07040402_read_json.router,
                      prefix="/de07040402_read_json",
                      tags=["de07040402"])
router.include_router(de07040403_write_parquet.router,
                      prefix="/de07040403_write_parquet",
                      tags=["de07040403"])

router.include_router(de07040601_join_leftanti.router,
                      prefix="/de07040601_join_leftanti",
                      tags=["de07040601"])
router.include_router(de07040602_join_leftanti_count.router,
                      prefix="/de07040602_join_leftanti_count",
                      tags=["de07040602"])
router.include_router(de07040603_join_title.router,
                      prefix="/de07040603_union_by_name",
                      tags=["de07040603"])
router.include_router(de07040604_union_by_name.router,
                      prefix="/de07040604_union_by_name",
                      tags=["de07040604"])

router.include_router(de07040701_cache_explain.router,
                      prefix="/de07040701_cache_explain",
                      tags=["de07040701"])
router.include_router(de07040702_cache_checkpoint.router,
                      prefix="/de07040702_cache_checkpoint",
                      tags=["de07040702"])

router.include_router(de07040801_hour_min_sec.router,
                      prefix="/de07040801_hour_min_sec",
                      tags=["de07040801"])
router.include_router(de07040802_filter_is_not_null.router,
                      prefix="/de07040802_filter_is_not_null",
                      tags=["de07040802"])
router.include_router(de07040803_max_count_reaction.router,
                      prefix="/de07040803_max_count_reaction",
                      tags=["de07040803"])

router.include_router(de07040901_window_orderby_pa.router,
                      prefix="/de07040901_window_orderby_pa",
                      tags=["de07040901"])
router.include_router(de07040902_events_print_schema.router,
                      prefix="/de07040902_events_print_schema",
                      tags=["de07040902"])
router.include_router(de07040903_message_from_lag.router,
                      prefix="/de07040903_message_from_lag",
                      tags=["de07040903"])
router.include_router(de07040904_purchase_amount_max_min.router,
                      prefix="/de07040904_purchase_amount_max_min",
                      tags=["de07040904"])

router.include_router(de07041001_json_to_parquet.router,
                      prefix="/de07041001_json_to_parquet",
                      tags=["de07041001"])
router.include_router(de07041002_jobs_with_params.router,
                      prefix="/de07041002_jobs_with_params",
                      tags=["de07041002"])

router.include_router(de07041101_spark_submit_python_scripts.router,
                      prefix="/de07041101_spark_submit_python_scripts",
                      tags=["de07041101"])
router.include_router(de07041102_spark_submit_partition.router,
                      prefix="/de07041102_spark_submit_partition",
                      tags=["de07041102"])

router.include_router(de07041201_job_bash_or_spark_operator.router,
                      prefix="/de07041201_job_bash_or_spark_operator",
                      tags=["de07041201"])

router.include_router(de07050201_def_input_paths.router,
                      prefix="/de07050201_def_input_paths",
                      tags=["de07050201"])
router.include_router(de07050202_find_new_tags.router,
                      prefix="/de07050202_find_new_tags",
                      tags=["de07050202"])
router.include_router(de07050203_find_new_tags_84.router,
                      prefix="/de07050203_find_new_tags_84",
                      tags=["de07050203"])
router.include_router(de07050204_joba_find_new_tags.router,
                      prefix="/de07050204_joba_find_new_tags",
                      tags=["de07050204"])
router.include_router(de07050205_dag_joba_find_new_tags.router,
                      prefix="/de07050205_dag_joba_find_new_tags",
                      tags=["de07050205"])
router.include_router(de07050301_tag_tops.router,
                      prefix="/de07050301_tag_tops",
                      tags=["de07050301"])
router.include_router(de07050302_reaction_tag_tops.router,
                      prefix="/de07050302_reaction_tag_tops",
                      tags=["de07050302"])
router.include_router(de07050303_calculate_user_interests.router,
                      prefix="/de07050303_calculate_user_interests",
                      tags=["de07050303"])
router.include_router(de07050304_compare_df.router,
                      prefix="/de07050304_compare_df",
                      tags=["de07050304"])
router.include_router(de07050305_pyspark_job.router,
                      prefix="/de07050305_pyspark_job",
                      tags=["de07050305"])
router.include_router(de07050306_airflow_dag.router,
                      prefix="/de07050306_airflow_dag",
                      tags=["de07050306"])

router.include_router(de07050401_connection_interests.router,
                      prefix="/de07050401_connection_interests",
                      tags=["de07050401"])
