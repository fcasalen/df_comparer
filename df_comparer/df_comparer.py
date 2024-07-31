from pandas import DataFrame, merge
from .df_reader import df_reader
from .params_validators import DfComparerParametersDf, DfComparerParametersPaths
from numpy import NAN
import random
import string
from warnings import warn

def generate_random_string(length):
    letters = string.ascii_letters + "_"
    return ''.join(random.choice(letters) for _ in range(length))

class DfComparer:
    @staticmethod
    def from_df(new_df:DataFrame, id_list:list[str], old_df:DataFrame = None, rename_columns_new_old:list[str] = None, drop_not_changed:bool = False) -> DataFrame:
        if not isinstance(old_df, DataFrame):
            if not old_df:
                old_df = DataFrame(columns=new_df.columns)
        DfComparerParametersDf(id_list=id_list, new_df=new_df, old_df=old_df, rename_columns_new_old=rename_columns_new_old)
        erros = []
        for col in id_list:
            if new_df[col].isnull().any():
                erros.append(f'new_df tem valores nulos na coluna {col}. As linhas com valores nulos nessa coluna serão removidas')
            if old_df[col].isnull().any():
                erros.append(f'old_df tem valores nulos na coluna {col}. As linhas com valores nulos nessa coluna serão removidas')
        if erros:
            warn("\n".join(erros))
        new_df = new_df.dropna(subset=id_list)
        old_df = old_df.dropna(subset=id_list)
        value_name = generate_random_string(10)
        var_name = generate_random_string(10)
        new_df_melted = new_df.melt(id_vars=id_list, value_name=value_name, var_name=var_name)
        old_df_melted = old_df.melt(id_vars=id_list, value_name=value_name, var_name=var_name)
        id_list_adj = id_list + [var_name]
        df_final = merge(left=new_df_melted, right=old_df_melted, on=id_list_adj, how='outer')
        df_final.drop_duplicates(inplace=True)
        df_final.reset_index(drop=True, inplace=True)
        df_final['changes'] = 'kept'
        df_final.loc[df_final.query(f'{value_name}_x.isnull() and {value_name}_y.isnull() == False').index, 'changes'] = 'excluded'
        df_final.loc[df_final.query(f'{value_name}_y.isnull() and {value_name}_x.isnull() == False').index, 'changes'] = 'added'
        df_final.loc[df_final.query(f'{value_name}_x.isnull() == False and {value_name}_y.isnull() == False and {value_name}_x != {value_name}_y').index, 'changes'] = 'changed'
        df_final = df_final.fillna(NAN)
        df_final = df_final.astype(str)
        if not rename_columns_new_old:
            df_final.rename(
                columns={
                    f'{value_name}_x': 'new_df',
                    f'{value_name}_y': 'old_df',
                    var_name: 'variable'
                },
                inplace=True
            )
            return df_final
        df_final.rename(
            columns={
                f'{value_name}_x': rename_columns_new_old[0],
                f'{value_name}_y': rename_columns_new_old[1],
                var_name: 'variable'
            },
            inplace=True
        )
        if drop_not_changed:
            df_final = df_final.query('changes!="kept"').reset_index(drop=True)
        return df_final
    
    @staticmethod
    def from_paths(new_df_path:str, id_list:list[str], old_df_path:str = '', rename_columns_to_path:bool = True, drop_not_changed:bool = False) -> DataFrame:
        DfComparerParametersPaths(id_list=id_list, new_df_path=new_df_path, old_df_path=old_df_path)
        new_df = df_reader(new_df_path)
        old_df = None
        old_path_rename_col = 'old_df'
        if old_df_path != '':
            old_df = df_reader(old_df_path)
            old_path_rename_col = old_df_path
        rename_columns = None
        if rename_columns_to_path:
            rename_columns = [new_df_path, old_path_rename_col]
        return DfComparer.from_df(
            new_df=new_df,
            old_df=old_df,
            id_list=id_list,
            rename_columns_new_old=rename_columns,
            drop_not_changed=drop_not_changed
        )