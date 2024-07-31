from pydantic import BaseModel, field_validator, Field, ConfigDict
from pandas import DataFrame
from os.path import exists

class DfComparerParametersDf(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed = True)
    id_list:list[str]
    new_df:DataFrame = Field(default = DataFrame())
    old_df:DataFrame = Field(default = DataFrame())
    rename_columns_new_old: list[str] | None = None

    @field_validator('rename_columns_new_old')
    def validate_rename_columns_new_old(cls, rename_columns_new_old):
        if not rename_columns_new_old:
            return rename_columns_new_old
        if len(rename_columns_new_old) != 2:
            raise ValueError('rename_columns_new_old should be a list with two strings')

    def __init__(self, id_list:list[str], new_df:DataFrame, old_df:DataFrame, rename_columns_new_old:list[str] = None):
        super().__init__(id_list = id_list, rename_columns_new_old = rename_columns_new_old)
        extra_keys = set(id_list) - set(new_df.columns)
        if extra_keys:
            raise ValueError(f'columns in id_list not found in new_df: {", ".join(extra_keys)}')
        extra_keys = set(id_list) - set(old_df.columns)
        if extra_keys:
            raise ValueError(f'columns in id_list not found in old_df: {", ".join(extra_keys)}')

class DfComparerParametersPaths(BaseModel):
    id_list:list[str]
    new_df_path:str
    old_df_path:str
    
    @field_validator('new_df_path')
    def valida_new_df(cls, new_df_path):
        if not exists(new_df_path):
            raise ValueError(f'{new_df_path} não existe')
        
    @field_validator('old_df_path')
    def valida_old_df(cls, old_df_path):
        if not exists(old_df_path) and old_df_path != '':
            raise ValueError(f'{old_df_path} não existe')