from enum import Enum


class AuthType(str, Enum):
    NONE = "NONE"
    API_KEY = "API_KEY"
    BASIC_AUTH = "BASIC_AUTH"
    OAUTH2 = "OAUTH2"
    JWT = "JWT"
