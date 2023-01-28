import sqlite3

connection = sqlite3.connect("database.db")

with open("db/schema.sql") as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute(
    "INSERT INTO exercises (name, muscle, description) VALUES (?, ?, ?)",
    (
        "Lat Pulldown",
        "latissimus dorsi",
        "The pulldown exercise works the back muscles and is performed at a"
        " workstation with adjustable resistance, usually plates. While"
        " seated, you pull a hanging bar toward you to reach chin level, then"
        " release it back up with control for one repetition. This exercise"
        " can be done as part of an upper-body strength workout.",
    ),
)

cur.execute(
    "INSERT INTO exercises (name, muscle, description) VALUES (?, ?, ?)",
    (
        "Wide Grip Lat Pulldown",
        "latissimus dorsi",
        "Wide grip version of the Lat Pulldown",
    ),
)

cur.execute(
    "INSERT INTO exercises (name, muscle, description) VALUES (?, ?, ?)",
    (
        "Leg Press",
        "quadriceps",
        "Leg presses are done in a seated position. Your legs repeatedly press"
        " against weights, which can be adjusted according to your fitness"
        " level. This targets your quads, glutes, hamstrings, hips, and"
        " calves. The seated position of leg presses helps keep your upper"
        " body and torso still.",
    ),
)

connection.commit()
connection.close()
