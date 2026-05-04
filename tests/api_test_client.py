from fastapi.testclient import TestClient

from api.app.main import app


client = TestClient(app)
