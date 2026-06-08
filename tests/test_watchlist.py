def test_add_to_watchlist(client, auth_headers, movie_in_db):
    response = client.post(
        "/watchlist/",
        json={"movie_id": movie_in_db},
        headers=auth_headers,
    )
    assert response.status_code == 201


def test_duplicate_watchlist(client, auth_headers, movie_in_db):
    client.post("/watchlist/", json={"movie_id": movie_in_db}, headers=auth_headers)

    response = client.post(
        "/watchlist/",
        json={"movie_id": movie_in_db},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_watchlist_movie_not_found(client, auth_headers):
    response = client.post(
        "/watchlist/",
        json={"movie_id": 999999},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_watchlist_order(client, auth_headers, two_movies_in_db):
    movie_id_first, movie_id_second = two_movies_in_db

    client.post("/watchlist/", json={"movie_id": movie_id_first}, headers=auth_headers)
    client.post("/watchlist/", json={"movie_id": movie_id_second}, headers=auth_headers)

    res = client.get("/watchlist", headers=auth_headers)
    assert res.status_code == 200

    data = res.json()
    assert data[0]["movie"]["id"] == movie_id_second
