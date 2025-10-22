#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE ${TEST_DB_NAME:-wallet_db_test};
    GRANT ALL PRIVILEGES ON DATABASE ${TEST_DB_NAME:-wallet_db_test} TO $POSTGRES_USER;
EOSQL

