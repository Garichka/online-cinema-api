def test_get_movies_pagination(client, auth_headers):
    response = client.get("/movies?skip=0&limit=10", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_movie_detail_not_found(client, auth_headers):
    response = client.get("/movies/999999", headers=auth_headers)
    assert response.status_code == 404


def test_movie_detail_cache_miss_and_hit(client, auth_headers, movie_in_db):
    movie_id = movie_in_db

    res1 = client.get(f"/movies/{movie_id}", headers=auth_headers)
    assert res1.status_code == 200

    res2 = client.get(f"/movies/{movie_id}", headers=auth_headers)
    assert res2.status_code == 200
    assert res1.json() == res2.json()
