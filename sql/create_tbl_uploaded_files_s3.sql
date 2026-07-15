CREATE TABLE uploaded_files_s3 (
    id              SERIAL PRIMARY KEY,
    filename        VARCHAR(255),
    extension       VARCHAR(20),
    file_size       BIGINT,
    content_type    VARCHAR(100),
    upload_time     TIMESTAMP,
    last_modified   TIMESTAMP,
    etag            VARCHAR(100),
    bucket_name     VARCHAR(100),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);