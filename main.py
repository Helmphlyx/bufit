import os

from flask import render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from sqlite_utilities import SqliteUtilites
from flask import Blueprint
from flask_login import login_required, current_user
from models import User

from settings import settings

DATABASE_NAME = settings.DATABASE_NAME
main = Blueprint("main", __name__)


# Generic DB Queries
def get_exercise(exercise_id: int):
    db_utils = SqliteUtilites(DATABASE_NAME)
    exercise_artifact = db_utils.execute(
        "SELECT e.id, e.name, e.description, e.created, m.muscle,"
        " m.muscle_latin FROM exercises e JOIN muscles m on e.muscle = m.id"
        f" WHERE e.id = {exercise_id}",
        fetch_all=False,
    )

    if exercise_artifact is None:
        abort(404)
    return exercise_artifact


def get_workout(workout_id: int):
    db_utils = SqliteUtilites(DATABASE_NAME)
    exercise_artifact = db_utils.execute(
        f"SELECT * FROM workouts WHERE id = {workout_id}"
    )

    if exercise_artifact is None:
        abort(404)
    return exercise_artifact


def get_exercises_for_workout(workout_id: int):
    db_utils = SqliteUtilites(DATABASE_NAME)
    selected_exercises_artifact = db_utils.execute(
        "SELECT a.id, a.name, a.muscle, b.num_sets, b.num_reps, b.num_rest,"
        " b.id AS WorkoutExerciseID FROM workout_exercises b JOIN exercises a"
        f" ON a.id = b.ExercisesID AND b.WorkoutID = {workout_id}",
        fetch_all=True,
    )

    if selected_exercises_artifact is None:
        print("aborted")
        abort(404)
    return selected_exercises_artifact


def get_selected_exercise(exercise_id: int):
    db_utils = SqliteUtilites(DATABASE_NAME)
    selected_exercise_artifact = db_utils.execute(
        "SELECT b.id, b.num_sets, b.num_reps, b.num_rest, b.notes, a.name AS"
        " WorkoutName, a.id as WorkoutID FROM workout_exercises b JOIN"
        f" workouts a ON a.id = b.WorkoutID WHERE b.id = {exercise_id}"
    )

    if selected_exercise_artifact is None:
        abort(404)
    return selected_exercise_artifact


def get_all_muscles():
    db_utils = SqliteUtilites(DATABASE_NAME)
    muscles = db_utils.execute("SELECT * FROM muscles", fetch_all=True)
    return [muscle["muscle"] for muscle in muscles]


# Pages
@main.route("/home")
@login_required
def home():
    return render_template("home.html")


@main.route("/create_exercise", methods=("GET", "POST"))
@login_required
def create_exercise():
    muscles = get_all_muscles()

    if request.method == "POST":
        name = request.form.get("name")
        muscle = request.form.get("muscle")
        description = request.form.get("description")
        image = request.files["image"]

        if not name:
            flash("Exercise name is required!")
        else:
            if not image:
                image_path = "static/images/coming_soon.jpg"
            else:
                image_path = os.path.join(
                    "static/images/", secure_filename(image.filename)
                )
                image.save(image_path)

            sql_utils = SqliteUtilites(DATABASE_NAME)
            muscle_id = sql_utils.execute(
                f"SELECT id FROM muscles WHERE muscles.muscle = '{muscle}'"
            )[0]
            sql_utils.execute(
                "INSERT INTO exercises (name, muscle, description, image_url)"
                f" VALUES ('{name}', '{muscle_id}', '{description}',"
                f" '{image_path}')",
                commit=True,
            )
            return redirect(url_for("main.home"))
    return render_template("create_exercise.html", muscles=muscles)


@main.route("/create_workout", methods=["GET", "POST"])
@login_required
def create_workout():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description", "")
        db_utils = SqliteUtilites(DATABASE_NAME)

        workout_id = db_utils.execute(
            "INSERT INTO workouts (name, user_id, description) VALUES"
            f" ('{name}', {current_user.id}, '{description}')",
            row_id=True,
            commit=True,
        )
        # create workout
        return redirect(url_for("main.edit_workout", workout_id=workout_id))
    return render_template("create_workout.html")


@main.route("/edit_workout/<int:workout_id>", methods=["GET", "POST"])
@login_required
def edit_workout(workout_id):
    db_utils = SqliteUtilites(DATABASE_NAME)
    selected_workout = get_workout(workout_id)
    exercises = db_utils.execute("SELECT * FROM exercises", fetch_all=True)

    if request.method == "POST":
        exercise_id = request.form.get("exercise")
        num_sets = request.form.get("num_sets", 0)
        num_reps = request.form.get("num_reps", 0)
        num_rest = request.form.get("num_rest", 0)
        notes = request.form.get("notes", 0)

        if exercise_id:
            db_utils.execute(
                "INSERT INTO workout_exercises (WorkoutID, ExercisesID,"
                f" num_sets, num_reps, num_rest, notes) VALUES({workout_id},"
                f" {exercise_id}, {num_sets}, {num_reps}, {num_rest},"
                f" '{notes}')",
                commit=True,
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
    db_utils = SqliteUtilites(DATABASE_NAME)
    exercises = db_utils.execute(
        "SELECT * FROM exercises WHERE name IN ( SELECT exercise FROM"
        f" exercise_likes WHERE user_id = {current_user.id})",
        fetch_all=True,
    )

    workouts = db_utils.execute(
        "SELECT * FROM workouts WHERE name IN ( SELECT workout FROM"
        f" workout_likes WHERE user_id = {current_user.id})",
        fetch_all=True,
    )
    return render_template(
        "library.html", exercises=exercises, workouts=workouts
    )


@main.route("/search_exercises", methods=("GET", "POST"))
@login_required
def search_exercises():
    db_utils = SqliteUtilites(DATABASE_NAME)

    muscles = get_all_muscles()
    muscles.insert(0, "All")

    if request.method == "POST":
        muscle = request.form.get("muscle")
        if muscle == "All":
            exercises = db_utils.execute(
                "SELECT e.id, e.name, e.description, e.created, e.image_url,"
                " m.muscle, m.muscle_latin FROM exercises e JOIN muscles m on"
                " e.muscle = m.id",
                fetch_all=True,
            )
        else:
            exercises = db_utils.execute(
                "SELECT e.id, e.name, e.description, e.created, e.image_url,"
                " m.muscle, m.muscle_latin FROM exercises e JOIN muscles m on"
                f" e.muscle = m.id WHERE m.muscle = '{muscle}'",
                fetch_all=True,
            )
        redirect(url_for("main.search_exercises", muscle=muscle))
    else:
        exercises = db_utils.execute(
            "SELECT e.id, e.name, e.description, e.created, m.muscle,"
            " m.muscle_latin FROM exercises e JOIN muscles m on e.muscle ="
            " m.id",
            fetch_all=True,
        )
    return render_template(
        "search_exercises.html", exercises=exercises, muscles=muscles
    )


@main.route("/search_workouts")
@login_required
def search_workouts():
    db_utils = SqliteUtilites(DATABASE_NAME)
    workouts = db_utils.execute(
        "SELECT a.name, a.description, a.id, a.created, b.name AS author FROM"
        " workouts a JOIN users b ON a.user_id = b.id",
        fetch_all=True,
    )

    return render_template("search_workouts.html", workouts=workouts)


@main.route("/<int:exercise_id>", methods=("GET", "POST"))
@login_required
def exercise(exercise_id):
    exercise_artifact = get_exercise(exercise_id)

    if request.method == "POST":
        db_utils = SqliteUtilites(DATABASE_NAME)
        db_utils.execute(
            "INSERT INTO exercise_likes (user_id, exercise) VALUES"
            f" ({current_user.id}, '{exercise_artifact['name']}')",
            commit=True,
        )
        flash(
            f"{exercise_artifact['name']} has been added to your Liked"
            " Exercises"
        )
        return redirect(url_for("main.home"))
    return render_template("exercise.html", exercise=exercise_artifact)


@main.route("/workout/<int:workout_id>", methods=("GET", "POST"))
@login_required
def workout(workout_id):
    workout_artifact = get_workout(workout_id)
    db_utils = SqliteUtilites(DATABASE_NAME)

    if request.method == "POST":
        db_utils.execute(
            "INSERT INTO workout_likes (user_id, workout) VALUES"
            f" ({current_user.id}, '{workout_artifact['name']}')",
            commit=True,
        )
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


# @main.route("/<int:`workout_id`>/edit_workout", methods=("GET", "POST"))
# @login_required
# def edit_workout(workout_id):
#     workout_artifact = get_workout(workout_id)
#
#     if request.method == "POST":
#         name = request.form["name"]
#         description = request.form["description"]
#
#         if not name:
#             flash("Name is required!")
#         else:
#             db_utils = SqliteUtilites(DATABASE_NAME)
#             db_utils.execute(
#                 f"UPDATE workouts SET name = '{name}',"
#                 f" description = '{description}' WHERE id = {id}",
#                 commit=True,
#             )
#             return redirect(url_for("main.search_workouts"))
#
#     selected_exercises = get_exercises_for_workout(workout_id)
#
#     return render_template(
#         "edit_workout.html",
#         workout=workout_artifact,
#         selected_exercises=selected_exercises,
#     )


@main.route("/update_workout_order_", methods=["POST"])
def update_workout_order():
    print(request.form.get("order_data"))

    return redirect(url_for("main.edit_workout", workout_id="1"))


@main.route("/<int:workout_id>/edit_workout_title", methods=("GET", "POST"))
@login_required
def edit_workout_title(workout_id):
    workout_artifact = get_workout(workout_id)

    if request.method == "POST":
        title = request.form["name"]

        if not title:
            flash("Title is required!")
        else:
            db_utils = SqliteUtilites(DATABASE_NAME)
            db_utils.execute(
                f"UPDATE workouts SET name = '{title}' WHERE id ="
                f" {workout_id};",
                commit=True,
            )
            return redirect(
                url_for("main.edit_workout", workout_id=workout_id)
            )

    return render_template("edit_workout_title.html", workout=workout_artifact)


@main.route(
    "/<int:workout_id>/edit_workout_description", methods=("GET", "POST")
)
@login_required
def edit_workout_description(workout_id):
    workout_artifact = get_workout(workout_id)

    if request.method == "POST":
        description = request.form["description"]

        if not description:
            flash("Description is required!")
        else:
            db_utils = SqliteUtilites(DATABASE_NAME)
            db_utils.execute(
                f"UPDATE workouts SET description = '{description}' WHERE id ="
                f" {workout_id};",
                commit=True,
            )
            return redirect(
                url_for("main.edit_workout", workout_id=workout_id)
            )

    return render_template(
        "edit_workout_description.html", workout=workout_artifact
    )


@main.route("/<int:id>/edit", methods=("GET", "POST"))
@login_required
def edit(id):
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
            db_utils = SqliteUtilites(DATABASE_NAME)
            muscle_id = db_utils.execute(
                f"SELECT id FROM muscles WHERE muscles.muscle = '{muscle}'"
            )[0]

            if not image:
                db_utils.execute(
                    f"UPDATE exercises SET name = '{name}', muscle ="
                    f" '{muscle_id}', description = '{description}' WHERE id ="
                    f" {id}",
                    commit=True,
                )
            else:
                image_path = os.path.join(
                    "static/images/", secure_filename(image.filename)
                )
                image.save(image_path)

                db_utils.execute(
                    f"UPDATE exercises SET name = '{name}', muscle ="
                    f" '{muscle_id}', description = '{description}',"
                    f" image_url='{image_path}' WHERE id = {id}",
                    commit=True,
                )

            return redirect(url_for("main.search_exercises"))

    return render_template(
        "edit.html", exercise=exercise_artifact, muscles=muscles
    )


@main.route("/<int:id>/edit_workout_exercise", methods=("GET", "POST"))
@login_required
def edit_workout_exercise(id):
    exercise_artifact = get_selected_exercise(id)
    workout_id = exercise_artifact["WorkoutID"]

    if request.method == "POST":
        print("post")
        num_sets = request.form.get("num_sets", 0)
        num_reps = request.form.get("num_reps", 0)
        num_rest = request.form.get("num_rest", 0)
        notes = request.form.get("notes", 0)

        print(f"{num_sets} {num_reps} {num_rest} {notes}")
        db_utils = SqliteUtilites(DATABASE_NAME)
        db_utils.execute(
            f"UPDATE workout_exercises SET num_sets = '{num_sets}', num_reps ="
            f" '{num_reps}', num_rest = '{num_rest}', notes = '{notes}' WHERE"
            f" id = {id}",
            commit=True,
        )
        return redirect(url_for("main.edit_workout", workout_id=workout_id))
    print("getted")
    return render_template(
        "edit_workout_exercise.html", exercise=exercise_artifact
    )


@main.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id: int):
    exercise_artifact = get_exercise(id)

    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute(f"DELETE FROM exercises WHERE id = {id}", commit=True)

    flash('"{}" was successfully deleted!'.format(exercise_artifact["name"]))
    return redirect(url_for("main.home"))


@main.route("/<int:id>/delete_workout_exercise", methods=("POST",))
@login_required
def delete_workout_exercise(id: int):
    exercise_artifact = get_selected_exercise(id)
    workout_id = exercise_artifact["WorkoutID"]
    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute(
        f"DELETE FROM workout_exercises WHERE id = {id}", commit=True
    )

    # flash('"{}" was successfully deleted!'.format(exercise_artifact["name"]))
    return redirect(url_for("main.edit_workout", workout_id=workout_id))


@main.route("/<int:id>/delete_workout", methods=("POST",))
@login_required
def delete_workout(id: int):
    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute(f"DELETE FROM workouts WHERE id = {id}", commit=True)

    flash('"{}" was successfully deleted!'.format(current_user.name))
    return redirect(url_for("main.home"))
