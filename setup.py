from setuptools import setup, find_packages

setup(
    name="mini_mlflow",
    version="0.1.0",
    description="A lightweight ML experiment tracking system inspired by MLflow.",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.115.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.0.0",
        "uvicorn>=0.30.0",
        "requests>=2.31.0",
        "alembic>=1.13.0",
        "psycopg2-binary>=2.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.0.0",
            "httpx",
        ],
        "examples": [
            "scikit-learn",
            "pandas",
            "numpy",
            "nltk"
        ]
    },
)