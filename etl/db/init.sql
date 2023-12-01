BEGIN;

-- создаем схему
CREATE SCHEMA IF NOT EXISTS content;
-- делаем созданную схему основной
SET search_path TO content,public;

-- устанавливаем схему по умолчанию
ALTER ROLE app SET search_path TO content,public;

--------------------
-- ОПИСАНИЕ ТАБЛИЦ
--------------------
-- таблица с кинопроизведениями
CREATE TABLE "filmwork" (
    "id" uuid NOT NULL PRIMARY KEY,
    "title" varchar(255) NOT NULL,
    "description" text NULL,
    "creation_date" date NULL,
    "file_path" varchar(100) NULL,
    "rating" double precision NULL,
    "type" varchar(255) NOT NULL,
    "created_at" timestamp with time zone NOT NULL,
    "updated_at" timestamp with time zone NOT NULL
);

-- таблица с жанрами
CREATE TABLE "genre" (
    "id" uuid NOT NULL PRIMARY KEY,
    "name" varchar(255) NOT NULL,
    "description" text NULL,
    "created_at" timestamp with time zone NOT NULL,
    "updated_at" timestamp with time zone NOT NULL
);

-- таблица с персонами
CREATE TABLE "person" (
    "id" uuid NOT NULL PRIMARY KEY,
    "full_name" varchar(255) NOT NULL,
    "created_at" timestamp with time zone NOT NULL,
    "updated_at" timestamp with time zone NOT NULL
);

-- таблица с персонами в кинопроизведении
CREATE TABLE "filmwork_person" (
    "id" uuid NOT NULL PRIMARY KEY,
    "filmwork_id" uuid NOT NULL,
    "person_id" uuid NOT NULL,
    "role" text NULL,
    "created_at" timestamp with time zone NOT NULL
);

-- таблица с жанрами в кинопроизведении
CREATE TABLE "filmwork_genre" (
    "id" uuid NOT NULL PRIMARY KEY,
    "filmwork_id" uuid NOT NULL,
    "genre_id" uuid NOT NULL,
    "created_at" timestamp with time zone NOT NULL
);

--------------------
-- КЛЮЧИ
--------------------
ALTER TABLE "filmwork_person"
    ADD CONSTRAINT "filmwork_person_filmwork_fk"
    FOREIGN KEY ("filmwork_id")
    REFERENCES "filmwork" ("id") DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "filmwork_person"
    ADD CONSTRAINT "filmwork_person_person_fk"
    FOREIGN KEY ("person_id")
    REFERENCES "person" ("id") DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "filmwork_genre"
    ADD CONSTRAINT "filmwork_genre_filmwork_fk"
    FOREIGN KEY ("filmwork_id")
    REFERENCES "filmwork" ("id") DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "filmwork_genre"
    ADD CONSTRAINT "filmwork_genre_genre_fk"
    FOREIGN KEY ("genre_id")
    REFERENCES "genre" ("id") DEFERRABLE INITIALLY DEFERRED;

--------------------
-- ИНДЕКСЫ
--------------------
CREATE UNIQUE INDEX "filmwork_person_filmwork_idx" ON "filmwork_person" ("filmwork_id", "person_id", "role");
CREATE INDEX "filmwork_genre_filmwork_idx" ON "filmwork_genre" ("filmwork_id");
CREATE INDEX "filmwork_genre_genre_idx"  ON "filmwork_genre" ("genre_id");
CREATE INDEX "filmwork_created_at_idx" ON "filmwork" ("created_at");
CREATE INDEX "filmwork_updated_at_idx" ON "filmwork" ("updated_at");
CREATE INDEX "genre_created_at_idx" ON "genre" ("created_at");
CREATE INDEX "genre_updated_at_idx" ON "genre" ("updated_at");
CREATE INDEX "person_created_at_idx" ON "person" ("created_at");
CREATE INDEX "person_updated_at_idx" ON "person" ("updated_at");

COMMIT;

