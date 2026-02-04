app/
  api/
    ops_auth_demo.py          # Controller: rotas /auth/*
  services/
    auth_service.py           # Service: regras de negócio
  db/
    models/
      user.py                 # SQLAlchemy model
      session.py              # SQLAlchemy model
    repositories/
      auth_repository.py      # Repository/DAO
  schemas/
    auth/
      api.py                  # Pydantic DTOs
  core/
    password.py               # hashing/verify (Argon2)
    csrf.py                   # CSRF double submit
    throttle.py               # lockout/rate limit (in-memory)
  deps/
    auth.py                   # DI providers e dependencies (verify_auth, verify_csrf)
