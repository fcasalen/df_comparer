from pandas import read_csv, read_excel, read_parquet

def df_reader(file_path:str):
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        return read_excel(file_path)
    elif file_path.endswith('.parquet'):
        return read_parquet(file_path)
    elif file_path.endswith('.csv'):
        return read_csv(file_path)
    else:
        raise ValueError('Unsupported file format')