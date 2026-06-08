def test_create_review(client, auth_headers, movie_in_db):
    response = client.post(
        "/reviews/",
        json={"movie_id": movie_in_db, "rating": 8},
        headers=auth_headers,
    )
    assert response.status_code == 201


def test_duplicate_review(client, auth_headers, movie_in_db):
    client.post(
        "/reviews/",
        json={"movie_id": movie_in_db, "rating": 8},
        headers=auth_headers,
    )
    response = client.post(
        "/reviews/",
        json={"movie_id": movie_in_db, "rating": 7},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_rating_validation(client, auth_headers, movie_in_db):
    response = client.post(
        "/reviews/",
        json={"movie_id": movie_in_db, "rating": 11},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_review_for_nonexistent_movie(client, auth_headers):
    response = client.post(
        "/reviews/",
        json={"movie_id": 999999, "rating": 5},
        headers=auth_headers,
    )
    assert response.status_code == 404
