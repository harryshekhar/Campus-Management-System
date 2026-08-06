import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# WHERE: python-dotenv is a library used in local development and deployments.
# WHY: It loads environment variables from a hidden '.env' file into your app. 
# This keeps sensitive data (like database passwords) out of your source code.
from dotenv import load_dotenv

load_dotenv()

# WHERE: Retrieves the connection string from the operating system's environment.
# WHY: The URL tells SQLAlchemy exactly where the database is, what type it is (Postgres, MySQL, SQLite), 
# and the credentials to access it (e.g., "postgresql://user:password@localhost/dbname").
DATABASE_URL = os.getenv("DATABASE_URL")

# WHERE: Usually used during debugging/local development.
# WHY: Prints the URL to the console so you can verify it loaded correctly. 
# NOTE: You should remove or comment this out in production so you don't leak passwords in your server logs!
print("DATABASE_URL =", repr(DATABASE_URL))

# WHERE/WHY: A "fail-fast" safety check. If the app boots up but cannot find a database URL, 
# it immediately crashes with a clear error rather than failing mysteriously later on.
if not DATABASE_URL:
    raise Exception("DATABASE_URL is not set")

# WHERE: Specific to PostgreSQL databases, often needed when deploying to platforms like Heroku or Render.
# WHY: Older systems provide the URL as "postgres://", but modern SQLAlchemy (v1.4+) strictly 
# requires "postgresql://". This automatically fixes the URL string so SQLAlchemy doesn't crash.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )

# WHERE: The core of SQLAlchemy's connection system.
# WHY: The "engine" is responsible for actually talking to the database. It manages 
# the "connection pool" (keeping a few database connections open and ready to use, which makes your app faster).
engine = create_engine(DATABASE_URL)

# WHERE: Used inside your API endpoints (e.g., FastAPI dependency injection) to talk to the DB.
# WHY: Creates a "factory" for database sessions. 
# - autocommit=False: Requires you to manually call `session.commit()` so you can group changes together safely.
# - autoflush=False: Prevents SQLAlchemy from prematurely pushing changes to the database before you are ready.
# - bind=engine: Tells the session to use the engine we created above.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# WHERE: Imported by your `models.py` file (like in your previous question).
# WHY: Creates a base class for your ORM models. When your User or Student class inherits from `Base`, 
# they are automatically registered in SQLAlchemy's metadata system. Later, you can use `Base.metadata.create_all(bind=engine)` 
# to automatically generate your database tables!
Base = declarative_base()