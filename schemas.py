from pydantic import BaseModel


class RegistrationDetails(BaseModel):
    name: str
    email: str
    password: str
    password2: str
    phone: str

    class Config:
        orm_mode = True



class LoginDetails(BaseModel):
    email: str
    password: str

class Settings(BaseModel):
    authjwt_secret_key: str = "secret"
    # Configure application to store and get JWT from cookies
    authjwt_token_location: set = {"cookies"}
    # Only allow JWT cookies to be sent over https
    authjwt_cookie_secure: bool = False
    # Enable csrf double submit protection. default is True
    authjwt_cookie_csrf_protect: bool = False
    # Change to 'lax' in production to make your website more secure from CSRF Attacks, default is None
    # authjwt_cookie_samesite: str = 'lax'