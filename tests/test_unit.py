from datetime import date
from typing import Dict, Union

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
import pytest

from app import models
from app.actions import (get_trainer as z, get_trainer_by_name as y, get_trainers as x,
                         create_trainer as w, add_trainer_pokemon as v,
                         add_trainer_item as u, get_items as t, get_pokemon as s, get_pokemons as r)
from app.models import Trainer as q
from app.schemas import PokemonCreate as p, ItemCreate as o
from main import app

client = TestClient(app)


def init_test_database():
    # Créer une session de base de données en mémoire pour les tests
    engine = create_engine('sqlite:///:memory:')
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    database = SessionLocal()

    # Créer les tables dans la base de données de test
    models.Base.metadata.create_all(bind=engine)

    return database


def test_get_trainer():
    database = init_test_database()

    test_birthdate = date(2000, 1, 1)
    fake_trainer = q(id=1, name="Test Trainer", birthdate=test_birthdate)
    database.add(fake_trainer)
    database.commit()
    result = z(database, trainer_id=1)
    assert result is not None
    assert result.id == 1
    assert result.name == "Test Trainer"
    assert str(result.birthdate) == "2000-01-01"

    database.close()


def test_get_trainer_by_name():
    # Initialiser la base de données de test
    database = init_test_database()

    # Ajouter un entraîneur à la base de données pour les tests
    test_trainer1 = models.Trainer(id=1, name="Test Trainer 1", birthdate=date(2000, 1, 1))
    test_trainer2 = models.Trainer(id=2, name="Test Trainer 2", birthdate=date(2000, 2, 2))
    test_trainer3 = models.Trainer(id=3, name="Test Trainer 3", birthdate=date(2000, 3, 3))

    database.add_all([test_trainer1, test_trainer2, test_trainer3])
    database.commit()

    # Appeler la fonction get_trainer_by_name avec un nom d'entraîneur
    result = y(database, name="Test Trainer 2")

    # Vérifier que le résultat contient l'entraîneur correspondant
    assert result is not None
    assert len(result) == 1
    assert result[0].id == 2
    assert result[0].name == "Test Trainer 2"

    # Nettoyer la base de données après les tests
    database.close()


def test_get_trainers():
    database = init_test_database()

    test_trainer1 = models.Trainer(id=1, name="Test Trainer 1", birthdate=date(2000, 1, 1))
    test_trainer2 = models.Trainer(id=2, name="Test Trainer 2", birthdate=date(2000, 2, 2))
    test_trainer3 = models.Trainer(id=3, name="Test Trainer 3", birthdate=date(2000, 3, 3))

    database.add_all([test_trainer1, test_trainer2, test_trainer3])
    database.commit()

    result = x(database)

    assert result is not None
    assert len(result) == 3
    assert result[0].name == "Test Trainer 1"
    assert result[1].name == "Test Trainer 2"
    assert result[2].name == "Test Trainer 3"

    database.close()


def test_create_trainer():
    database = init_test_database()

    test_trainer1 = models.Trainer(id=1, name="Test Trainer 1", birthdate=date(2000, 1, 1))

    created_trainer = w(database, trainer=test_trainer1)

    assert created_trainer is not None
    assert created_trainer.id is not None
    assert created_trainer.name == "Test Trainer 1"
    assert created_trainer.birthdate == date(2000, 1, 1)

    retrieved_trainer = z(database, trainer_id=created_trainer.id)
    assert retrieved_trainer is not None
    assert retrieved_trainer.id == created_trainer.id
    assert retrieved_trainer.name == "Test Trainer 1"
    assert retrieved_trainer.birthdate == date(2000, 1, 1)

    database.close()


def create_pokemon_create(data: Dict[str, Union[int, str]]) -> p:
    return p(**data)


def test_add_trainer_pokemon():
    database = init_test_database()

    test_trainer1 = models.Trainer(id=1, name="Test Trainer 1", birthdate=date(2000, 1, 1))
    created_trainer = w(database, trainer=test_trainer1)

    assert created_trainer is not None

    test_pokemon_data = {"api_id": 1, "custom_name": "Test Pokemon 1"}
    test_pokemon_create = create_pokemon_create(test_pokemon_data)

    created_pokemon = v(database, test_pokemon_create, created_trainer.id)
    assert created_pokemon is not None

    # Vérifier que le Pokémon a été correctement créé et lié à l'entraîneur
    assert created_pokemon.id is not None
    assert created_pokemon.api_id == 1
    assert created_pokemon.custom_name == "Test Pokemon 1"
    assert created_pokemon.trainer_id == created_trainer.id

    # Vérifier que le Pokémon peut être récupéré de la base de données
    retrieved_pokemon = (
        database.query(models.Pokemon).filter(models.Pokemon.id ==
                                              created_pokemon.id).first())
    assert retrieved_pokemon is not None
    assert retrieved_pokemon.id == created_pokemon.id
    assert retrieved_pokemon.api_id == 1
    assert retrieved_pokemon.custom_name == "Test Pokemon 1"
    assert retrieved_pokemon.trainer_id == created_trainer.id

    # Nettoyer la base de données après les tests
    database.close()


def create_item_create(data: dict) -> o:
    return o(**data)


def test_add_trainer_item():
    database = init_test_database()

    test_trainer1 = models.Trainer(id=1, name="Test Trainer 1", birthdate=date(2000, 1, 1))
    created_trainer = w(database, trainer=test_trainer1)
    assert created_trainer is not None

    test_item_data = {"name": "Item 1", "description": "Item 1 description"}
    test_item_create = create_item_create(test_item_data)

    created_item = u(database, test_item_create, test_trainer1.id)
    assert created_item is not None

    # Vérifier que l'item a été correctement créé et lié à l'entraîneur
    assert created_item.id is not None
    assert created_item.name == "Item 1"
    assert created_item.description == "Item 1 description"
    assert created_item.trainer_id == created_trainer.id

    # Vérifier que l'item peut être récupéré de la base de données
    retrieved_item = database.query(models.Item).filter(models.Item.id == created_item.id).first()
    assert retrieved_item is not None
    assert retrieved_item.id == created_item.id
    assert retrieved_item.name == "Item 1"
    assert retrieved_item.description == "Item 1 description"
    assert retrieved_item.trainer_id == created_trainer.id

    # Nettoyer la base de données après les tests
    database.close()


def test_get_items():
    # Initialiser la base de données de test
    database = init_test_database()

    test_trainer_data = models.Trainer(id=1, name="Test Trainer 1", birthdate=date(2000, 1, 1))
    created_trainer = w(database, trainer=test_trainer_data)
    assert created_trainer is not None
    items_to_add = [
        models.Item(name="Item 1", description="Item 1 description", trainer_id=created_trainer.id),
        models.Item(name="Item 2", description="Item 2 description", trainer_id=created_trainer.id),
        models.Item(name="Item 3", description="Item 3 description", trainer_id=created_trainer.id),
    ]

    # Ajouter les items à la session de base de données
    database.add_all(items_to_add)
    database.commit()

    # Appeler la fonction get_items pour récupérer les items
    retrieved_items = t(database)

    # Vérifier que le nombre d'items récupérés correspond au nombre d'items ajoutés
    assert len(retrieved_items) == len(items_to_add)

    # Vérifier que les détails des items récupérés correspondent aux détails ajoutés
    for retrieved_item, added_item in zip(retrieved_items, items_to_add):
        assert retrieved_item.id == added_item.id
        assert retrieved_item.name == added_item.name
        assert retrieved_item.description == added_item.description
        assert retrieved_item.trainer_id == added_item.trainer_id

    # Nettoyer la base de données après les tests
    database.close()


def test_get_pokemon():
    # Initialiser la base de données de test
    database = init_test_database()

    # Créer un entraîneur pour le test
    test_trainer_data = models.Trainer(id=1, name="Test Trainer 1", birthdate=date(2000, 1, 1))
    created_trainer = w(database, trainer=test_trainer_data)
    assert created_trainer is not None

    # Créer une liste d'objets Pokemon
    pokemons_to_add = [
        models.Pokemon(api_id=1,
                       name="Pokemon 1",
                       custom_name="Custom 1",
                       trainer_id=created_trainer.id),
        models.Pokemon(api_id=2,
                       name="Pokemon 2",
                       custom_name="Custom 2",
                       trainer_id=created_trainer.id),
        models.Pokemon(api_id=3,
                       name="Pokemon 3",
                       custom_name="Custom 3",
                       trainer_id=created_trainer.id),
    ]

    # Ajouter les Pokémon à la session de base de données
    database.add_all(pokemons_to_add)
    database.commit()

    # Appeler la fonction get_pokemon pour récupérer un Pokémon par son id
    retrieved_pokemon = s(database, pokemon_id=pokemons_to_add[0].id)

    # Vérifier que le Pokémon récupéré correspond au Pokémon ajouté
    assert retrieved_pokemon is not None
    assert retrieved_pokemon.id == pokemons_to_add[0].id
    assert retrieved_pokemon.api_id == pokemons_to_add[0].api_id
    assert retrieved_pokemon.name == pokemons_to_add[0].name
    assert retrieved_pokemon.custom_name == pokemons_to_add[0].custom_name
    assert retrieved_pokemon.trainer_id == pokemons_to_add[0].trainer_id

    # Nettoyer la base de données après les tests
    database.close()


def test_get_pokemons():
    # Initialiser la base de données de test
    database = init_test_database()

    # Créer un entraîneur pour le test
    test_trainer_data = models.Trainer(id=1, name="Test Trainer 1", birthdate=date(2000, 1, 1))
    created_trainer = w(database, trainer=test_trainer_data)
    assert created_trainer is not None

    # Créer une liste d'objets Pokemon
    pokemons_to_add = [
        models.Pokemon(api_id=1,
                       name="Pokemon 1",
                       custom_name="Custom 1",
                       trainer_id=created_trainer.id),
        models.Pokemon(api_id=2,
                       name="Pokemon 2",
                       custom_name="Custom 2",
                       trainer_id=created_trainer.id),
        models.Pokemon(api_id=3,
                       name="Pokemon 3",
                       custom_name="Custom 3",
                       trainer_id=created_trainer.id),
    ]

    # Ajouter les Pokémon à la session de base de données
    database.add_all(pokemons_to_add)
    database.commit()

    # Appeler la fonction get_pokemons pour récupérer tous les Pokémon
    retrieved_pokemons = r(database)

    # Vérifier que le nombre de Pokémon récupérés correspond au nombre de Pokémon ajoutés
    assert len(retrieved_pokemons) == len(pokemons_to_add)

    # Vérifier que les détails des Pokémon récupérés correspondent aux détails ajoutés
    for retrieved_pokemon, added_pokemon in zip(retrieved_pokemons, pokemons_to_add):
        assert retrieved_pokemon.id == added_pokemon.id
        assert retrieved_pokemon.api_id == added_pokemon.api_id
        assert retrieved_pokemon.name == added_pokemon.name
        assert retrieved_pokemon.custom_name == added_pokemon.custom_name
        assert retrieved_pokemon.trainer_id == added_pokemon.trainer_id

    # Nettoyer la base de données après les tests
    database.close()


def test_get_pokemon_count():
    # Initialiser la base de données de test
    database = init_test_database()

    # Créer un entraîneur pour le test
    test_trainer_data = models.Trainer(id=1,
                                       name="Test Trainer 1",
                                       birthdate=date(2000, 1, 1))
    created_trainer = w(database, trainer=test_trainer_data)
    assert created_trainer is not None

    # Créer une liste d'objets Pokemon
    pokemons_to_add = [
        models.Pokemon(api_id=1,
                       name="Pokemon 1",
                       custom_name="Custom 1",
                       trainer_id=created_trainer.id),
        models.Pokemon(api_id=2,
                       name="Pokemon 2",
                       custom_name="Custom 2",
                       trainer_id=created_trainer.id),
        models.Pokemon(api_id=3,
                       name="Pokemon 3",
                       custom_name="Custom 3",
                       trainer_id=created_trainer.id),
    ]

    # Ajouter les Pokémon à la session de base de données
    database.add_all(pokemons_to_add)
    database.commit()
    # Appeler la méthode get_pokemon_count et vérifier le résultat
    count = created_trainer.get_pokemon_count()
    assert count == len(pokemons_to_add)

    # Nettoyer la base de données après les tests
    database.close()


def test_trainer_str_representation():
    # Initialiser la base de données de test
    database = init_test_database()

    # Créer un entraîneur pour le test
    test_trainer_data = models.Trainer(id=1,
                                       name="Test Trainer 1",
                                       birthdate=date(2000, 1, 1))
    created_trainer = w(database, trainer=test_trainer_data)
    assert created_trainer is not None

    # Appeler la méthode __str__
    str_representation = x(created_trainer)

    # Vérifier que la représentation sous forme de chaîne correspond à ce à quoi vous vous attendez
    expected_str = (f"Trainer(id={created_trainer.id}, name={created_trainer.name}, "
                    f"birthdate={created_trainer.birthdate})")
    assert str_representation == expected_str

    # Nettoyer la base de données après les tests
    database.close()


def test_pokemon_str_representation():
    # Initialiser la base de données de test
    database = init_test_database()

    # Créer un entraîneur pour le test
    test_trainer1 = models.Trainer(id=1,
                                   name="Test Trainer 1",
                                   birthdate=date(2000, 1, 1))
    created_trainer = w(database, trainer=test_trainer1)

    assert created_trainer is not None

    test_pokemon_data = {"api_id": 1, "custom_name": "Test Pokemon 1"}
    test_pokemon_create = z(test_pokemon_data)

    created_pokemon = v(database,
                                          test_pokemon_create, created_trainer.id)
    assert created_pokemon is not None

    # Appeler la méthode __str__
    str_representation = q(created_pokemon)

    # Vérifier que la représentation sous forme de chaîne correspond à ce à quoi vous vous attendez
    expected_str = (f"Pokemon(id={created_pokemon.id}, "
                    f"name={created_pokemon.name}, "
                    f"custom_name={created_pokemon.custom_name})")
    assert str_representation == expected_str

    # Nettoyer la base de données après les tests
    database.close()


def test_pokemon_to_dict():
    # Initialiser la base de données de test
    database = init_test_database()

    # Créer un entraîneur pour le test
    test_trainer1 = models.Trainer(id=1,
                                   name="Test Trainer 1",
                                   birthdate=date(2000, 1, 1))
    created_trainer = w(database, trainer=test_trainer1)

    assert created_trainer is not None

    test_pokemon_data = {"api_id": 1, "custom_name": "Test Pokemon 1"}
    test_pokemon_create = z(test_pokemon_data)

    created_pokemon = v(database,
                                          test_pokemon_create, created_trainer.id)
    assert created_pokemon is not None

    # Appeler la méthode to_dict
    pokemon_dict = y(created_pokemon)

    # Vérifier que le dictionnaire correspond à ce à quoi vous vous attendez
    expected_dict = {
        "id": created_pokemon.id,
        "api_id": created_pokemon.api_id,
        "name": created_pokemon.name,
        "custom_name": created_pokemon.custom_name,
        "trainer_id": created_pokemon.trainer_id
    }
    assert pokemon_dict == expected_dict

    # Nettoyer la base de données après les tests
    database.close()


def test_item_str_representation():
    # Initialiser la base de données de test
    database = init_test_database()

    # Créer un entraîneur pour le test
    test_trainer1 = models.Trainer(id=1,
                                   name="Test Trainer 1",
                                   birthdate=date(2000, 1, 1))
    created_trainer = w(database, trainer=test_trainer1)
    assert created_trainer is not None

    test_item_data = {"name": "Item 1", "description": "Item 1 description"}
    test_item_create = z(test_item_data)

    created_item = v(database, test_item_create, test_trainer1.id)
    assert created_item is not None

    # Appeler la méthode __str__
    str_representation = q(created_item)

    # Vérifier que la représentation sous forme de chaîne correspond à ce à quoi vous vous attendez
    expected_str = f"Item(id={created_item.id}, name={created_item.name})"
    assert str_representation == expected_str

    # Nettoyer la base de données après les tests
    database.close()


def test_item_to_dict():
    # Initialiser la base de données de test
    database = init_test_database()

    # Créer un entraîneur pour le test
    test_trainer1 = models.Trainer(id=1,
                                   name="Test Trainer 1",
                                   birthdate=date(2000, 1, 1))
    created_trainer = w(database, trainer=test_trainer1)
    assert created_trainer is not None

    test_item_data = {"name": "Item 1", "description": "Item 1 description"}
    test_item_create = z(test_item_data)

    created_item = v(database, test_item_create, test_trainer1.id)
    assert created_item is not None

    # Appeler la méthode to_dict
    item_dict = y(created_item)

    # Vérifier que le dictionnaire correspond à ce à quoi vous vous attendez
    expected_dict = {
        "id": created_item.id,
        "name": created_item.name,
        "description": created_item.description,
        "trainer_id": created_item.trainer_id
    }
    assert item_dict == expected_dict

    # Nettoyer la base de données après les tests
    database.close()
