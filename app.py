from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

from sqlite_utilities import SqliteUtilites

DATABASE_NAME = "database.db"


# Generic DB Queries
def get_exercise(exercise_id: int):
    db_utils = SqliteUtilites(DATABASE_NAME)
    exercise_artifact = db_utils.execute(
        f"SELECT * FROM exercises WHERE id = {exercise_id}"
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
        "SELECT * FROM workout_exercises b INNER JOIN exercises a ON a.id ="
        f" b.ExercisesID AND b.WorkoutID = {workout_id}",
        fetch_all=True,
    )

    if selected_exercises_artifact is None:
        abort(404)
    return selected_exercises_artifact


# Global Settings
app = Flask(__name__)
app.config["SECRET_KEY"] = "SOME_SECRET_KEY_VALUE"
app.url_map.strict_slashes = False

global_user = None

# Pages
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username:
            flash("Username is required!")
        else:
            # TODO: add login functionality
            # Temporarily use GLOBAL USER
            global_user = username
            return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/create_account", methods=("GET", "POST"))
def create_account():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            flash("Username is required!")
        else:
            # TODO: add login functionality
            return redirect(url_for("login"))
    return render_template("create_account.html")


@app.route("/create_exercise", methods=("GET", "POST"))
def create_exercise():
    if request.method == "POST":
        name = request.form.get("name")
        muscle = request.form.get("muscle")
        description = request.form.get("description")
        if not name:
            flash("Exercise name is required!")
        else:
            sql_utils = SqliteUtilites(DATABASE_NAME)
            sql_utils.execute(
                "INSERT INTO exercises (name, muscle, description) VALUES"
                f" ('{name}', '{muscle}', '{description}')",
                commit=True,
            )
            return redirect(url_for("home"))
    return render_template("create_exercise.html")


@app.route("/create_workout", methods=["GET", "POST"])
def create_workout():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        db_utils = SqliteUtilites(DATABASE_NAME)

        workout_id = db_utils.execute(
            "INSERT INTO workouts (name, author, description) VALUES"
            f" ('{name}', '{global_user}', '{description}')",
            row_id=True,
            commit=True,
        )
        # create workout
        return redirect(
            url_for("add_exercise_to_workout", workout_id=workout_id)
        )
    return render_template("create_workout.html")


@app.route(
    "/add_exercise_to_workout/<int:workout_id>", methods=["GET", "POST"]
)
def add_exercise_to_workout(workout_id):
    db_utils = SqliteUtilites(DATABASE_NAME)
    selected_workout = get_workout(workout_id)
    exercises = db_utils.execute("SELECT * FROM exercises", fetch_all=True)

    if request.method == "POST":
        exercise_id = request.form.get("exercise")
        num_sets = request.form.get("num_sets", 0)
        num_reps = request.form.get("num_reps", 0)

        if exercise_id:
            db_utils.execute(
                "INSERT INTO workout_exercises (WorkoutID, ExercisesID,"
                f" num_sets, num_reps) VALUES({workout_id}, {exercise_id},"
                f" {num_sets}, {num_reps})",
                commit=True,
            )

    selected_exercises = get_exercises_for_workout(workout_id)

    return render_template(
        "add_exercise_to_workout.html",
        workout=selected_workout,
        exercises=exercises,
        selected_exercises=(selected_exercises or []),
    )


@app.route("/library")
def library():
    db_utils = SqliteUtilites(DATABASE_NAME)
    exercises = db_utils.execute(
        "SELECT * FROM exercises WHERE name IN ( SELECT exercise FROM"
        f" exercise_likes WHERE username = '{global_user}')",
        fetch_all=True,
    )

    workouts = db_utils.execute(
        "SELECT * FROM workouts WHERE name IN ( SELECT workout FROM"
        f" workout_likes WHERE username = '{global_user}')",
        fetch_all=True,
    )
    return render_template(
        "library.html", exercises=exercises, workouts=workouts
    )


@app.route("/search_exercises", methods=("GET", "POST"))
def search_exercises():
    db_utils = SqliteUtilites(DATABASE_NAME)

    muscles = db_utils.execute(
        "SELECT DISTINCT muscle FROM exercises", fetch_all=True
    )
    muscles = [muscle["muscle"] for muscle in muscles]

    if request.method == "POST":
        muscle = request.form.get("muscle")
        exercises = db_utils.execute(
            f"SELECT * FROM exercises WHERE muscle = '{muscle}'",
            fetch_all=True,
        )
        redirect(url_for("search_exercises", muscle=muscle))
    else:
        exercises = db_utils.execute("SELECT * FROM exercises", fetch_all=True)
    return render_template(
        "search_exercises.html", exercises=exercises, muscles=muscles
    )


@app.route("/search_workouts")
def search_workouts():
    db_utils = SqliteUtilites(DATABASE_NAME)
    workouts = db_utils.execute("SELECT * FROM workouts", fetch_all=True)
    return render_template("search_workouts.html", workouts=workouts)


@app.route("/<int:exercise_id>", methods=("GET", "POST"))
def exercise(exercise_id):
    exercise_artifact = get_exercise(exercise_id)

    if request.method == "POST":
        db_utils = SqliteUtilites(DATABASE_NAME)
        db_utils.execute(
            "INSERT INTO exercise_likes (username, exercise) VALUES"
            f" ('{global_user}', '{exercise_artifact['name']}')",
            commit=True,
        )
        flash(
            f"{exercise_artifact['name']} has been added to your Liked"
            " Exercises"
        )
        return redirect(url_for("home"))
    return render_template("exercise.html", exercise=exercise_artifact)


@app.route("/workout/<int:workout_id>", methods=("GET", "POST"))
def workout(workout_id):
    workout_artifact = get_workout(workout_id)

    if request.method == "POST":
        db_utils = SqliteUtilites(DATABASE_NAME)
        db_utils.execute(
            "INSERT INTO workout_likes (username, workout) VALUES"
            f" ('{global_user}', '{workout_artifact['name']}')",
            commit=True,
        )
        flash(
            f"{workout_artifact['name']} has been added to your Liked Workouts"
        )
        return redirect(url_for("home"))

    selected_exercises = get_exercises_for_workout(workout_id)
    return render_template(
        "workout.html",
        workout=workout_artifact,
        selected_exercises=selected_exercises,
    )


@app.route("/<int:workout_id>/edit_workout", methods=("GET", "POST"))
def edit_workout(workout_id):
    workout_artifact = get_workout(workout_id)

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]

        if not name:
            flash("Name is required!")
        else:
            db_utils = SqliteUtilites(DATABASE_NAME)
            db_utils.execute(
                f"UPDATE workouts SET name = '{name}',"
                f" description = '{description}' WHERE id = {id}",
                commit=True,
            )
            return redirect(url_for("search_workouts"))

    selected_exercises = get_exercises_for_workout(workout_id)

    return render_template(
        "edit_workout.html",
        workout=workout_artifact,
        selected_exercises=selected_exercises,
    )


@app.route("/<int:id>/edit", methods=("GET", "POST"))
def edit(id):
    exercise_artifact = get_exercise(id)

    if request.method == "POST":
        name = request.form["name"]
        muscle = request.form["muscle"]
        description = request.form["description"]

        if not name:
            flash("Name is required!")
        else:
            db_utils = SqliteUtilites(DATABASE_NAME)
            db_utils.execute(
                f"UPDATE exercises SET name = '{name}', muscle = '{muscle}',"
                f" description = '{description}' WHERE id = {id}",
                commit=True,
            )
            return redirect(url_for("search_exercises"))

    return render_template("edit.html", exercise=exercise_artifact)


@app.route("/<int:id>/delete", methods=("POST",))
def delete(id: int):
    exercise_artifact = get_exercise(id)

    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute(f"DELETE FROM exercises WHERE id = {id}", commit=True)

    flash('"{}" was successfully deleted!'.format(exercise_artifact["name"]))
    return redirect(url_for("home"))


@app.route("/<int:id>/delete_workout", methods=("POST",))
def delete_workout(id: int):
    workout_artifact = get_workout(id)

    db_utils = SqliteUtilites(DATABASE_NAME)
    db_utils.execute(f"DELETE FROM workouts WHERE id = {id}", commit=True)

    flash('"{}" was successfully deleted!'.format(workout_artifact["name"]))
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run()
