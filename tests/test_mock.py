from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# Test 1 : Création d'un nouveau dresseur + vérification de la création
def test_create_trainer(mocker):
    """
        Création d'un dresseur
    """
    mocker.patch(
        "app.actions.create_trainer",
        return_value={
            "name": "Younes",
            "birthdate": "1990-11-04",
            "id": 1,
            "inventory": [],
            "pokemons": []
        }
    )
    response = client.post("/trainers/", json={"name": "Younes", "birthdate": "1990-11-04"})
    assert response.status_code == 200
    assert (response.json() ==
            {"name": "Younes", "birthdate": "1990-11-04", "id": 1, "inventory": [], "pokemons": []})


def test_get_items(mocker):
    mocker.patch("app.actions.get_items",
                 return_value=[
                     {
                         "name": "test",
                         "description": "test",
                         "id": 1,
                         "trainer_id": 2
                     },
                     {
                         "name": "test2",
                         "description": "test2",
                         "id": 1,
                         "trainer_id": 1
                     }
                 ])
    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_trainers(mocker):
    mocker.patch("app.actions.get_trainers",
                 return_value=[
                     {
                         "name": "Younes",
                         "birthdate": "1990-11-04",
                         "id": 1,
                         "inventory": [],
                         "pokemons": []
                     }
                 ])
    response = client.get("/trainers")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_pokemon(mocker):
    mocker.patch("app.actions.get_pokemons",
                 return_value=[
                     {
                         "api_id": 150,
                         "custom_name": "test",
                         "id": 1,
                         "name": "mewtwo",
                         "trainer_id": 1
                     },
                     {
                         "api_id": 56,
                         "custom_name": "test2",
                         "id": 2,
                         "name": "mankey",
                         "trainer_id": 2
                     }
                 ])
    response = client.get("/pokemons")
    assert response.status_code == 200
    assert len(response.json()) == 2
