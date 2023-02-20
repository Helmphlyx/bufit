import os
from typing import Optional

from flask import render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from sqlite_utilities import SqliteUtilites
from flask import Blueprint
from flask_login import login_required, current_user
from models import User

from settings import settings

from helpers import sanitize_input

DEFAULT_EXERCISE_IMAGE_PATH = "/static/img/example-exercise-img.jpg"
DATABASE_NAME = settings.DATABASE_NAME
main = Blueprint("main", __name__)


# Generic DB Queries
def get_exercise(exercise_id: int):
    """Get exercise by ID."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    exercise_artifact = db_utils.execute(
        f"SELECT e.id, e.name, e.description, e.created, m.muscle,"
        f" m.muscle_latin, e.image_url FROM exercises e JOIN muscles m on"
        f" e.muscle = m.id WHERE e.id = ?",
        params=(exercise_id,),
        fetch_all=False,
    )

    if exercise_artifact is None:
        abort(404)
    return exercise_artifact


def check_exercise_name_exists(exercise_name: str):
    """Check exercise by name."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    count = db_utils.execute(
        f"SELECT COUNT(id) FROM exercises WHERE name = ?",
        params=(exercise_name,),
    )[0]

    return count > 0


def get_all_exercises_with_muscles():
    """Get all exercises with their muscle group."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    exercises = db_utils.execute(
        "SELECT e.id, e.name, e.description, e.created, e.image_url,"
        " m.muscle, m.muscle_latin FROM exercises e JOIN muscles m on"
        " e.muscle = m.id",
        fetch_all=True,
    )

    return exercises


def get_all_exercises_by_muscles(muscle: str):
    """Get all exercises by a muscle group."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    exercises = db_utils.execute(
        f"SELECT e.id, e.name, e.description, e.created, e.image_url,"
        f" m.muscle, m.muscle_latin FROM exercises e JOIN muscles m on"
        f" e.muscle = m.id WHERE m.muscle = ?",
        params=(muscle,),
        fetch_all=True,
    )
    return exercises


def get_similar_exercises_by_name(exercise_name: str):
    """Get similar exercises by name."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    exercises = db_utils.execute(
        f"SELECT e.id, e.name, e.description, e.created, e.image_url,"
        f" m.muscle, m.muscle_latin FROM exercises e JOIN muscles m on"
        f" e.muscle = m.id WHERE upper(e.name) LIKE upper('%' || ? || '%')",
        params=(exercise_name,),
        fetch_all=True,
    )
    return exercises


def get_liked_exercises(user_id: int):
    """Get all liked exercises by a given user id."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    liked_exercises = db_utils.execute(
        f"SELECT * FROM exercises WHERE name IN ( SELECT exercise FROM"
        f" exercise_likes WHERE user_id = ?)",
        params=(user_id,),
        fetch_all=True,
    )

    return liked_exercises


def like_exercise(user_id: int, exercise_name: str):
    """Get all liked exercises by a given user id."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute(
        f"INSERT INTO exercise_likes (user_id, exercise) VALUES (?, ?)",
        params=(user_id, exercise_name),
        commit=True,
    )
    return


def create_new_exercise(
    name: str, muscle_id: str, description: str, image_path: str
):
    """Create exercise into exercise table."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute(
        f"INSERT INTO exercises (name, muscle, description, image_url)"
        f" VALUES (?, ?, ?,"
        f" ?)",
        params=(name, muscle_id, description, image_path),
        commit=True,
    )
    return


def delete_exercise(exercise_id: int):
    """Delete exercise in exercise table."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute(
        f"DELETE FROM exercises WHERE id = ?",
        params=(exercise_id,),
        commit=True,
    )
    return


def update_exercise(
    name: str,
    muscle_id: str,
    exercise_id: int,
    description: str,
    image_path: Optional[str] = None,
):
    """Update exercise in exercise table."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    if image_path is None:
        db_utils.execute(
            f"UPDATE exercises SET name = ?, muscle ="
            f" ?, description = ? WHERE id ="
            f" ?",
            params=(name, muscle_id, description, exercise_id),
            commit=True,
        )
    else:
        db_utils.execute(
            f"UPDATE exercises SET name = ?, muscle ="
            f" ?, description = ?,"
            f" image_url = ? WHERE id = ?",
            params=(name, muscle_id, description, image_path, exercise_id),
            commit=True,
        )
    return


def get_workout(workout_id: int):
    """Get workout by ID."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    exercise_artifact = db_utils.execute(
        f"SELECT * FROM workouts WHERE id = ?", params=(workout_id,)
    )

    if exercise_artifact is None:
        abort(404)
    return exercise_artifact


def get_similar_workout_by_name(workout_name: str):
    """Get similar workout by name."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    workouts = db_utils.execute(
        f"SELECT a.name, a.description, a.id, a.created, b.name AS author FROM"
        f" workouts a JOIN users b ON a.user_id = b.id"
        f" WHERE a.name LIKE '%' || ? || '%'",
        params=(workout_name,),
        fetch_all=True,
    )

    return workouts


def check_workout_name_exists(workout_name: str, user_id: int):
    """Check workout by name and user id."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    count = db_utils.execute(
        f"SELECT COUNT(id) FROM workouts WHERE user_id = ? AND name = ?",
        params=(user_id, workout_name),
    )[0]

    return count > 0


def get_all_workouts_with_author_names():
    """Get all workouts with their author's name."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    workouts = db_utils.execute(
        "SELECT a.name, a.description, a.id, a.created, b.name AS author FROM"
        " workouts a JOIN users b ON a.user_id = b.id",
        fetch_all=True,
    )
    return workouts


def get_liked_workout(user_id: int):
    """Get all liked workouts by a given user id."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    liked_workouts = db_utils.execute(
        f"SELECT * FROM workouts WHERE name IN ( SELECT workout FROM"
        f" workout_likes WHERE user_id = ?)",
        params=(user_id,),
        fetch_all=True,
    )

    return liked_workouts


def like_workout(user_id: int, workout_name: str):
    """Like a workout."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute(
        f"INSERT INTO exercise_likes (user_id, exercise) VALUES (?, ?)",
        params=(user_id, workout_name),
        commit=True,
    )
    return


def update_workout_exercise(
    workout_id: int, num_reps, num_sets: int, num_rest: int, notes: str
):
    """Update exercise in workout_exercises table."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute(
        f"UPDATE workout_exercises SET num_sets = ?, num_reps ="
        f" ?, num_rest = ?, notes = ? WHERE"
        f" id = ?",
        params=(num_sets, num_reps, num_rest, notes, workout_id),
        commit=True,
    )
    return


def update_workout_title(workout_id: int, title: str):
    """Update a workout's title."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute(
        f"UPDATE workouts SET name = ? WHERE id = ?;",
        params=(title, workout_id),
        commit=True,
    )
    return


def update_workout_description(workout_id: int, description: str):
    """Update a workout's description."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute(
        f"UPDATE workouts SET description = ? WHERE id = ?;",
        params=(description, workout_id),
        commit=True,
    )
    return


def create_new_workout(name: int, user_id: int, description: str):
    """Create workout into workout table."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    workout_id = db_utils.execute(
        f"INSERT INTO workouts (name, user_id, description) VALUES (?, ?, ?)",
        params=(name, user_id, description),
        row_id=True,
        commit=True,
    )
    return workout_id


def delete_workout_by_id(workout_id: int):
    """Delete workout from workout table."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute(
        f"DELETE FROM workouts WHERE id = ?",
        params=(workout_id,),
        commit=True,
    )
    return


def get_muscle_id_for_muscle(muscle: str):
    """Get workout by ID."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    muscle_id = db_utils.execute(
        f"SELECT id FROM muscles WHERE muscles.muscle = ?", params=(muscle,)
    )[0]

    if muscle_id is None:
        abort(404)
    return muscle_id


def get_exercises_for_workout(workout_id: int):
    """Get exercises for a given workout ID."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    selected_exercises_artifact = db_utils.execute(
        f"SELECT a.id, a.name, a.muscle, b.num_sets, b.num_reps, b.num_rest,"
        f" b.notes, b.id AS WorkoutExerciseID FROM workout_exercises b JOIN"
        f" exercises a ON a.id = b.ExercisesID AND b.WorkoutID = ? ORDER BY"
        f" b.exercise_order",
        params=(workout_id,),
        fetch_all=True,
    )

    if selected_exercises_artifact is None:
        print("aborted")
        abort(404)
    return selected_exercises_artifact


def create_exercise_for_workout(
    workout_id: int,
    exercise_id: str,
    num_sets: int,
    num_reps: int,
    num_rest: int,
    notes: str,
    workout_order: int,
):
    """Create exercise for a given workout ID."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute(
        f"INSERT INTO workout_exercises (WorkoutID, ExercisesID,"
        f" num_sets, num_reps, num_rest, notes, exercise_order)"
        f" VALUES(?, ?, ?, ?,"
        f" ?,  ?, ?)",
        params=(
            workout_id,
            exercise_id,
            num_sets,
            num_reps,
            num_rest,
            notes,
            workout_order,
        ),
        commit=True,
    )

    return


def delete_workout_exercise_by_id(workout_exercise_id: int):
    """Delete exercise from workout."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute(
        f"DELETE FROM workout_exercises WHERE id = ?",
        params=(workout_exercise_id,),
        commit=True,
    )
    return


def get_selected_exercise(exercise_id: int):
    """Get a workout's selected exercise for a given ID."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    selected_exercise_artifact = db_utils.execute(
        f"SELECT b.id, b.num_sets, b.num_reps, b.num_rest, b.notes, a.name AS"
        f" WorkoutName, a.id as WorkoutID FROM workout_exercises b JOIN"
        f" workouts a ON a.id = b.WorkoutID WHERE b.id = ?",
        params=(exercise_id,),
    )

    if selected_exercise_artifact is None:
        abort(404)
    return selected_exercise_artifact


def get_all_muscles():
    """Get all muscle categories."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    muscles = db_utils.execute("SELECT * FROM muscles", fetch_all=True)
    return [muscle["muscle"] for muscle in muscles]


# Routes
@main.route("/home")
@login_required
def home():
    """Home page."""
    return render_template("home.html")


@main.route("/create_exercise", methods=("GET", "POST"))
@login_required
def create_exercise():
    """Create exercise page."""
    muscles = get_all_muscles()

    if request.method == "POST":
        name = sanitize_input(request.form.get("name"))
        muscle = request.form.get("muscle")
        description = sanitize_input(request.form.get("description"))
        image = request.files["image"]

        if not name:
            flash("Exercise name is required!")
        else:
            if check_exercise_name_exists(name):
                flash("Exercise with this name already exists!")
            else:
                # Handle exercise image
                if not image:
                    image_path = DEFAULT_EXERCISE_IMAGE_PATH
                else:
                    image_path = os.path.join(
                        "static/images/", secure_filename(image.filename)
                    )
                    image.save(image_path)

                muscle_id = get_muscle_id_for_muscle(muscle)
                create_new_exercise(name, muscle_id, description, image_path)
                return redirect(url_for("main.home"))
    return render_template("create_exercise.html", muscles=muscles)


@main.route("/create_workout", methods=["GET", "POST"])
@login_required
def create_workout():
    """Create a workout page."""
    if request.method == "POST":
        name = sanitize_input(request.form.get("name"))

        if not name:
            flash("Name is required!")
        else:
            if check_workout_name_exists(name, current_user.id):
                flash(
                    "You have a workout with this name. Please choose a"
                    " different name..."
                )
            else:
                description = sanitize_input(
                    request.form.get("description", "")
                )
                workout_id = create_new_workout(
                    name, current_user.id, description
                )
                return redirect(
                    url_for("main.edit_workout", workout_id=workout_id)
                )
    return render_template("create_workout.html")


@main.route("/edit_workout/<int:workout_id>", methods=["GET", "POST"])
@login_required
def edit_workout(workout_id):
    """Edit workout page."""
    db_utils = SqliteUtilites(DATABASE_NAME)
    selected_workout = get_workout(workout_id)
    exercises = db_utils.execute("SELECT * FROM exercises", fetch_all=True)

    if request.method == "POST":
        exercise_id = request.form.get("exercise")
        num_sets = request.form.get("num_sets", 0)
        num_reps = request.form.get("num_reps", 0)
        num_rest = request.form.get("num_rest", 0)
        notes = request.form.get("notes", 0)
        workout_order = len(selected_workout)

        if exercise_id:
            create_exercise_for_workout(
                workout_id,
                exercise_id,
                num_sets,
                num_reps,
                num_rest,
                notes,
                workout_order,
            )

    selected_exercises = get_exercises_for_workout(workout_id)

    return render_template(
        "edit_workout.html",
        workout=selected_workout,
        exercises=exercises,
        selected_exercises=(selected_exercises or []),
    )


@main.route("/library")
@login_required
def library():
    """User's library page."""
    exercises = get_liked_exercises(current_user.id)
    workouts = get_liked_workout(current_user.id)

    return render_template(
        "library.html", exercises=exercises, workouts=workouts
    )


@main.route("/search_exercises", methods=("GET", "POST"))
@login_required
def search_exercises():
    """Search exercise page."""
    muscles = get_all_muscles()
    muscles.insert(0, "All")

    if request.method == "POST":
        muscle = request.form.get("muscle")
        exercise_search_name = request.form.get("exercise_search_name")
        if muscle == "All":
            exercises = get_all_exercises_with_muscles()
        elif exercise_search_name:
            exercises = get_similar_exercises_by_name(exercise_search_name)
        else:
            exercises = get_all_exercises_by_muscles(muscle)
        redirect(url_for("main.search_exercises", muscle=muscle))
    else:
        exercises = get_all_exercises_with_muscles()
    return render_template(
        "search_exercises.html", exercises=exercises, muscles=muscles
    )


@main.route("/search_workouts", methods=("GET", "POST"))
@login_required
def search_workouts():
    """Search workouts page."""
    if request.method == "POST":
        workout_name = sanitize_input(request.form.get("workout_name"))
        if not workout_name:
            workouts = get_all_workouts_with_author_names()
        else:
            workouts = get_similar_workout_by_name(workout_name)
        redirect(url_for("main.search_workouts", workouts=workouts))
    else:
        workouts = get_all_workouts_with_author_names()

    return render_template("search_workouts.html", workouts=workouts)


@main.route("/<int:exercise_id>", methods=("GET", "POST"))
@login_required
def exercise(exercise_id):
    """Exercise page."""
    exercise_artifact = get_exercise(exercise_id)

    if request.method == "POST":
        like_exercise(current_user.id, exercise_artifact["name"])
        flash(
            f"{exercise_artifact['name']} has been added to your Liked"
            " Exercises"
        )
        return redirect(url_for("main.home"))
    return render_template("exercise.html", exercise=exercise_artifact)


@main.route("/workout/<int:workout_id>", methods=("GET", "POST"))
@login_required
def workout(workout_id):
    """Workout page."""
    workout_artifact = get_workout(workout_id)

    if request.method == "POST":
        like_workout(current_user.id, workout_artifact["name"])
        flash(
            f"{workout_artifact['name']} has been added to your Liked Workouts"
        )
        return redirect(url_for("main.home"))

    selected_exercises = get_exercises_for_workout(workout_id)

    author = User.query.filter(User.id == workout_artifact["user_id"]).first()
    return render_template(
        "workout.html",
        workout=workout_artifact,
        selected_exercises=selected_exercises,
        author=author.name,
    )


@main.route("/update_workout_order_", methods=["POST"])
def update_workout_order():
    """Handles updating workout order."""
    order_data = request.form.get("order_data").split(",")
    order_update_case = [
        f"WHEN {order_index} THEN {order_data.index(order_index)}"
        for order_index in order_data
    ]

    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute(
        f"""
        UPDATE workout_exercises
            SET exercise_order = CASE id
                                {' '.join(case for case in order_update_case)}
                                ELSE 0
                                END
        WHERE id IN({','.join(index for index in order_data)});
        """,
        commit=True,
    )

    workout_id = db_utils.execute(
        f"""
        SELECT WorkoutID FROM workout_exercises WHERE id = {order_data[0]}
        """
    )[0]

    workout_artifact = get_workout(workout_id)
    selected_exercises = get_exercises_for_workout(workout_id)
    author = User.query.filter(User.id == workout_artifact["user_id"]).first()

    return render_template(
        "edit_workout_order.html",
        workout=workout_artifact,
        selected_exercises=selected_exercises,
        author=author,
    )


@main.route("/<int:workout_id>/edit_workout_order", methods=("GET", "POST"))
@login_required
def edit_workout_order(workout_id):
    """Editing workout order page."""
    workout_artifact = get_workout(workout_id)

    selected_exercises = get_exercises_for_workout(workout_id)

    author = User.query.filter(User.id == workout_artifact["user_id"]).first()
    return render_template(
        "edit_workout_order.html",
        workout=workout_artifact,
        selected_exercises=selected_exercises,
        author=author.name,
    )


@main.route("/<int:workout_id>/edit_workout_title", methods=("GET", "POST"))
@login_required
def edit_workout_title(workout_id):
    """Editing workout title page."""
    workout_artifact = get_workout(workout_id)

    if request.method == "POST":
        title = request.form["name"]

        if not title:
            flash("Title is required!")
        else:
            update_workout_title(workout_id, title)
            return redirect(
                url_for("main.edit_workout", workout_id=workout_id)
            )

    return render_template("edit_workout_title.html", workout=workout_artifact)


@main.route(
    "/<int:workout_id>/edit_workout_description", methods=("GET", "POST")
)
@login_required
def edit_workout_description(workout_id):
    """Editing workout description page."""
    workout_artifact = get_workout(workout_id)

    if request.method == "POST":
        description = request.form["description"]

        if not description:
            flash("Description is required!")
        else:
            update_workout_description(workout_id, description)
            return redirect(
                url_for("main.edit_workout", workout_id=workout_id)
            )

    return render_template(
        "edit_workout_description.html", workout=workout_artifact
    )


@main.route("/<int:id>/edit", methods=("GET", "POST"))
@login_required
def edit(id):
    """Edit exercise page."""
    exercise_artifact = get_exercise(id)
    muscles = get_all_muscles()

    if request.method == "POST":
        name = request.form["name"]
        muscle = request.form["muscle"]
        description = request.form["description"]
        image = request.files["image"]

        if not name:
            flash("Name is required!")
        else:
            muscle_id = get_muscle_id_for_muscle(muscle)

            if not image:
                update_exercise(name, muscle_id, id, description)
            else:
                image_path = os.path.join(
                    "static/images/", secure_filename(image.filename)
                )
                image.save(image_path)

                update_exercise(name, muscle_id, id, description, image_path)

            return redirect(url_for("main.search_exercises"))

    return render_template(
        "edit.html", exercise=exercise_artifact, muscles=muscles
    )


@main.route("/<int:id>/edit_workout_exercise", methods=("GET", "POST"))
@login_required
def edit_workout_exercise(id):
    """Edit exercise in a given workout page."""
    exercise_artifact = get_selected_exercise(id)
    workout_id = exercise_artifact["WorkoutID"]
    workout_exercise_id = exercise_artifact["id"]

    if request.method == "POST":
        num_sets = request.form.get("num_sets", 0)
        num_reps = request.form.get("num_reps", 0)
        num_rest = request.form.get("num_rest", 0)
        notes = request.form.get("notes", 0)

        update_workout_exercise(
            workout_exercise_id, num_reps, num_sets, num_rest, notes
        )
        return redirect(url_for("main.edit_workout", workout_id=workout_id))
    return render_template(
        "edit_workout_exercise.html", exercise=exercise_artifact
    )


@main.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id: int):
    """Handles deleting exercise."""
    exercise_artifact = get_exercise(id)

    delete_exercise(id)

    flash('"{}" was successfully deleted!'.format(exercise_artifact["name"]))
    return redirect(url_for("main.home"))


@main.route("/<int:id>/delete_workout_exercise", methods=("POST",))
@login_required
def delete_workout_exercise(id: int):
    """Handles deleting selected exercise from workout."""
    exercise_artifact = get_selected_exercise(id)
    workout_id = exercise_artifact["WorkoutID"]
    delete_workout_exercise_by_id(id)

    # TODO: appropriate flash message
    #  flash('"{}" was successfully deleted!'.format(exercise_artifact["name"]))
    return redirect(url_for("main.edit_workout", workout_id=workout_id))


@main.route("/<int:id>/delete_workout", methods=("POST",))
@login_required
def delete_workout(id: int):
    """Handles deleting workout."""
    delete_workout_by_id(id)
    flash('"{}" was successfully deleted!'.format(current_user.name))
    return redirect(url_for("main.home"))
