INSERT INTO public.f_activity (activity_id, create_date, customer_id, action_id, quantity)
SELECT DISTINCT ON (uniq_id)
       uniq_id         AS activity_id,
       date_time::date AS create_date,
       cus.id      AS customer_id,
       ual.action_id      ,
       quantity
FROM public.user_activity_log ual
         JOIN public.d_customer cus ON cus.customer_id = ual.customer_id and '{{ ds }}' BETWEEN cus.start_date AND cus.end_date
         WHERE ual.date_time::date = '{{ ds }}'
            ORDER BY uniq_id, date_time DESC