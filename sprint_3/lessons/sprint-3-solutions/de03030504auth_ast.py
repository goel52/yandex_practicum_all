# pprintast realization.py 
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
    Import(names=[
        alias(name='datetime', asname=None),
      ]),
    Import(names=[
        alias(name='requests', asname=None),
      ]),
    Import(names=[
        alias(name='json', asname=None),
      ]),
    Assign(targets=[
        Name(id='dag', ctx=Store()),
      ], value=Call(func=Name(id='DAG', ctx=Load()), args=[], keywords=[
        keyword(arg='dag_id', value=Constant(value='533_api_generate_report', kind=None)),
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
    Assign(targets=[
        Name(id='nickname', ctx=Store()),
      ], value=Constant(value='aa-tolmachev', kind=None), type_comment=None),
    Assign(targets=[
        Name(id='cohort', ctx=Store()),
      ], value=Constant(value='1', kind=None), type_comment=None),
    Assign(targets=[
        Name(id='api_token', ctx=Store()),
      ], value=Constant(value='5f55e6c0-e9e5-4a9c-b313-63c01fc31460', kind=None), type_comment=None),
    Assign(targets=[
        Name(id='headers', ctx=Store()),
      ], value=Dict(keys=[
        Constant(value='X-API-KEY', kind=None),
        Constant(value='X-Nickname', kind=None),
        Constant(value='X-Cohort', kind=None),
      ], values=[
        Name(id='api_token', ctx=Load()),
        Name(id='nickname', ctx=Load()),
        Name(id='cohort', ctx=Load()),
      ]), type_comment=None),
    FunctionDef(name='create_files_request', args=arguments(posonlyargs=[], args=[
        arg(arg='headers', annotation=None, type_comment=None),
      ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
        Assign(targets=[
            Name(id='api_conn', ctx=Store()),
          ], value=Call(func=Attribute(value=Name(id='BaseHook', ctx=Load()), attr='get_connection', ctx=Load()), args=[
            Constant(value='create_files_api', kind=None),
          ], keywords=[]), type_comment=None),
        Assign(targets=[
            Name(id='api_endpoint', ctx=Store()),
          ], value=Attribute(value=Name(id='api_conn', ctx=Load()), attr='host', ctx=Load()), type_comment=None),
        Assign(targets=[
            Name(id='method_url', ctx=Store()),
          ], value=Constant(value='/generate_report', kind=None), type_comment=None),
        Assign(targets=[
            Name(id='r', ctx=Store()),
          ], value=Call(func=Attribute(value=Name(id='requests', ctx=Load()), attr='post', ctx=Load()), args=[
            BinOp(left=BinOp(left=Constant(value='https://', kind=None), op=Add(), right=Name(id='api_endpoint', ctx=Load())), op=Add(), right=Name(id='method_url', ctx=Load())),
          ], keywords=[
            keyword(arg='headers', value=Name(id='headers', ctx=Load())),
          ]), type_comment=None),
        Assign(targets=[
            Name(id='response_dict', ctx=Store()),
          ], value=Call(func=Attribute(value=Name(id='json', ctx=Load()), attr='loads', ctx=Load()), args=[
            Attribute(value=Name(id='r', ctx=Load()), attr='content', ctx=Load()),
          ], keywords=[]), type_comment=None),
        Expr(value=Call(func=Name(id='print', ctx=Load()), args=[
            JoinedStr(values=[
                Constant(value='task_id is ', kind=None),
                FormattedValue(value=Subscript(value=Name(id='response_dict', ctx=Load()), slice=Index(value=Constant(value='task_id', kind=None)), ctx=Load()), conversion=-1, format_spec=None),
              ]),
          ], keywords=[])),
        Return(value=Subscript(value=Name(id='response_dict', ctx=Load()), slice=Index(value=Constant(value='task_id', kind=None)), ctx=Load())),
      ], decorator_list=[], returns=None, type_comment=None),
    Assign(targets=[
        Name(id='task', ctx=Store()),
      ], value=Call(func=Name(id='PythonOperator', ctx=Load()), args=[], keywords=[
        keyword(arg='task_id', value=Constant(value='create_files_request', kind=None)),
        keyword(arg='python_callable', value=Name(id='create_files_request', ctx=Load())),
        keyword(arg='op_kwargs', value=Dict(keys=[
            Constant(value='headers', kind=None),
          ], values=[
            Name(id='headers', ctx=Load()),
          ])),
        keyword(arg='dag', value=Name(id='dag', ctx=Load())),
      ]), type_comment=None),
    Expr(value=Name(id='task', ctx=Load())),
  ], type_ignores=[])
