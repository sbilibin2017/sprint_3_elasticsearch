ALTER TABLE genre_film_work RENAME COLUMN film_work_id TO filmwork_id;
ALTER TABLE person_film_work RENAME COLUMN film_work_id TO filmwork_id;
ALTER TABLE film_work RENAME TO filmwork;
ALTER TABLE person_film_work RENAME TO filmwork_person;
ALTER TABLE genre_film_work RENAME TO filmwork_genre;