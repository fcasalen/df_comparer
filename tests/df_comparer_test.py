from typing import Callable

import pandas as pd
import pytest

from src.df_comparer import df_comparer


class TestFromDF:
    def test_compare(self, open_mock_file: Callable[[str], dict]):
        expected_df = pd.DataFrame(
            {
                "item1": [1, 1, 2, 2, 3, 3, 4, 4],
                "variable": ["coluna", "valor"] * 4,
                "new_df": ["hoje", 5, "ontem", 6, "amanha", 7, pd.NA, pd.NA],
                "old_df": ["ontem", 5, "ontem", 4, pd.NA, pd.NA, "amanha", 7],
                "changes": [
                    "changed",
                    "kept",
                    "kept",
                    "changed",
                    "added",
                    "added",
                    "excluded",
                    "excluded",
                ],
            }
        ).convert_dtypes()

        df = df_comparer.from_df(
            new_df=pd.DataFrame(open_mock_file("df1.json")),
            old_df=pd.DataFrame(open_mock_file("df2.json")),
            id_list=["item1"],
        )
        pd.testing.assert_frame_equal(left=df, right=expected_df)

    def test_compare_only_changed(self, open_mock_file: Callable[[str], dict]):
        expected_df = pd.DataFrame(
            {
                "item1": [1, 2, 3, 3, 4, 4],
                "variable": ["coluna", "valor"] * 3,
                "new_df": ["hoje", 6, "amanha", 7, pd.NA, pd.NA],
                "old_df": ["ontem", 4, pd.NA, pd.NA, "amanha", 7],
                "changes": [
                    "changed",
                    "changed",
                    "added",
                    "added",
                    "excluded",
                    "excluded",
                ],
            }
        ).convert_dtypes()
        df = df_comparer.from_df(
            new_df=pd.DataFrame(open_mock_file("df1.json")),
            old_df=pd.DataFrame(open_mock_file("df2.json")),
            id_list=["item1"],
            drop_not_changed=True,
        )
        pd.testing.assert_frame_equal(left=df, right=expected_df)

    def test_compare_rename(self, open_mock_file: Callable[[str], dict]):
        df = df_comparer.from_df(
            new_df=pd.DataFrame(open_mock_file("df1.json")),
            old_df=pd.DataFrame(open_mock_file("df2.json")),
            id_list=["item1"],
            rename_columns_new_old=["ha", "oi"],
        )
        expected_df = pd.DataFrame(
            {
                "item1": [1, 1, 2, 2, 3, 3, 4, 4],
                "variable": ["coluna", "valor"] * 4,
                "ha": ["hoje", 5, "ontem", 6, "amanha", 7, pd.NA, pd.NA],
                "oi": ["ontem", 5, "ontem", 4, pd.NA, pd.NA, "amanha", 7],
                "changes": [
                    "changed",
                    "kept",
                    "kept",
                    "changed",
                    "added",
                    "added",
                    "excluded",
                    "excluded",
                ],
            }
        ).convert_dtypes()
        pd.testing.assert_frame_equal(left=df, right=expected_df)

    def test_id_list_with_na(self):
        df1 = pd.DataFrame(
            {
                "id1": ["first", "second", pd.NA],
                "id2": ["first", pd.NA, "third"],
                "col1": [1, 2, 3],
            }
        )
        df2 = pd.DataFrame(
            {
                "id1": ["first", "second", "third"],
                "id2": ["first", "second", "third"],
                "col1": [4, 5, 6],
            }
        )
        df = df_comparer.from_df(new_df=df1, old_df=df2, id_list=["id1", "id2"])
        expected_df = pd.DataFrame(
            {
                "id1": ["first", "second", "third"],
                "id2": ["first", "second", "third"],
                "variable": ["col1", "col1", "col1"],
                "new_df": [1, pd.NA, pd.NA],
                "old_df": [4, 5, 6],
                "changes": ["changed", "excluded", "excluded"],
            }
        ).convert_dtypes()
        pd.testing.assert_frame_equal(left=df, right=expected_df)

    def test_invalid_id_list(self, open_mock_file: Callable[[str], dict]):
        with pytest.raises(
            AssertionError, match="id_list has columns not in new_df: oi"
        ):
            df_comparer.from_df(
                new_df=pd.DataFrame(open_mock_file("df1.json")),
                old_df=pd.DataFrame(open_mock_file("df2.json")),
                id_list=["oi"],
            )

    def test_old_df_none(self, open_mock_file: Callable[[str], dict]):
        df = df_comparer.from_df(
            new_df=pd.DataFrame(open_mock_file("df1.json")), id_list=["item1"]
        )
        expected_df = pd.DataFrame(
            {
                "item1": [1, 1, 2, 2, 3, 3],
                "variable": ["coluna", "valor"] * 3,
                "new_df": ["hoje", 5, "ontem", 6, "amanha", 7],
                "old_df": [pd.NA] * 6,
                "changes": ["added"] * 6,
            }
        ).convert_dtypes()
        pd.testing.assert_frame_equal(left=df, right=expected_df)

    def test_both_null(self):
        df = df_comparer.from_df(
            new_df=pd.DataFrame({"item1": ["oxe"], "val": [pd.NA]}),
            old_df=pd.DataFrame({"item1": ["oxe"], "val": [pd.NA]}),
            id_list=["item1"],
        )
        assert df.equals(
            pd.DataFrame(
                {
                    "item1": ["oxe"],
                    "variable": ["val"],
                    "new_df": [pd.NA],
                    "old_df": [pd.NA],
                    "changes": "kept",
                }
            ).convert_dtypes()
        )

    def test_new_column_one(self):
        df = df_comparer.from_df(
            new_df=pd.DataFrame(
                {"item1": ["oxe", "oxe1"], "val": [1, 2], "ha": [3, 2]}
            ),
            old_df=pd.DataFrame({"item1": ["oxe", "oxe1"], "val": [2.1, 2]}),
            id_list=["item1"],
        )
        expected_df = pd.DataFrame(
            {
                "item1": ["oxe", "oxe", "oxe1", "oxe1"],
                "variable": ["ha", "val", "ha", "val"],
                "new_df": [3, 1, 2, 2],
                "old_df": [pd.NA, 2.1, pd.NA, 2],
                "changes": ["added", "changed", "added", "kept"],
            }
        ).convert_dtypes()
        pd.testing.assert_frame_equal(left=df, right=expected_df)

    def test_new_column_two(self):
        df = df_comparer.from_df(
            old_df=pd.DataFrame({"item1": ["oxe", "oxe"], "val": [1, 2], "ha": [3, 2]}),
            new_df=pd.DataFrame({"item1": ["oxe", "oxe"], "val": [2, 2]}),
            id_list=["item1"],
        )
        expected_df = pd.DataFrame(
            {
                "item1": ["oxe", "oxe", "oxe", "oxe"],
                "variable": ["ha", "ha", "val", "val"],
                "new_df": [pd.NA, pd.NA, 2, 2],
                "old_df": [3, 2, 1, 2],
                "changes": ["excluded", "excluded", "changed", "kept"],
            }
        ).convert_dtypes()
        pd.testing.assert_frame_equal(left=df, right=expected_df)

    def drop_not_changed(self):
        df = df_comparer.from_df(
            old_df=pd.DataFrame({"item1": ["oxe", "oxe"], "val": [1, 2], "ha": [3, 2]}),
            new_df=pd.DataFrame({"item1": ["oxe", "oxe"], "val": [2, 2]}),
            id_list=["item1"],
            drop_not_changed=True,
        )
        expected_df = pd.DataFrame(
            {
                "item1": ["oxe", "oxe", "oxe"],
                "variable": ["val", "ha", "ha"],
                "new_df": [2.0, pd.NA, pd.NA],
                "old_df": [1, 3, 2],
                "changes": ["changed", "excluded", "excluded"],
            }
        )
        pd.testing.assert_frame_equal(left=df, right=expected_df)


class TestFromPath:
    def test_old_df_none_not_renaming_path(self):
        df = df_comparer.from_paths(
            new_df_path="tests/mocks/df1.xlsx",
            id_list=["item1"],
            rename_columns_to_path=False,
        )
        expected_df = pd.DataFrame(
            {
                "item1": [1, 1, 2, 2, 3, 3],
                "variable": ["coluna", "valor"] * 3,
                "new_df": ["hoje", 5, "ontem", 6, "amanha", 7],
                "old_df": [pd.NA] * 6,
                "changes": ["added"] * 6,
            }
        ).convert_dtypes()
        pd.testing.assert_frame_equal(left=df, right=expected_df)

    def test_old_df_none_renaming_path(self):
        df = df_comparer.from_paths(
            new_df_path="tests/mocks/df1.xlsx",
            id_list=["item1"],
            rename_columns_to_path=True,
        )
        expected_df = pd.DataFrame(
            {
                "item1": [1, 1, 2, 2, 3, 3],
                "variable": ["coluna", "valor"] * 3,
                "tests/mocks/df1.xlsx": ["hoje", 5, "ontem", 6, "amanha", 7],
                "old_df": [pd.NA] * 6,
                "changes": ["added"] * 6,
            }
        ).convert_dtypes()
        pd.testing.assert_frame_equal(left=df, right=expected_df)

    def test_compare(self):
        df = df_comparer.from_paths(
            new_df_path="tests/mocks/df1.xlsx",
            old_df_path="tests/mocks/df2.xlsx",
            id_list=["item1"],
            rename_columns_to_path=False,
        )
        expected_df = pd.DataFrame(
            {
                "item1": [1, 1, 2, 2, 3, 3, 4, 4],
                "variable": ["coluna", "valor"] * 4,
                "new_df": ["hoje", 5, "ontem", 6, "amanha", 7, pd.NA, pd.NA],
                "old_df": ["ontem", 5, "ontem", 4, pd.NA, pd.NA, "amanha", 7],
                "changes": [
                    "changed",
                    "kept",
                    "kept",
                    "changed",
                    "added",
                    "added",
                    "excluded",
                    "excluded",
                ],
            }
        ).convert_dtypes()
        pd.testing.assert_frame_equal(left=df, right=expected_df)
