CREATE TABLE IF NOT EXISTS stg.srv_wf_settings (
    id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    workflow_key varchar UNIQUE,
    workflow_settings text
);