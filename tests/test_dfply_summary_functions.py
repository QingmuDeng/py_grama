import numpy as np
import pandas as pd
import unittest

from context import grama as gr
from context import data

X = gr.Intention()

##==============================================================================
## transform summary functions
##==============================================================================


class TestSummaryFcn(unittest.TestCase):
    def test_mean(self):
        df = data.df_diamonds >> gr.tf_select(X.cut, X.x) >> gr.tf_head(5)
        # straight summarize
        t = df >> gr.tf_summarize(m=gr.mean(X.x))
        df_truth = pd.DataFrame({"m": [4.086]})
        self.assertTrue(t.equals(df_truth))
        # grouped summarize
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_summarize(m=gr.mean(X.x))
        df_truth = pd.DataFrame(
            {"cut": ["Good", "Ideal", "Premium"], "m": [4.195, 3.950, 4.045]}
        )
        self.assertTrue(t.equals(df_truth))
        # straight mutate
        t = df >> gr.tf_mutate(m=gr.mean(X.x))
        df_truth = df.copy()
        df_truth["m"] = df_truth.x.mean()
        self.assertTrue(t.equals(df_truth))
        # grouped mutate
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_mutate(m=gr.mean(X.x))
        df_truth["m"] = pd.Series([3.950, 4.045, 4.195, 4.045, 4.195])
        self.assertTrue(t.sort_index().equals(df_truth))

    def test_first(self):
        df = data.df_diamonds >> gr.tf_select(X.cut, X.x) >> gr.tf_head(5)
        # straight summarize
        t = df >> gr.tf_summarize(f=gr.first(X.x))
        df_truth = pd.DataFrame({"f": [3.95]})
        self.assertTrue(t.equals(df_truth))
        # grouped summarize
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_summarize(f=gr.first(X.x))
        df_truth = pd.DataFrame(
            {"cut": ["Good", "Ideal", "Premium"], "f": [4.05, 3.95, 3.89]}
        )
        self.assertTrue(t.equals(df_truth))
        # summarize with order_by
        t = df >> gr.tf_summarize(f=gr.first(X.x, order_by=gr.desc(X.cut)))
        df_truth = pd.DataFrame({"f": [3.89]})
        # straight mutate
        t = df >> gr.tf_mutate(f=gr.first(X.x))
        df_truth = df.copy()
        df_truth["f"] = df_truth.x.iloc[0]
        self.assertTrue(t.equals(df_truth))
        # grouped mutate
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_mutate(f=gr.first(X.x))
        df_truth["f"] = pd.Series([3.95, 3.89, 4.05, 3.89, 4.05])
        self.assertTrue(t.sort_index().equals(df_truth))

    def test_last(self):
        df = data.df_diamonds >> gr.tf_select(X.cut, X.x) >> gr.tf_head(5)
        # straight summarize
        t = df >> gr.tf_summarize(l=gr.last(X.x))
        df_truth = pd.DataFrame({"l": [4.34]})
        self.assertTrue(t.equals(df_truth))
        # grouped summarize
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_summarize(l=gr.last(X.x))
        df_truth = pd.DataFrame(
            {"cut": ["Good", "Ideal", "Premium"], "l": [4.34, 3.95, 4.20]}
        )
        self.assertTrue(t.equals(df_truth))
        # summarize with order_by
        t = df >> gr.tf_summarize(
            f=gr.last(X.x, order_by=[gr.desc(X.cut), gr.desc(X.x)])
        )
        df_truth = pd.DataFrame({"f": [4.05]})
        assert df_truth.equals(t)
        # straight mutate
        t = df >> gr.tf_mutate(l=gr.last(X.x))
        df_truth = df.copy()
        df_truth["l"] = df_truth.x.iloc[4]
        self.assertTrue(t.equals(df_truth))
        # grouped mutate
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_mutate(l=gr.last(X.x))
        df_truth["l"] = pd.Series([3.95, 4.20, 4.34, 4.20, 4.34])
        self.assertTrue(t.sort_index().equals(df_truth))

    def test_nth(self):
        df = data.df_diamonds >> gr.tf_select(X.cut, X.x) >> gr.tf_head(10)
        # straight summarize
        t = df >> gr.tf_summarize(second=gr.nth(X.x, 1))
        df_truth = pd.DataFrame({"second": [3.89]})
        self.assertTrue(t.equals(df_truth))
        # grouped summarize
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_summarize(first=gr.nth(X.x, 0))
        df_truth = pd.DataFrame(
            {
                "cut": ["Fair", "Good", "Ideal", "Premium", "Very Good"],
                "first": [3.87, 4.05, 3.95, 3.89, 3.94],
            }
        )
        self.assertTrue(t.equals(df_truth))
        # summarize with order_by
        t = df >> gr.tf_summarize(
            last=gr.nth(X.x, -1, order_by=[gr.desc(X.cut), gr.desc(X.x)])
        )
        df_truth = pd.DataFrame({"last": [3.87]})
        self.assertTrue(df_truth.equals(t))
        # straight mutate
        t = df >> gr.tf_mutate(out_of_range=gr.nth(X.x, 500))
        df_truth = df.copy()
        df_truth["out_of_range"] = np.nan
        self.assertTrue(t.equals(df_truth))
        # grouped mutate
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_mutate(penultimate=gr.nth(X.x, -2))
        df_truth = df.copy()
        df_truth["penultimate"] = pd.Series(
            [np.nan, 3.89, 4.05, 3.89, 4.05, 4.07, 4.07, 4.07, np.nan, 4.07]
        )
        self.assertTrue(t.sort_index().equals(df_truth))

    def test_n(self):
        df = data.df_diamonds >> gr.tf_select(X.cut, X.x) >> gr.tf_head(5)
        # straight summarize
        t = df >> gr.tf_summarize(n=gr.n(X.x))
        df_truth = pd.DataFrame({"n": [5]})
        self.assertTrue(t.equals(df_truth))
        # grouped summarize
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_summarize(n=gr.n(X.x))
        df_truth = pd.DataFrame({"cut": ["Good", "Ideal", "Premium"], "n": [2, 1, 2]})
        self.assertTrue(t.equals(df_truth))
        # straight mutate
        t = df >> gr.tf_mutate(n=gr.n(X.x))
        df_truth = df.copy()
        df_truth["n"] = 5
        self.assertTrue(t.equals(df_truth))
        # grouped mutate
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_mutate(n=gr.n(X.x))
        df_truth["n"] = pd.Series([1, 2, 2, 2, 2, 2])
        self.assertTrue(t.sort_index().equals(df_truth))

    def test_n_distinct(self):
        df = pd.DataFrame(
            {
                "col_1": ["a", "a", "a", "b", "b", "b", "c", "c"],
                "col_2": [1, 1, 1, 2, 3, 3, 4, 5],
            }
        )
        # straight summarize
        t = df >> gr.tf_summarize(n=gr.n_distinct(X.col_2))
        df_truth = pd.DataFrame({"n": [5]})
        self.assertTrue(t.equals(df_truth))
        # grouped summarize
        t = df >> gr.tf_group_by(X.col_1) >> gr.tf_summarize(n=gr.n_distinct(X.col_2))
        df_truth = pd.DataFrame({"col_1": ["a", "b", "c"], "n": [1, 2, 2]})
        self.assertTrue(t.equals(df_truth))
        # straight mutate
        t = df >> gr.tf_mutate(n=gr.n_distinct(X.col_2))
        df_truth = df.copy()
        df_truth["n"] = 5
        self.assertTrue(t.equals(df_truth))
        # grouped mutate
        t = df >> gr.tf_group_by(X.col_1) >> gr.tf_mutate(n=gr.n_distinct(X.col_2))
        df_truth["n"] = pd.Series([1, 1, 1, 2, 2, 2, 2, 2])
        self.assertTrue(t.equals(df_truth))

    def test_IQR(self):
        df = data.df_diamonds >> gr.tf_select(X.cut, X.x) >> gr.tf_head(5)
        # straight summarize
        t = df >> gr.tf_summarize(i=gr.IQR(X.x))
        df_truth = pd.DataFrame({"i": [0.25]})
        self.assertTrue(t.equals(df_truth))
        # grouped summarize
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_summarize(i=gr.IQR(X.x))
        df_truth = pd.DataFrame(
            {"cut": ["Good", "Ideal", "Premium"], "i": [0.145, 0.000, 0.155]}
        )
        test_vector = abs(t.i - df_truth.i)
        assert all(test_vector < 0.000000001)
        # straight mutate
        t = df >> gr.tf_mutate(i=gr.IQR(X.x))
        df_truth = df.copy()
        df_truth["i"] = 0.25
        self.assertTrue(t.equals(df_truth))
        # grouped mutate
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_mutate(i=gr.IQR(X.x))
        df_truth["i"] = pd.Series([0.000, 0.155, 0.145, 0.155, 0.145])
        test_vector = abs(t.i - df_truth.i)
        self.assertTrue(all(test_vector < 0.000000001))

    def test_colmin(self):
        df = data.df_diamonds >> gr.tf_select(X.cut, X.x) >> gr.tf_head(5)
        # straight summarize
        t = df >> gr.tf_summarize(m=gr.colmin(X.x))
        df_truth = pd.DataFrame({"m": [3.89]})
        self.assertTrue(t.equals(df_truth))
        # grouped summarize
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_summarize(m=gr.colmin(X.x))
        df_truth = pd.DataFrame(
            {"cut": ["Good", "Ideal", "Premium"], "m": [4.05, 3.95, 3.89]}
        )
        self.assertTrue(t.equals(df_truth))
        # straight mutate
        t = df >> gr.tf_mutate(m=gr.colmin(X.x))
        df_truth = df.copy()
        df_truth["m"] = 3.89
        self.assertTrue(t.equals(df_truth))
        # grouped mutate
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_mutate(m=gr.colmin(X.x))
        df_truth["m"] = pd.Series([3.95, 3.89, 4.05, 3.89, 4.05])
        self.assertTrue(t.sort_index().equals(df_truth))

    def test_colmax(self):
        df = data.df_diamonds >> gr.tf_select(X.cut, X.x) >> gr.tf_head(5)
        # straight summarize
        t = df >> gr.tf_summarize(m=gr.colmax(X.x))
        df_truth = pd.DataFrame({"m": [4.34]})
        self.assertTrue(t.equals(df_truth))
        # grouped summarize
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_summarize(m=gr.colmax(X.x))
        df_truth = pd.DataFrame(
            {"cut": ["Good", "Ideal", "Premium"], "m": [4.34, 3.95, 4.20]}
        )
        self.assertTrue(t.equals(df_truth))
        # straight mutate
        t = df >> gr.tf_mutate(m=gr.colmax(X.x))
        df_truth = df.copy()
        df_truth["m"] = 4.34
        self.assertTrue(t.equals(df_truth))
        # grouped mutate
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_mutate(m=gr.colmax(X.x))
        df_truth["m"] = pd.Series([3.95, 4.20, 4.34, 4.20, 4.34])
        self.assertTrue(t.sort_index().equals(df_truth))

    def test_median(self):
        df = (
            data.df_diamonds
            >> gr.tf_group_by(X.cut)
            >> gr.tf_head(3)
            >> gr.tf_select(X.cut, X.x)
            >> gr.tf_ungroup()
        )
        # straight summarize
        t = df >> gr.tf_summarize(m=gr.median(X.x))
        df_truth = pd.DataFrame({"m": [4.05]})
        self.assertTrue(t.equals(df_truth))

        # grouped summarize
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_summarize(m=gr.median(X.x))
        df_truth = pd.DataFrame(
            {
                "cut": ["Fair", "Good", "Ideal", "Premium", "Very Good"],
                "m": [6.27, 4.25, 3.95, 3.89, 3.95],
            }
        )
        self.assertTrue(t.equals(df_truth))
        # straight mutate
        t = df >> gr.tf_mutate(m=gr.median(X.x))
        df_truth = df.copy()
        df_truth["m"] = 4.05
        self.assertTrue(t.equals(df_truth))
        # grouped mutate
        # t = df >> group_by(X.cut) >> mutate(m=median(X.x))
        # df_truth['m'] = pd.Series(
        #     [6.27, 6.27, 6.27, 4.25, 4.25, 4.25, 3.95, 3.95, 3.95, 3.89, 3.89, 3.89, 3.95, 3.95, 3.95],
        #     index=t.index)
        # assert t.equals(df_truth)
        # make sure it handles case with even counts properly
        df = (
            data.df_diamonds
            >> gr.tf_group_by(X.cut)
            >> gr.tf_head(2)
            >> gr.tf_select(X.cut, X.x)
        )
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_summarize(m=gr.median(X.x))
        df_truth = pd.DataFrame(
            {
                "cut": ["Fair", "Good", "Ideal", "Premium", "Very Good"],
                "m": [5.160, 4.195, 3.940, 4.045, 3.945],
            }
        )
        test_vector = abs(t.m - df_truth.m)
        self.assertTrue(all(test_vector < 0.000000001))

    def test_var(self):
        df = (
            data.df_diamonds
            >> gr.tf_group_by(X.cut)
            >> gr.tf_head(3)
            >> gr.tf_select(X.cut, X.x)
            >> gr.tf_ungroup()
        )

        # straight summarize
        t = df >> gr.tf_summarize(v=gr.var(X.x))
        df_truth = pd.DataFrame({"v": [0.687392]})
        test_vector = abs(t.v - df_truth.v)
        self.assertTrue(all(test_vector < 0.00001))

        # grouped summarize
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_summarize(v=gr.var(X.x))
        df_truth = pd.DataFrame(
            {
                "cut": ["Fair", "Good", "Ideal", "Premium", "Very Good"],
                "v": [2.074800, 0.022033, 0.056133, 0.033100, 0.005233],
            }
        )
        test_vector = abs(t.v - df_truth.v)
        self.assertTrue(all(test_vector < 0.00001))
        # straight mutate
        t = df >> gr.tf_mutate(v=gr.var(X.x))
        df_truth = df.copy()
        df_truth["v"] = 0.687392
        test_vector = abs(t.v - df_truth.v)
        self.assertTrue(all(test_vector < 0.00001))
        # grouped mutate
        # t = df >> group_by(X.cut) >> mutate(v=var(X.x))
        # df_truth['v'] = pd.Series([2.074800, 2.074800, 2.074800, 0.022033, 0.022033, 0.022033,
        #                            0.056133, 0.056133, 0.056133, 0.033100, 0.033100, 0.033100,
        #                            0.005233, 0.005233, 0.005233],
        #                           index=t.index)
        # test_vector = abs(t.v - df_truth.v)
        # assert all(test_vector < .00001)
        # test with single value (var undefined)
        df = (
            data.df_diamonds
            >> gr.tf_group_by(X.cut)
            >> gr.tf_head(1)
            >> gr.tf_select(X.cut, X.x)
        )
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_summarize(v=gr.var(X.x))
        df_truth = pd.DataFrame(
            {
                "cut": ["Fair", "Good", "Ideal", "Premium", "Very Good"],
                "v": [np.nan, np.nan, np.nan, np.nan, np.nan],
            }
        )
        self.assertTrue(t.equals(df_truth))

    def test_sd(self):
        df = (
            data.df_diamonds
            >> gr.tf_group_by(X.cut)
            >> gr.tf_head(3)
            >> gr.tf_select(X.cut, X.x)
            >> gr.tf_ungroup()
        )
        # straight summarize
        t = df >> gr.tf_summarize(s=gr.sd(X.x))
        df_truth = pd.DataFrame({"s": [0.829091]})
        test_vector = abs(t.s - df_truth.s)
        self.assertTrue(all(test_vector < 0.00001))
        # grouped summarize
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_summarize(s=gr.sd(X.x))
        df_truth = pd.DataFrame(
            {
                "cut": ["Fair", "Good", "Ideal", "Premium", "Very Good"],
                "s": [1.440417, 0.148436, 0.236925, 0.181934, 0.072342],
            }
        )
        test_vector = abs(t.s - df_truth.s)
        self.assertTrue(all(test_vector < 0.00001))
        # straight mutate
        t = df >> gr.tf_mutate(s=gr.sd(X.x))
        df_truth = df.copy()
        df_truth["s"] = 0.829091
        test_vector = abs(t.s - df_truth.s)
        self.assertTrue(all(test_vector < 0.00001))
        # grouped mutate
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_mutate(s=gr.sd(X.x))
        # df_truth['s'] = pd.Series([1.440417, 1.440417, 1.440417, 0.148436, 0.148436, 0.148436,
        #                            0.236925, 0.236925, 0.236925, 0.181934, 0.181934, 0.181934,
        #                            0.072342, 0.072342, 0.072342],
        #                           index=t.index)
        # test_vector = abs(t.s - df_truth.s)
        # print(t)
        # print(df_truth)
        self.assertTrue(all(test_vector < 0.00001))
        # test with single value (var undefined)
        df = (
            data.df_diamonds
            >> gr.tf_group_by(X.cut)
            >> gr.tf_head(1)
            >> gr.tf_select(X.cut, X.x)
        )
        t = df >> gr.tf_group_by(X.cut) >> gr.tf_summarize(s=gr.sd(X.x))
        df_truth = pd.DataFrame(
            {
                "cut": ["Fair", "Good", "Ideal", "Premium", "Very Good"],
                "s": [np.nan, np.nan, np.nan, np.nan, np.nan],
            }
        )
        self.assertTrue(t.equals(df_truth))

    def test_quant(self):
        df = pd.DataFrame(data={"x": [0, 0.25, 0.5, 0.75, 1]})

        df_t_25 = pd.DataFrame({"q": [0.25]})
        df_t_50 = pd.DataFrame({"q": [0.50]})
        df_t_75 = pd.DataFrame({"q": [0.75]})

        df_c_25 = df >> gr.tf_summarize(q=gr.quant(X.x, p=0.25))
        df_c_50 = df >> gr.tf_summarize(q=gr.quant(X.x, p=0.50))
        df_c_75 = df >> gr.tf_summarize(q=gr.quant(X.x, p=0.75))

        self.assertTrue(df_t_25.equals(df_c_25))
        self.assertTrue(df_t_50.equals(df_c_50))
        self.assertTrue(df_t_75.equals(df_c_75))

    def test_rsq(self):
        # Known case; Rsq = 3/4
        y_meas = pd.Series([-1, 0, +1])
        y_fit = pd.Series([-0.5, 0, +0.5])
        rsq_comp = gr.rsq(y_fit, y_meas)

        self.assertTrue(rsq_comp, 3 / 4)

    def test_corr(self):
        df_data = gr.df_make(x=[1., 2., 3., 4.])
        df_data["y"] = 0.5 * df_data.x
        df_data["z"] = - 0.5 * df_data.x

        self.assertTrue(abs(gr.corr(df_data.x, df_data.y) - 1.0) < 1e-6)
        self.assertTrue(abs(gr.corr(df_data.x, df_data.z) + 1.0) < 1e-6)
