SQL_LAST_INSERTED_PERSONS = f"SELECT id, modified " \
                            f"FROM content.person " \
                            f"WHERE modified > %s " \
                            f"ORDER BY modified " \
                            f"LIMIT %s;"

SQL_LAST_INSERTED_GENRES = f"SELECT id, modified " \
                           f"FROM content.genre " \
                           f"WHERE modified > %s " \
                           f"ORDER BY modified " \
                           f"LIMIT %s;"

SQL_MOVIES_WHERE_PERSON = f"SELECT fw.id " \
                    f"FROM content.film_work fw " \
                    f"LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id " \
                    f"WHERE pfw.person_id IN %s " \
                    f"ORDER BY fw.modified "

SQL_MOVIES_WHERE_GENRE = f"SELECT fw.id " \
                    f"FROM content.film_work fw " \
                    f"LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id " \
                    f"WHERE gfw.genre_id IN %s "

SQL_PERSONS_WHERE_MOVIE = f"SELECT p.id " \
                    f"FROM content.person p " \
                    f"LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id " \
                    f"WHERE pfw.film_work_id IN %s " \
                    f"ORDER BY p.modified "

SQL_GENRES_WHERE_MOVIE = f"SELECT g.id " \
                    f"FROM content.genre g " \
                    f"LEFT JOIN content.genre_film_work gfw ON gfw.genre_id = g.id " \
                    f"WHERE gfw.film_work_id IN %s " \
                    f"ORDER BY g.modified "

SQL_LAST_INSERTED_TIME_FILMWORKS = f"SELECT id, modified " \
                                   f"FROM content.film_work " \
                                   f"WHERE modified > %s " \
                                   f"ORDER BY modified " \
                                   f"LIMIT %s"

UNION_PERSON_GENRES = f"({SQL_MOVIES_WHERE_PERSON}) UNION ({SQL_MOVIES_WHERE_GENRE})"

ALL_MODIFIED_MOVIES = f"SELECT " \
                      f"fw.id as fw_id, " \
                      f"fw.title, " \
                      f"fw.description, " \
                      f"fw.rating, " \
                      f"COALESCE (" \
                      f"json_agg(" \
                      f"DISTINCT jsonb_build_object(" \
                      f"'person_role', pfw.role, " \
                      f"'person_id', p.id, " \
                      f"'person_name', p.full_name)" \
                      f") " \
                      f"FILTER (WHERE p.id is not null), " \
                      f"'[]') as persons, " \
                      f"array_agg(DISTINCT g.name) as genres " \
                      f"FROM content.film_work fw " \
                      f"LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id " \
                      f"LEFT JOIN content.person p ON p.id = pfw.person_id " \
                      f"LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id " \
                      f"LEFT JOIN content.genre g ON g.id = gfw.genre_id " \
                      f"WHERE fw.id IN ({UNION_PERSON_GENRES}) OR fw.id IN %s " \
                      f"GROUP BY fw.id;"

ALL_MODIFIED_PERSONS = f"SELECT " \
                      f"p.id as p_id, " \
                      f"p.full_name, " \
                      f"COALESCE (" \
                      f"json_agg(" \
                      f"DISTINCT jsonb_build_object(" \
                          f"'filmwork_id', fw.id," \
                          f"'roles', pfw.role," \
                          f"'title', fw.title," \
                          f"'imdb_rating', fw.rating)" \
                          f") " \
                          f"FILTER (WHERE fw.id is not null), " \
                          f"'[]') as films " \
                      f"FROM content.person p " \
                      f"LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id " \
                      f"LEFT JOIN content.film_work fw ON fw.id = pfw.film_work_id " \
                      f"WHERE p.id IN ({SQL_PERSONS_WHERE_MOVIE}) OR p.id IN %s " \
                      f"GROUP BY p.id;"

ALL_MODIFIED_GENRES = f"SELECT " \
                      f"g.id as g_id, " \
                      f"g.name " \
                      f"FROM content.genre g " \
                      f"LEFT JOIN content.genre_film_work gfw ON gfw.genre_id = g.id " \
                      f"LEFT JOIN content.film_work fw ON fw.id = gfw.film_work_id " \
                      f"WHERE g.id IN ({SQL_GENRES_WHERE_MOVIE}) OR g.id IN %s " \
                      f"GROUP BY g.id;"