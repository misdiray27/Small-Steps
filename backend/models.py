from pydantic import BaseModel,EmailStr,Field
from typing import Optional,List
class Register(BaseModel):
 full_name:str; email:EmailStr; password:str=Field(min_length=6); confirm_password:str
 user_type:Optional[str]=None; stress_sources:List[str]=[]; other_stress:Optional[str]=None; meditation_time:str='Not set'; recent_feeling:str='Indifferent'; meditation_experience:str='None'; goals:List[str]=[]; support_preference:str='A mixture of everything'
class Login(BaseModel): email:EmailStr; password:str
class Analyze(BaseModel): user_id:int; message:str; count:int=6
class Chat(BaseModel): user_id:int; message:str; language:str='English'
class Profile(BaseModel): full_name:str
class Prefs(BaseModel): language:Optional[str]=None; meditation_time:Optional[str]=None
class PasswordChange(BaseModel): user_id:int; old_password:str; new_password:str=Field(min_length=6)
class Forgot(BaseModel): email:EmailStr
