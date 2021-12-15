# FastAPI Dependencies/Tooling
from fastapi.security import OAuth2PasswordBearer

### FastAPI ###
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
