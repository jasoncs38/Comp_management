from comp_management import app, db

with app.app_context():
    with db.engine.connect() as conn:
        conn.execute(db.text(
          "ALTER TABLE user ADD COLUMN is_main_admin BOOLEAN DEFAULT 0"
        ))
        conn.commit()

print("is_main_admin column added successfully.")