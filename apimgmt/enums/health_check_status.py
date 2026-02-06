from enum import Enum


class HealthCheckStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"
