from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


class TestAuthEndpoints:
    def test_login_missing_fields(self) -> None:
        """Login fails with missing fields."""
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422

    def test_login_invalid_credentials(self) -> None:
        """Login fails with wrong credentials."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "noone@test.com", "password": "WrongPass123!"},
        )
        assert response.status_code == 401

    def test_login_invalid_email_format(self) -> None:
        """Login fails with invalid email."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "not-an-email", "password": "SomePass123!"},
        )
        assert response.status_code == 422


class TestConvocatoriasEndpoints:
    def test_list_convocatorias_empty(self) -> None:
        """List convocatorias returns empty list when none exist."""
        response = client.get("/api/v1/convocatorias")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_all_requires_admin(self) -> None:
        """List all convocatorias requires admin role."""
        response = client.get("/api/v1/convocatorias/todas")
        assert response.status_code == 401

    def test_create_requires_admin(self) -> None:
        """Create convocatoria requires admin role."""
        response = client.post(
            "/api/v1/convocatorias",
            json={
                "titulo": "Test Convocatoria",
                "fecha_inicio": "2026-01-01T00:00:00Z",
                "fecha_cierre": "2026-12-31T00:00:00Z",
            },
        )
        assert response.status_code == 401


class TestPostulacionesEndpoints:
    def test_list_mine_requires_auth(self) -> None:
        """List my postulaciones requires authentication."""
        response = client.get("/api/v1/postulaciones/mine")
        assert response.status_code == 401

    def test_list_all_requires_admin(self) -> None:
        """List all postulaciones requires admin role."""
        response = client.get("/api/v1/postulaciones/todas")
        assert response.status_code == 401

    def test_create_requires_auth(self) -> None:
        """Create postulacion requires authentication."""
        response = client.post(
            "/api/v1/postulaciones",
            json={"id_convocatoria": 1},
        )
        assert response.status_code == 401


class TestResultadosEndpoints:
    def test_mis_resultados_requires_auth(self) -> None:
        """My results requires authentication."""
        response = client.get("/api/v1/resultados/mis-resultados")
        assert response.status_code == 401

    def test_ranking_requires_admin(self) -> None:
        """Ranking requires admin role."""
        response = client.get("/api/v1/resultados/ranking/1")
        assert response.status_code == 401

    def test_evaluar_requires_admin(self) -> None:
        """Evaluate requires admin role."""
        response = client.post("/api/v1/resultados/1/evaluar")
        assert response.status_code == 401


class TestAdminEndpoints:
    def test_aspirantes_requires_admin(self) -> None:
        """List aspirantes requires admin role."""
        response = client.get("/api/v1/admin/aspirantes")
        assert response.status_code == 401

    def test_postulacion_detalle_requires_admin(self) -> None:
        """Postulacion detail requires admin role."""
        response = client.get("/api/v1/admin/postulaciones/1/detalle")
        assert response.status_code == 401


class TestReglasEndpoints:
    def test_list_reglas_requires_admin(self) -> None:
        """List reglas requires admin role."""
        response = client.get("/api/v1/reglas/convocatorias/1")
        assert response.status_code == 401

    def test_create_regla_requires_admin(self) -> None:
        """Create regla requires admin role."""
        response = client.post(
            "/api/v1/reglas/convocatorias/1",
            json={
                "tipo_item": "FORMACION",
                "descripcion_regla": "Test rule",
                "puntaje_unitario": 1.0,
                "unidad": "puntos",
            },
        )
        assert response.status_code == 401
