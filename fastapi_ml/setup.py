from setuptools import find_packages, setup

setup(
    name="fastapi-ml",
    version="0.1.0",
    description="FastAPI ML Service for BI MVP",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.32.0",
        "anthropic>=0.40.0",
        "pydantic>=2.10.0",
        "pydantic-settings>=2.6.0",
        "python-dotenv>=1.0.1",
        "httpx>=0.28.0",
        "pandas>=2.2.0",
        "numpy>=2.1.0",
        "scikit-learn>=1.5.0",
    ],
    python_requires=">=3.12",
)
