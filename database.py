import re
import requests

from flask_sqlalchemy import SQLAlchemy
from sqlite_utilities import SqliteUtilites
from settings import settings

DATABASE_NAME = settings.DATABASE_NAME
db = SQLAlchemy()


def init_db():
    """Initialize database tables and initial values."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute_from_file("db/sql/create_tables.sql")
    init_muscle_table()
    init_exercise_table()


def init_muscle_table():
    """Initialize our muscle categories using external API."""
    muscles_url = "https://wger.de/api/v2/muscle/"
    response = requests.get(muscles_url)
    muscles_data = response.json().get("results", [{}])
    sorted_muscles_data = sorted(muscles_data, key=lambda d: d["id"])
    for muscle_data in sorted_muscles_data:
        db_utils = SqliteUtilites(DATABASE_NAME)
        db_utils.execute(
            "INSERT INTO muscles (muscle, muscle_latin) VALUES"
            f" ('{muscle_data['name']}', '{muscle_data['name_en']}')",
            commit=True,
        )


def init_exercise_table():
    """Initialize our exercise tables using external API."""
    image_url = "https://wger.de/api/v2/exerciseimage/?is_main=true&exercise=3"
    image_url_response = requests.get(image_url)
    exercises_image_data = image_url_response.json().get("results", [{}])

    # Set up exercise images
    image_dict = {}
    default_image = "static/images/coming_soon.jpg"
    for exercise_image_data in exercises_image_data:
        exercise_base = exercise_image_data.get("exercise_base")
        exercise_image = exercise_image_data.get("image", default_image)
        image_dict[exercise_base] = exercise_image

    # Set up exercises
    exercises_url = "https://wger.de/api/v2/exercise/?limit=1000&status=2&language=2&muscles="
    exercises_url_response = requests.get(exercises_url)
    exercises_data = exercises_url_response.json().get("results", [{}])

    for exercise_data in exercises_data:
        db_utils = SqliteUtilites(DATABASE_NAME)
        exercise_name = exercise_data["name"]
        exercise_base = exercise_data["exercise_base"]
        exercise_muscle = (
            exercise_data["muscles"][0]
            if len(exercise_data["muscles"]) > 0
            else "UNKNOWN"
        )
        exercise_description = f"""
        {sanitizer(exercise_data['description'])}
        """

        exercise_image = image_dict.get(exercise_base, default_image)
        db_utils.execute(
            "INSERT INTO exercises (name, muscle, description, image_url)"
            f' VALUES ("{exercise_name}", "{exercise_muscle}",'
            f' "{exercise_description}", "{exercise_image}")',
            commit=True,
        )


def sanitizer(value: str):
    """Remove HTML tags in given value."""
    regex_pattern = re.compile("<.*?>")
    return re.sub(regex_pattern, "", value).replace('"', "'")
