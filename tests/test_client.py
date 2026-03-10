"""Тесты клиентских утилит (cookies, session store, exceptions)."""

import json

import pytest

from netschoolapi import NetSchoolAPI
from netschoolapi.client import get_login_methods, search_schools
from netschoolapi.exceptions import (
    ESIAError,
    LoginError,
    MFAError,
    NetSchoolError,
    SchoolNotFound,
    SessionExpired,
)

# ═══════════════════════════════════════════════════════════
#  _extract_access_token_from_session_store
# ═══════════════════════════════════════════════════════════


class TestExtractAccessToken:
    def test_active_entry_in_list(self):
        payload = [{"active": True, "accessToken": "token-123"}]
        token = NetSchoolAPI._extract_access_token_from_session_store(
            json.dumps(payload),
        )
        assert token == "token-123"

    def test_stringified_list(self):
        payload = [{"active": True, "accessToken": "token-456"}]
        token = NetSchoolAPI._extract_access_token_from_session_store(
            json.dumps(json.dumps(payload)),
        )
        assert token == "token-456"

    def test_dict_with_access_token(self):
        payload = {"accessToken": "tok-dict"}
        token = NetSchoolAPI._extract_access_token_from_session_store(
            json.dumps(payload),
        )
        assert token == "tok-dict"

    def test_dict_with_at(self):
        payload = {"at": "tok-at"}
        token = NetSchoolAPI._extract_access_token_from_session_store(
            json.dumps(payload),
        )
        assert token == "tok-at"

    def test_list_no_active_fallback(self):
        payload = [{"accessToken": "fallback-tok"}]
        token = NetSchoolAPI._extract_access_token_from_session_store(
            json.dumps(payload),
        )
        assert token == "fallback-tok"

    def test_invalid_json(self):
        assert NetSchoolAPI._extract_access_token_from_session_store("not json") is None

    def test_empty_list(self):
        assert NetSchoolAPI._extract_access_token_from_session_store("[]") is None

    def test_empty_dict(self):
        assert NetSchoolAPI._extract_access_token_from_session_store("{}") is None


# ═══════════════════════════════════════════════════════════
#  _parse_cookies
# ═══════════════════════════════════════════════════════════


class TestParseCookies:
    def test_full_cookie_string(self):
        result = NetSchoolAPI._parse_cookies(
            "NSSESSIONID=abc123; other=val",
        )
        assert result == {"NSSESSIONID": "abc123", "other": "val"}

    def test_hex_session_id(self):
        result = NetSchoolAPI._parse_cookies("a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4")
        assert result == {"NSSESSIONID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"}

    def test_empty_string(self):
        assert NetSchoolAPI._parse_cookies("") == {}

    def test_no_nssessionid(self):
        assert NetSchoolAPI._parse_cookies("foo=bar; baz=qux") == {}

    def test_whitespace(self):
        result = NetSchoolAPI._parse_cookies("  NSSESSIONID=xyz  ; foo=bar  ")
        assert result["NSSESSIONID"] == "xyz"


# ═══════════════════════════════════════════════════════════
#  Exception hierarchy
# ═══════════════════════════════════════════════════════════


class TestExceptions:
    def test_login_error_is_netschool_error(self):
        assert issubclass(LoginError, NetSchoolError)

    def test_mfa_error_is_login_error(self):
        assert issubclass(MFAError, LoginError)

    def test_esia_error_is_login_error(self):
        assert issubclass(ESIAError, LoginError)

    def test_school_not_found_is_login_error(self):
        assert issubclass(SchoolNotFound, LoginError)

    def test_session_expired_is_netschool_error(self):
        assert issubclass(SessionExpired, NetSchoolError)

    def test_session_expired_not_login_error(self):
        """SessionExpired — отдельная ветка, не LoginError."""
        assert not issubclass(SessionExpired, LoginError)

    def test_catch_esia_as_login(self):
        """ESIAError должна ловиться как LoginError."""
        with pytest.raises(LoginError):
            raise ESIAError("test")

    def test_catch_mfa_as_login(self):
        """MFAError должна ловиться как LoginError."""
        with pytest.raises(LoginError):
            raise MFAError("test")


# ═══════════════════════════════════════════════════════════
#  NetSchoolAPI.__repr__
# ═══════════════════════════════════════════════════════════


class TestNetSchoolRepr:
    def test_repr_default(self):
        ns = NetSchoolAPI.__new__(NetSchoolAPI)
        ns._http = type("H", (), {"base_url": "https://sgo.example.ru/webapi"})()
        ns._student_id = -1
        r = repr(ns)
        assert "NetSchoolAPI" in r
        assert "sgo.example.ru" in r


# ═══════════════════════════════════════════════════════════
#  Session export
# ═══════════════════════════════════════════════════════════


class TestSessionExport:
    def test_export_session_json(self):
        """export_session() возвращает валидный JSON."""
        ns = NetSchoolAPI.__new__(NetSchoolAPI)
        ns._access_token = "tok123"
        ns._student_id = 42
        ns._year_id = 10
        ns._school_id = 5

        # Минимальный мок http client
        class FakeCookies:
            def __iter__(self):
                return iter({"NSSESSIONID": "abc"}.items())

            def items(self):
                return [("NSSESSIONID", "abc")]

        class FakeClient:
            cookies = FakeCookies()

        class FakeHttp:
            client = FakeClient()

        ns._http = FakeHttp()  # type: ignore[assignment]

        data = json.loads(ns.export_session())
        assert data["version"] == 1
        assert data["access_token"] == "tok123"
        assert data["student_id"] == 42


# ═══════════════════════════════════════════════════════════
#  search_schools — валидация аргументов
# ═══════════════════════════════════════════════════════════


class TestSearchSchoolsArgs:
    @pytest.mark.asyncio
    async def test_unknown_region_raises(self):
        """Несуществующий регион → ValueError."""
        with pytest.raises(ValueError, match="Не удалось определить URL"):
            await search_schools("Неизвестная область", "школа")

    @pytest.mark.asyncio
    async def test_url_passthrough(self):
        """URL начинающийся с http(s):// не проходит через get_url."""
        # Ожидаем ошибку подключения, но не ValueError —
        # значит URL был принят как есть.
        with pytest.raises(Exception) as exc_info:
            await search_schools("https://127.0.0.1:1", "школа", timeout=1)
        assert not isinstance(exc_info.value, ValueError)


# ═══════════════════════════════════════════════════════════
#  get_login_methods — валидация аргументов
# ═══════════════════════════════════════════════════════════


class TestGetLoginMethodsArgs:
    @pytest.mark.asyncio
    async def test_unknown_region_raises(self):
        """Несуществующий регион → ValueError."""
        with pytest.raises(ValueError, match="Не удалось определить URL"):
            await get_login_methods("Неизвестная область")

    @pytest.mark.asyncio
    async def test_url_passthrough(self):
        """УРЛ начинающийся с http(s):// не проходит через get_url."""
        with pytest.raises(Exception) as exc_info:
            await get_login_methods("https://127.0.0.1:1", timeout=1)
        assert not isinstance(exc_info.value, ValueError)
