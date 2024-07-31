```python
#works with dataframes and csv, xls, xlsx and parquet files

from df_comparer import DfComparer
#supposing two dataframes df1 and df2 where columns for identification of row are col1 and col2,
changes = DfComparer.from_df(
    new_df=df1,
    old_df=df2,
    id_list=['col1', 'col2'],
    drop_not_changed=True #only return what changed,
    rename_columns_new_old=['new_value', 'old_value'] #rename columns with the new and old_value..if not passed, will use new_df, old_df
)

#supposing paths to two files: new_df_path, old_df_path
changes = Df.Comparer.from_paths(
    new_df_path=new_df_path,
    old_df_path=old_df_path,
    id_list=['col1', 'col2'],
    drop_not_changed=True #only return what changed,
    rename_columns_to_path=True #will rename columns with the new and old values to their respective paths
) 
```