import sqlite3
import os

DATABASE_PATH = "/data/app.db"

def migrate():
    if not os.path.exists(DATABASE_PATH):
        print("Database does not exist yet, skipping migration")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Check if progress column exists
        cursor.execute("PRAGMA table_info(issues)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'progress' not in columns:
            print("Adding progress column to issues table...")
            cursor.execute("ALTER TABLE issues ADD COLUMN progress INTEGER DEFAULT 0")
            print("✓ Added progress column")
        else:
            print("✓ Progress column already exists")

        # Check if issue_dependencies table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='issue_dependencies'")
        if not cursor.fetchone():
            print("Creating issue_dependencies table...")
            cursor.execute("""
                CREATE TABLE issue_dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_issue_id INTEGER NOT NULL,
                    target_issue_id INTEGER NOT NULL,
                    dependency_type VARCHAR NOT NULL DEFAULT 'finish-to-start',
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY (source_issue_id) REFERENCES issues(id),
                    FOREIGN KEY (target_issue_id) REFERENCES issues(id)
                )
            """)
            print("✓ Created issue_dependencies table")
        else:
            print("✓ issue_dependencies table already exists")

        # Check if project_members table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project_members'")
        if not cursor.fetchone():
            print("Creating project_members table...")
            cursor.execute("""
                CREATE TABLE project_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    role VARCHAR NOT NULL DEFAULT 'member',
                    joined_at DATETIME NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            print("✓ Created project_members table")
        else:
            print("✓ project_members table already exists")

        # Check if project_join_requests table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project_join_requests'")
        if not cursor.fetchone():
            print("Creating project_join_requests table...")
            cursor.execute("""
                CREATE TABLE project_join_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    message TEXT,
                    status VARCHAR NOT NULL DEFAULT '申請中',
                    reviewed_by INTEGER,
                    reviewed_at DATETIME,
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (reviewed_by) REFERENCES users(id)
                )
            """)
            print("✓ Created project_join_requests table")
        else:
            print("✓ project_join_requests table already exists")

        # Migrate existing projects - add owners as members
        print("Migrating existing projects to add owners as members...")
        cursor.execute("""
            INSERT OR IGNORE INTO project_members (project_id, user_id, role, joined_at)
            SELECT id, owner_id, 'owner', created_at
            FROM projects
            WHERE NOT EXISTS (
                SELECT 1 FROM project_members
                WHERE project_members.project_id = projects.id
                AND project_members.user_id = projects.owner_id
            )
        """)
        print("✓ Migrated existing project owners to members")

        conn.commit()
        print("\n✓ Database migration completed successfully!")

    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
