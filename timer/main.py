import sys
import sqlite3
import time

connection = sqlite3.connect("timer.db")


def main():
    args = sys.argv[1:]

    if len(args) < 1:
        print("Usage: timer <action> <project?>")
        exit(1)

    action = args[0]
    project = args[1] if len(args) > 1 else None

    timeInMilliseconds = int(time.time() * 1000)
    cursor = connection.cursor()

    # Create table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS timer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT,
            start_time INTEGER,
            end_time INTEGER
        );
        """
    )

    # Insert a row of data
    if action == "list":
        results = cursor.execute(
            """
            SELECT project, start_time, end_time
            FROM timer
            WHERE end_time IS NULL
            ORDER BY start_time DESC;
            """
        ).fetchall()
        print("Project\t\t\tStart Time\t\t\tDuration")
        for result in results:
            project, start_time, _ = result
            formattedStartTime = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(start_time / 1000)
            )
            runningFor = timeInMilliseconds - start_time  # in milliseconds
            minutes = int(runningFor / 1000 / 60)
            formattedMinutes = (
                f"{minutes} minutes" if minutes > 0 else "less than a minute"
            )
            print(
                f"{project}\t\
                {formattedStartTime}\t\
                {formattedMinutes}"
            )
    elif action == "delete":
        cursor.execute(
            """
            DELETE FROM timer
            WHERE project = ? AND end_time IS NULL;
            """,
            (project,),
        )
        connection.commit()
        print(f"Deleted timer for {project}")
    elif action == "delete-all":
        cursor.execute(
            """
            DELETE FROM timer
            WHERE project IS NOT NULL;
            """
        )
        connection.commit()
        print("Deleted all timers")
    elif action == "total":
        results = cursor.execute(
            """
            SELECT project, start_time, end_time
            FROM timer
            WHERE project IS NOT NULL
            ORDER BY start_time DESC;
            """
        ).fetchall()
        print("Project\t\t\tTotal Time")
        projects = {}
        for result in results:
            project, start_time, end_time = result
            if project not in projects:
                projects[project] = 0
            if end_time is None:
                end_time = timeInMilliseconds
            projects[project] += end_time - start_time
        for project, total in projects.items():
            minutes = int(total / 1000 / 60)
            formattedMinutes = (
                f"{minutes} minutes" if minutes > 0 else "less than a minute"
            )
            print(f"{project}\t\t\t{formattedMinutes}")

    elif action == "start":
        cursor.execute(
            """
            INSERT INTO timer (project, start_time)
            VALUES (?, ?);
            """,
            (
                project,
                timeInMilliseconds,
            ),
        )
        connection.commit()
        print(f"Starting timer for {project}")
    elif action == "stop":
        cursor.execute(
            """
            UPDATE timer
            SET end_time = ?
            WHERE project = ? AND end_time IS NULL;
            """,
            (
                timeInMilliseconds,
                project,
            ),
        )
        connection.commit()
        print(f"Stopping timer for {project}")

    elif action == "status":
        result = cursor.execute(
            """
            SELECT project, start_time, end_time
            FROM timer
            WHERE project = ? AND end_time IS NULL;
            """,
            (project,),
        ).fetchone()

        if result is None:
            print(f"No active timer for {project}")
        else:
            project, start_time, _ = result
            runningFor = timeInMilliseconds - start_time  # in milliseconds
            minutes = int(runningFor / 1000 / 60)
            formattedMinutes = (
                f"{minutes} minutes" if minutes > 0 else "less than a minute"
            )
            formattedStartTime = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(start_time / 1000)
            )
            print(
                f"Active timer for {project} started at {formattedStartTime}, running for {formattedMinutes}"
            )

    else:
        print("Invalid action")
        exit(1)
