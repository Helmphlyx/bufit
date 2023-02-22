DROP TABLE IF EXISTS exercises;
DROP TABLE IF EXISTS workouts;
DROP TABLE IF EXISTS workout_exercises;
DROP TABLE IF EXISTS exercise_likes;
DROP TABLE IF EXISTS workout_likes;
DROP TABLE IF EXISTS muscles;

CREATE TABLE exercises (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   name TEXT NOT NULL,
   muscle INTEGER NOT NULL DEFAULT 0,
   description TEXT NOT NULL,
   image_url TEXT DEFAULT "",
   created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workouts (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   name TEXT NOT NULL,
   user_id INTEGER NOT NULL,
   description TEXT NOT NULL,
   coach_workout INTEGER NOT NULL DEFAULT 0,
   created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workout_exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    WorkoutID INTEGER NOT NULL,
    ExercisesID INTEGER NOT NULL,
    num_sets INTEGER NOT NULL DEFAULT 0,
    num_reps INTEGER NOT NULL DEFAULT 0,
    num_rest INTEGER NOT NULL DEFAULT 0,
    notes TEXT DEFAULT "",
    exercise_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE exercise_likes (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   user_id INTEGER NOT NULL,
   exercise TEXT NOT NULL,
   created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workout_likes (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   user_id INTEGER NOT NULL,
   workout INTEGER NOT NULL,
   created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE muscles (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   muscle TEXT NOT NULL UNIQUE,
   muscle_latin TEXT NOT NULL DEFAULT ''
);
