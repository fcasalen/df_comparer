from .df_comparer import DfComparer
from pandas import DataFrame
from mocks_handler import MocksHandler
from pytest import raises
from numpy import NAN

mh = MocksHandler('df_comparer')

def test_compare():
    expected_df = DataFrame({
        'item1': ['1', '1', '2', '2', '3', '3', '4', '4'],
        'variable': ['coluna', 'valor'] * 4 ,
        'new_df': ['hoje', 5, 'ontem', 6, 'amanha', 7, NAN, NAN],
        'old_df': ['ontem', 5,'ontem', 4, NAN, NAN, 'amanha', 7],
        'changes': ['changed', 'kept', 'kept', 'changed', 'added', 'added', 'excluded', 'excluded']
    })
    expected_df['new_df'] = expected_df['new_df'].astype(str)
    expected_df['old_df'] = expected_df['old_df'].astype(str)
    df = DfComparer.from_df(
        new_df = DataFrame(mh.load_from_mocks_folder('df1')),
        old_df = DataFrame(mh.load_from_mocks_folder('df2')),
        id_list = ['item1']
    )
    assert df.equals(expected_df)
    df = DfComparer.from_df(
        new_df = DataFrame(mh.load_from_mocks_folder('df1')),
        old_df = DataFrame(mh.load_from_mocks_folder('df2')),
        id_list = ['item1'],
        rename_columns_new_old = ['ha', 'oi']
    )
    expected_df.rename(columns = {'new_df': 'ha', 'old_df': 'oi'}, inplace = True)
    assert df.equals(expected_df)    

def test_invalids():
    with raises(ValueError) as exc:
        DfComparer.from_df(
            new_df = DataFrame(mh.load_from_mocks_folder('df1')),
            old_df = DataFrame(mh.load_from_mocks_folder('df2')),
            id_list = ['oi']
        )
    assert str(exc.value) == 'columns in id_list not found in new_df: oi'

def test_old_df_none():
    df = DfComparer.from_df(
        new_df = DataFrame(mh.load_from_mocks_folder('df1')),
        id_list = ['item1']
    )
    expected_df = DataFrame({
        'item1': ['1', '1', '2', '2', '3', '3'],
        'variable': ['coluna', 'valor'] * 3,
        'new_df': ['hoje', 5, 'ontem', 6, 'amanha', 7],
        'old_df': [NAN] * 6,
        'changes': ['added'] * 6
    })
    expected_df = expected_df.astype(str)
    assert df.equals(expected_df)
    df = DfComparer.from_paths(
        new_df_path = 'df_comparer/mocks/df1.xlsx',
        id_list = ['item1'],
        rename_columns_to_path = False
    )
    assert df.equals(expected_df)

def test_both_null():
    df = DfComparer.from_df(
        new_df = DataFrame({'item1': ['oxe'], 'val': [NAN]}),
        old_df = DataFrame({'item1': ['oxe'], 'val': [NAN]}),
        id_list = ['item1']
    )
    assert df.equals(DataFrame({
        'item1':['oxe'],
        'variable': ['val'],
        'new_df': ['nan'],
        'old_df': ['nan'],
        'changes': 'kept'
    }))

def test_new_column():
    df = DfComparer.from_df(
        new_df = DataFrame({'item1': ['oxe', 'oxe'], 'val': [1,2], 'ha': [3, 2]}),
        old_df = DataFrame({'item1': ['oxe', 'oxe'], 'val': [2,2]}),
        id_list = ['item1']
    )
    expected_df = DataFrame({
        'item1':['oxe', 'oxe', 'oxe', 'oxe'],
        'variable': ['ha', 'ha', 'val', 'val'],
        'new_df': ['3', '2', '1', '2'],
        'old_df': ['nan', 'nan', '2.0', '2.0'],
        'changes': ['added', 'added', 'changed', 'kept']
    })
    assert df.equals(expected_df)
    df = DfComparer.from_df(
        old_df = DataFrame({'item1': ['oxe', 'oxe'], 'val': [1,2], 'ha': [3, 2]}),
        new_df = DataFrame({'item1': ['oxe', 'oxe'], 'val': [2,2]}),
        id_list = ['item1']
    )
    expected_df = DataFrame({
        'item1':['oxe', 'oxe', 'oxe', 'oxe'],
        'variable': ['ha', 'ha', 'val', 'val'],
        'new_df': ['nan', 'nan', '2.0', '2.0'],
        'old_df': ['3', '2', '1', '2'],
        'changes': ['excluded', 'excluded', 'changed', 'kept']
    })
    assert df.equals(expected_df)
    
def drop_not_changed():
    df = DfComparer.from_df(
        old_df = DataFrame({'item1': ['oxe', 'oxe'], 'val': [1,2], 'ha': [3, 2]}),
        new_df = DataFrame({'item1': ['oxe', 'oxe'], 'val': [2,2]}),
        id_list = ['item1'],
        drop_not_changed=True
    )
    expected_df = DataFrame({
        'item1':['oxe', 'oxe', 'oxe'],
        'variable': ['val', 'ha', 'ha'],
        'new_df': ['2.0', 'nan', 'nan'],
        'old_df': ['1', '3', '2'],
        'changes': ['changed', 'excluded', 'excluded']
    })
    assert df.equals(expected_df)