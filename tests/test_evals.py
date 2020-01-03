import numpy as np
import pandas as pd
import unittest

from collections import OrderedDict as od
from context import core
from context import grama as gr
from context import models
from pyDOE import lhs

##################################################
class TestDefaults(unittest.TestCase):

    def setUp(self):
        # 2D identity model with permuted df inputs
        domain_2d = gr.Domain(bounds={"x": [-1., +1], "y": [0., 1.]})
        marginals = {}
        marginals["x"] = gr.MarginalNamed(
            d_name="uniform",
            d_param={"loc":-1, "scale": 2}
        )
        marginals["y"] = gr.MarginalNamed(
            sign=-1,
            d_name="uniform",
            d_param={"loc": 0, "scale": 1}
        )

        self.model_2d = gr.Model(
            functions=[
                gr.Function(
                    lambda x: [x[0], x[1]],
                    ["x", "y"],
                    ["f", "g"],
                    "test",
                    0
                )
            ],
            domain=domain_2d,
            density=gr.Density(marginals=marginals)
        )

        ## Correct results
        self.df_2d_nominal = pd.DataFrame(
            data={"x": [0.0], "y": [0.5], "f": [0.0], "g": [0.5]}
        )
        self.df_2d_grad = pd.DataFrame(
            data={"Df_Dx": [1.0], "Dg_Dx": [0.0], "Df_Dy": [0.0], "Dg_Dy": [1.0]}
        )
        self.df_2d_qe = pd.DataFrame(
            data={"x": [0.0], "y": [0.1], "f": [0.0], "g": [0.1]}
        )

    ## Test default evaluations

    def test_nominal(self):
        """Checks the nominal evaluation is accurate
        """
        df_res = gr.eval_nominal(self.model_2d)

        ## Accurate
        self.assertTrue(
            np.allclose(self.df_2d_nominal, df_res)
        )

        ## Pass-through
        self.assertTrue(
            np.allclose(
                self.df_2d_nominal.drop(["f", "g"], axis=1),
                gr.eval_nominal(self.model_2d, skip=True)
            )
        )

    def test_grad_fd_accurate(self):
        """Checks the FD is accurate
        """
        df_grad = gr.eval_grad_fd(
            self.model_2d,
            df_base=self.df_2d_nominal,
            append=False
        )

        self.assertTrue(
            np.allclose(df_grad[self.df_2d_grad.columns], self.df_2d_grad)
        )

    def test_conservative(self):
        ## Accuracy
        df_res = gr.eval_conservative(
            self.model_2d,
            quantiles=[0.1, 0.1]
        )

        self.assertTrue(np.allclose(self.df_2d_qe, df_res))

        ## Repeat scalar value
        self.assertTrue(np.allclose(
            self.df_2d_qe,
            gr.eval_conservative(self.model_2d, quantiles=0.1)
        ))

        ## Pass-through
        self.assertTrue(np.allclose(
            self.df_2d_qe.drop(["f", "g"], axis=1),
            gr.eval_conservative(self.model_2d, quantiles=0.1, skip=True)
        ))

##################################################
class TestRandomSampling(unittest.TestCase):
    def setUp(self):
        self.md = gr.Model() >> \
                  gr.cp_function(fun=lambda x: x, var=1, out=1) >> \
                  gr.cp_marginals(x0={"dist": "uniform", "loc": 0, "scale": 1})

        self.md_2d = gr.Model() >> \
                  gr.cp_function(fun=lambda x: x[0], var=2, out=1) >> \
                  gr.cp_marginals(
                      x0={"dist": "uniform", "loc": 0, "scale": 1},
                      x1={"dist": "uniform", "loc": 0, "scale": 1}
                  )

    def test_lhs(self):
        ## Accurate
        n=2
        df_res = gr.eval_lhs(self.md_2d, n=n, df_det="nom", seed=101)

        np.random.seed(101)
        df_truth = pd.DataFrame(data=lhs(2, samples=n), columns=["x0", "x1"])
        df_truth["y0"] = df_truth["x0"]

        pd.testing.assert_frame_equal(
            df_res,
            df_truth,
            check_exact=False,
            check_dtype=False,
            check_column_type=False
        )

        ## Rounding
        df_round = gr.eval_lhs(self.md_2d, n=n+0.1, df_det="nom", seed=101)

        pd.testing.assert_frame_equal(
            df_round,
            df_truth,
            check_exact=False,
            check_dtype=False,
            check_column_type=False
        )

        ## Pass-through
        df_pass = gr.eval_lhs(self.md_2d, n=n, skip=True, df_det="nom", seed=101)

        pd.testing.assert_frame_equal(
            df_pass,
            df_truth[["x0", "x1"]],
            check_exact=False,
            check_dtype=False,
            check_column_type=False
        )

    def test_monte_carlo(self):
        ## Accurate
        n=2
        df_res = gr.eval_monte_carlo(self.md, n=n, df_det="nom", seed=101)

        np.random.seed(101)
        df_truth = pd.DataFrame({"x0": np.random.random(n)})
        df_truth["y0"] = df_truth["x0"]

        pd.testing.assert_frame_equal(
            df_res,
            df_truth,
            check_exact=False,
            check_dtype=False,
            check_column_type=False
        )

        ## Rounding
        df_round = gr.eval_monte_carlo(self.md, n=n+0.1, df_det="nom", seed=101)

        pd.testing.assert_frame_equal(
            df_round,
            df_truth,
            check_exact=False,
            check_dtype=False,
            check_column_type=False
        )

        ## Pass-through
        df_pass = gr.eval_monte_carlo(
            self.md,
            n=n,
            skip=True,
            df_det="nom",
            seed=101
        )

        pd.testing.assert_frame_equal(
            df_pass[["x0"]],
            df_truth[["x0"]],
            check_exact=False,
            check_dtype=False,
            check_column_type=False
        )

##################################################
class TestRandom(unittest.TestCase):

    def setUp(self):
        self.md = models.make_test()

    def test_monte_carlo(self):
        df_min = gr.eval_monte_carlo(self.md, df_det="nom")
        self.assertTrue(df_min.shape == (1, self.md.n_var + self.md.n_out))
        self.assertTrue(
            set(df_min.columns) == set(self.md.var + self.md.out)
        )

        df_seeded = gr.eval_monte_carlo(self.md, df_det="nom", seed=101)
        df_piped = self.md >> gr.ev_monte_carlo(df_det="nom", seed=101)
        self.assertTrue(df_seeded.equals(df_piped))

        df_skip = gr.eval_monte_carlo(self.md, df_det="nom", skip=True)
        self.assertTrue(
            set(df_skip.columns) == set(self.md.var)
        )

        df_noappend = gr.eval_monte_carlo(self.md, df_det="nom", append=False)
        self.assertTrue(
            set(df_noappend.columns) == set(self.md.out)
        )

    def test_lhs(self):
        df_min = gr.eval_lhs(self.md, df_det="nom")
        self.assertTrue(df_min.shape == (1, self.md.n_var + self.md.n_out))
        self.assertTrue(
            set(df_min.columns) == set(self.md.var + self.md.out)
        )

        df_seeded = gr.eval_lhs(self.md, df_det="nom", seed=101)
        df_piped = self.md >> gr.ev_lhs(df_det="nom", seed=101)
        self.assertTrue(df_seeded.equals(df_piped))

        df_skip = gr.eval_lhs(self.md, df_det="nom", skip=True)
        self.assertTrue(
            set(df_skip.columns) == set(self.md.var)
        )

        df_noappend = gr.eval_lhs(self.md, df_det="nom", append=False)
        self.assertTrue(
            set(df_noappend.columns) == set(self.md.out)
        )

    def test_sinews(self):
        df_min = gr.eval_sinews(self.md, df_det="nom")
        self.assertTrue(
            set(df_min.columns) == \
            set(self.md.var + self.md.out + ["sweep_var", "sweep_ind"])
        )
        self.assertTrue(df_min._plot_info["type"] == "sinew_outputs")

        df_seeded = gr.eval_sinews(self.md, df_det="nom", seed=101)
        df_piped = self.md >> gr.ev_sinews(df_det="nom", seed=101)
        self.assertTrue(df_seeded.equals(df_piped))

        df_skip = gr.eval_sinews(self.md, df_det="nom", skip=True)
        self.assertTrue(df_skip._plot_info["type"] == "sinew_inputs")

    def test_hybrid(self):
        df_min = gr.eval_hybrid(self.md, df_det="nom")
        self.assertTrue(
            set(df_min.columns) == \
            set(self.md.var + self.md.out + ["hybrid_var"])
        )
        self.assertTrue(df_min._meta["type"] == "eval_hybrid")

        df_seeded = gr.eval_hybrid(self.md, df_det="nom", seed=101)
        df_piped = self.md >> gr.ev_hybrid(df_det="nom", seed=101)
        self.assertTrue(df_seeded.equals(df_piped))

        df_total = gr.eval_hybrid(self.md, df_det="nom", plan="total")
        self.assertTrue(
            set(df_total.columns) == \
            set(self.md.var + self.md.out + ["hybrid_var"])
        )
        self.assertTrue(df_total._meta["type"] == "eval_hybrid")

        df_skip = gr.eval_hybrid(self.md, df_det="nom", skip=True)
        self.assertTrue(
            set(df_skip.columns) == \
            set(self.md.var + ["hybrid_var"])
        )

## Run tests
if __name__ == "__main__":
    unittest.main()
