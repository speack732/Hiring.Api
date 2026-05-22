class ServiceError(Exception):
    pass


class DuplicateEmployeeError(ServiceError):
    pass


class DuplicateUserError(ServiceError):
    pass


class EmployeeNotFoundError(ServiceError):
    pass


class FileValidationError(ServiceError):
    pass
