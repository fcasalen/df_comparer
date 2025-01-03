from .df_comparer import DfComparer
from mocks_handler import MocksHandler
from pytest import raises
import pandas as pd
import numpy as np

mh = MocksHandler('df_comparer')

def test_compare():
    expected_df = pd.DataFrame({
        'item1': ['1', '1', '2', '2', '3', '3', '4', '4'],
        'variable': ['coluna', 'valor'] * 4 ,
        'new_df': ['hoje', '5', 'ontem', '6', 'amanha', '7', 'NA', 'NA'],
        'old_df': ['ontem', '5','ontem', '4', 'NA', 'NA', 'amanha', '7'],
        'changes': ['changed', 'kept', 'kept', 'changed', 'added', 'added', 'excluded', 'excluded']
    })
    df = DfComparer.from_df(
        new_df = pd.DataFrame(mh.load_from_mocks_folder('df1')),
        old_df = pd.DataFrame(mh.load_from_mocks_folder('df2')),
        id_list = ['item1']
    )
    pd.testing.assert_frame_equal(df,expected_df)
    df = DfComparer.from_df(
        new_df = pd.DataFrame(mh.load_from_mocks_folder('df1')),
        old_df = pd.DataFrame(mh.load_from_mocks_folder('df2')),
        id_list = ['item1'],
        rename_columns_new_old = ['ha', 'oi']
    )
    expected_df.rename(columns = {'new_df': 'ha', 'old_df': 'oi'}, inplace = True)
    pd.testing.assert_frame_equal(df,expected_df)
    
def test_invalids():
    with raises(ValueError, match='columns in id_list not found in new_df: oi') as exc:
        DfComparer.from_df(
            new_df = pd.DataFrame(mh.load_from_mocks_folder('df1')),
            old_df = pd.DataFrame(mh.load_from_mocks_folder('df2')),
            id_list = ['oi']
        )

def test_old_df_none():
    df = DfComparer.from_df(
        new_df = pd.DataFrame(mh.load_from_mocks_folder('df1')),
        id_list = ['item1']
    )
    expected_df = pd.DataFrame({
        'item1': ['1', '1', '2', '2', '3', '3'],
        'variable': ['coluna', 'valor'] * 3,
        'new_df': ['hoje', '5', 'ontem', '6', 'amanha', '7'],
        'old_df': ['NA'] * 6,
        'changes': ['added'] * 6
    })
    expected_df['old_df'] = expected_df['old_df'].astype(object)
    pd.testing.assert_frame_equal(df,expected_df)
    df = DfComparer.from_paths(
        new_df_path = 'df_comparer/mocks/df1.xlsx',
        id_list = ['item1'],
        rename_columns_to_path = False
    )
    pd.testing.assert_frame_equal(df,expected_df)

def test_both_null():
    df = DfComparer.from_df(
        new_df = pd.DataFrame({'item1': ['oxe'], 'val': ['NA']}),
        old_df = pd.DataFrame({'item1': ['oxe'], 'val': ['NA']}),
        id_list = ['item1']
    )
    assert df.equals(pd.DataFrame({
        'item1':['oxe'],
        'variable': ['val'],
        'new_df': ['NA'],
        'old_df': ['NA'],
        'changes': 'kept'
    }))

def test_new_column():
    df = DfComparer.from_df(
        new_df = pd.DataFrame({'item1': ['oxe', 'oxe'], 'val': [1,2], 'ha': [3, 2]}),
        old_df = pd.DataFrame({'item1': ['oxe', 'oxe'], 'val': [2,2]}),
        id_list = ['item1']
    )
    expected_df = pd.DataFrame({
        'item1':['oxe', 'oxe', 'oxe', 'oxe'],
        'variable': ['ha', 'ha', 'val', 'val'],
        'new_df': ['3', '2', '1', '2'],
        'old_df': ['NA', 'NA', '2.0', '2.0'],
        'changes': ['added', 'added', 'changed', 'kept']
    })
    pd.testing.assert_frame_equal(df,expected_df)
    df = DfComparer.from_df(
        old_df = pd.DataFrame({'item1': ['oxe', 'oxe'], 'val': [1,2], 'ha': [3, 2]}),
        new_df = pd.DataFrame({'item1': ['oxe', 'oxe'], 'val': [2,2]}),
        id_list = ['item1']
    )
    expected_df = pd.DataFrame({
        'item1':['oxe', 'oxe', 'oxe', 'oxe'],
        'variable': ['ha', 'ha', 'val', 'val'],
        'new_df': ['NA', 'NA', '2.0', '2.0'],
        'old_df': ['3', '2', '1', '2'],
        'changes': ['excluded', 'excluded', 'changed', 'kept']
    })
    pd.testing.assert_frame_equal(df,expected_df)
    
def drop_not_changed():
    df = DfComparer.from_df(
        old_df = pd.DataFrame({'item1': ['oxe', 'oxe'], 'val': [1,2], 'ha': [3, 2]}),
        new_df = pd.DataFrame({'item1': ['oxe', 'oxe'], 'val': [2,2]}),
        id_list = ['item1'],
        drop_not_changed=True
    )
    expected_df = pd.DataFrame({
        'item1':['oxe', 'oxe', 'oxe'],
        'variable': ['val', 'ha', 'ha'],
        'new_df': ['2.0', 'NA', 'NA'],
        'old_df': ['1', '3', '2'],
        'changes': ['changed', 'excluded', 'excluded']
    })
    pd.testing.assert_frame_equal(df,expected_df)