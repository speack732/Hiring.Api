from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    email: str = Field(
        max_length=150,
        validation_alias=AliasChoices("email", "Email"),
    )
    password: str = Field(validation_alias=AliasChoices("password", "Password"))


class AuthResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(serialization_alias="accessToken")
    token_type: str = Field(default="Bearer", serialization_alias="tokenType")
    expires_in_minutes: int = Field(serialization_alias="expiresInMinutes")
