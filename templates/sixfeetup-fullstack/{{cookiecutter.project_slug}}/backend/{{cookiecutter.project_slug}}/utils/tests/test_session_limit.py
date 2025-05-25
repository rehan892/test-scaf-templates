import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

from {{ cookiecutter.project_slug }}.utils.session_limit import ActiveSessionMiddleware


class FakePipeline:
    def __init__(self, redis):
        self.redis = redis
        self.commands = []

    def hset(self, key, field, value):
        self.commands.append(("hset", key, field, value))
        return 1

    def hlen(self, key):
        self.commands.append(("hlen", key))
        return len(self.redis.store.get(key, {}))

    def expire(self, key, timeout):
        self.commands.append(("expire", key, timeout))
        return True

    def execute(self):
        results = []
        count = 0
        for cmd in self.commands:
            if cmd[0] == "hset":
                _, key, field, value = cmd
                self.redis.store.setdefault(key, {})[field] = value
                results.append(1)
            elif cmd[0] == "hlen":
                _, key = cmd
                count = len(self.redis.store.get(key, {}))
                results.append(count)
            elif cmd[0] == "expire":
                results.append(True)
        self.commands = []
        return results


class FakeRedis:
    def __init__(self):
        self.store = {}

    def pipeline(self):
        return FakePipeline(self)

    def hdel(self, key, field):
        if key in self.store:
            self.store[key].pop(field, None)


@pytest.fixture
def fake_redis(monkeypatch):
    r = FakeRedis()
    monkeypatch.setattr(
        "{{ cookiecutter.project_slug }}.utils.session_limit.get_redis_connection",
        lambda *_args, **_kwargs: r,
    )
    return r


@pytest.mark.django_db
def test_record_ip(fake_redis, rf: RequestFactory, user):
    middleware = ActiveSessionMiddleware(lambda r: HttpResponse("OK"))

    request = rf.get("/", REMOTE_ADDR="127.0.0.1")
    request.user = user

    sm = SessionMiddleware(lambda r: None)
    sm.process_request(request)
    request.session.save()

    response = middleware(request)

    assert response.status_code == 200
    key = f"active_sessions:{user.pk}"
    assert fake_redis.store[key][request.session.session_key] == "127.0.0.1"


@pytest.mark.django_db
def test_limit_exceeded(fake_redis, rf: RequestFactory, user):
    key = f"active_sessions:{user.pk}"
    fake_redis.store[key] = {f"s{i}": "ip" for i in range(20)}

    middleware = ActiveSessionMiddleware(lambda r: HttpResponse("OK"))

    request = rf.get("/", REMOTE_ADDR="127.0.0.2")
    request.user = user

    sm = SessionMiddleware(lambda r: None)
    sm.process_request(request)
    request.session.save()

    response = middleware(request)

    assert response.status_code == 403
    assert len(fake_redis.store[key]) == 20
    assert request.session.session_key not in fake_redis.store[key]
