Module(body=[
    ImportFrom(module='airflow', names=[
        alias(name='DAG', asname=None),
      ], level=0),
    ImportFrom(module='airflow.providers.http.operators.http', names=[
        alias(name='SimpleHttpOperator', asname=None),
      ], level=0),
    ImportFrom(module='airflow.hooks.base', names=[
        alias(name='BaseHook', asname=None),
      ], level=0),
    ImportFrom(module='airflow.operators.python', names=[
        alias(name='PythonOperator', asname=None),
      ], level=0),
    ImportFrom(module='airflow.operators.bash_operator', names=[
        alias(name='BashOperator', asname=None),
      ], level=0),
    Import(names=[
        alias(name='datetime', asname=None),
      ]),
    Import(names=[
        alias(name='requests', asname=None),
      ]),
    Assign(targets=[
        Name(id='dag', ctx=Store()),
      ], value=Call(func=Name(id='DAG', ctx=Load()), args=[], keywords=[
        keyword(arg='dag_id', value=Constant(value='535_bash_sleep_pythonoperator', kind=None)),
        keyword(arg='schedule_interval', value=Constant(value='0 0 * * *', kind=None)),
        keyword(arg='start_date', value=Call(func=Attribute(value=Name(id='datetime', ctx=Load()), attr='datetime', ctx=Load()), args=[
            Constant(value=2021, kind=None),
            Constant(value=1, kind=None),
            Constant(value=1, kind=None),
          ], keywords=[])),
        keyword(arg='catchup', value=Constant(value=False, kind=None)),
        keyword(arg='dagrun_timeout', value=Call(func=Attribute(value=Name(id='datetime', ctx=Load()), attr='timedelta', ctx=Load()), args=[], keywords=[
            keyword(arg='minutes', value=Constant(value=60, kind=None)),
          ])),
        keyword(arg='tags', value=List(elts=[
            Constant(value='example', kind=None),
            Constant(value='example2', kind=None),
          ], ctx=Load())),
        keyword(arg='params', value=Dict(keys=[
            Constant(value='example_key', kind=None),
          ], values=[
            Constant(value='example_value', kind=None),
          ])),
      ]), type_comment=None),
    Assign(targets=[
        Name(id='business_dt', ctx=Store()),
      ], value=Dict(keys=[
        Constant(value='dt', kind=None),
      ], values=[
        Constant(value='2022-05-06', kind=None),
      ]), type_comment=None),
    Import(names=[
        alias(name='time', asname=None),
      ]),
    FunctionDef(name='sleep_func', args=arguments(posonlyargs=[], args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
        Expr(value=Call(func=Attribute(value=Name(id='time', ctx=Load()), attr='sleep', ctx=Load()), args=[
            Constant(value=10, kind=None),
          ], keywords=[])),
      ], decorator_list=[], returns=None, type_comment=None),
    Assign(targets=[
        Name(id='task', ctx=Store()),
      ], value=Call(func=Name(id='PythonOperator', ctx=Load()), args=[], keywords=[
        keyword(arg='task_id', value=Constant(value='delay_python_task_lambda', kind=None)),
        keyword(arg='python_callable', value=Name(id='sleep_func', ctx=Load())),
        keyword(arg='dag', value=Name(id='dag', ctx=Load())),
      ]), type_comment=None),
    Expr(value=Name(id='task', ctx=Load())),
  ], type_ignores=[])