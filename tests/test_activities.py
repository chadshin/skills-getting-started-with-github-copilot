from urllib.parse import quote

from src.app import activities


def test_get_activities(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)
    assert isinstance(data["Chess Club"]["max_participants"], int)


def test_signup_success(client):
    # Arrange
    activity_name = "Debate Team"
    email = "student1@mergington.edu"
    quoted_activity = quote(activity_name, safe="")

    # Act
    response = client.post(
        f"/activities/{quoted_activity}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activities_response = client.get("/activities").json()
    assert email in activities_response[activity_name]["participants"]


def test_signup_duplicate(client):
    # Arrange
    activity_name = "Debate Team"
    email = "duplicate@mergington.edu"
    quoted_activity = quote(activity_name, safe="")

    client.post(
        f"/activities/{quoted_activity}/signup",
        params={"email": email},
    )

    # Act
    duplicate_response = client.post(
        f"/activities/{quoted_activity}/signup",
        params={"email": email},
    )

    # Assert
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Already signed up"


def test_signup_full(client):
    # Arrange
    activity_name = "Soccer Team"
    quoted_activity = quote(activity_name, safe="")
    activities[activity_name]["participants"] = [
        f"user{i}@example.com" for i in range(activities[activity_name]["max_participants"])
    ]

    # Act
    response = client.post(
        f"/activities/{quoted_activity}/signup",
        params={"email": "newstudent@mergington.edu"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_success(client):
    # Arrange
    activity_name = "Swimming Club"
    email = "remove@mergington.edu"
    quoted_activity = quote(activity_name, safe="")
    activities[activity_name]["participants"] = [email]

    # Act
    response = client.delete(
        f"/activities/{quoted_activity}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    activities_response = client.get("/activities").json()
    assert email not in activities_response[activity_name]["participants"]


def test_unregister_not_found(client):
    # Arrange
    activity_name = "Swimming Club"
    quoted_activity = quote(activity_name, safe="")

    # Act
    response = client.delete(
        f"/activities/{quoted_activity}/signup",
        params={"email": "missing@mergington.edu"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Participant not found"


def test_root_redirects_to_static(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"
