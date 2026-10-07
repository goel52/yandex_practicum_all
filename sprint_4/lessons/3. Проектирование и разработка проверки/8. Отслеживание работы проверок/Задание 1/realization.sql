         Select
	"datetime", 
	Table_name,
	DQ_check_name,
  dq_check_result
From 
	stage.dq_checks_results
where 
	datetime in (select max(datetime) from stage.dq_checks_results)
	and dq_check_result = 1