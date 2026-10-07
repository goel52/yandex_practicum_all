CREATE TABLE IF NOT EXISTS public.outbox (
        id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        object_id int NOT NULL,
        record_ts timestamp NOT NULL,
        type varchar NOT NULL,
        payload text NOT NULL
    );