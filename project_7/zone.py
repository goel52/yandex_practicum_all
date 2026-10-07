# /user/kostas76/data/spr/geo
def get_cities(spark, path_geo):
    r = 6371
    geo = spark.read.csv(path_geo,sep=";", inferSchema=True, header=True,)
    cities = geo.withColumn("timezone",F.concat(F.lit("Australia/"), F.col('city')))\
    .selectExpr(['city','lat as lat_c','lon as lon_c','timezone'])

    city1 = cities\
    .withColumn("isTimezone",F.when(F.col('timezone').isin(all_timezones),1).otherwise(0))\
    .filter(F.col('isTimezone')==1)\
    .drop('isTimezone')

    return cities\
        .withColumn("isTimezone",F.when(F.col('timezone').isin(all_timezones),1).otherwise(0))\
        .selectExpr(['city','lat_c as lat','lon_c as lon'])\
        .filter(F.col('isTimezone')==0)\
        .crossJoin(city1.drop('city','isTimezone'))\
        .withColumn('l1',\
            F.pow(\
                F.sin( ( F.radians(F.col('lat_c') )- F.radians(F.col('lat')) )/F.lit(2) )\
                , 2.0 ))\
        .withColumn('l2',\
            F.cos( F.radians(F.col('lat_c'))) * F.cos( F.radians(F.col('lat')))\
            *F.pow(\
                F.sin( ( F.radians(F.col('lon_c')) - F.radians(F.col('lon')) )/F.lit(2) )\
                , 2.0 ))\
        .withColumn('dist_m',\
            2*r*F.asin(F.sqrt(F.col('l1')+F.col('l2')))
                   )\
        .withColumn("rid1", F.row_number().over(Window.partitionBy('city','lat','lon').orderBy(F.asc("dist_m"))))\
        .filter(F.col('rid1')==1)\
        .selectExpr(['city','lat as lat_c','lon as lon_c','timezone'])\
        .union(city1)