__all__ = [
    "eval_nls",
    "ev_nls",
    "eval_min",
    "ev_min",
]

from grama import add_pipe, pipe, custom_formatwarning, df_make
from grama import eval_df, eval_nominal, tran_outer
from numpy import Inf, isfinite
from pandas import DataFrame, concat
from scipy.optimize import minimize
from toolz import curry

## Nonlinear least squares
# --------------------------------------------------
@curry
def eval_nls(
    model,
    df_data=None,
    out=None,
    var_fix=None,
    append=False,
    tol=1e-3,
    maxiter=25,
    nrestart=1,
):
    r"""Estimate with Nonlinear Least Squares (NLS)

    Estimate best-fit variable levels with nonlinear least squares (NLS).

    Args:
        model (gr.Model): Model to analyze. All model variables
            selected for fitting must be bounded or random. Deterministic
            variables may have semi-infinite bounds.
        df_data (DataFrame): Data for estimating parameters. Variables not
            found in df_data optimized in fitting.
        out (list or None): Output contributions to consider in computing MSE.
            Assumed to be model.out if left as None.
        var_fix (list or None): Variables to fix to nominal levels. Note that
            variables with domain width zero will automatically be fixed.
        append (bool): Append metadata? (Initial guess, MSE, optimizer status)
        tol (float): Optimizer convergence tolerance
        maxiter (int): Optimizer maximum iterations
        nrestart (int): Number of restarts; beyond nrestart=1 random
            restarts are used.

    Returns:
        DataFrame: Results of estimation

    Examples:
        >>> import grama as gr
        >>> from grama.data import df_trajectory_full
        >>> from grama.models import make_trajectory_linear
        >>>
        >>> md_trajectory = make_trajectory_linear()
        >>>
        >>> df_fit = (
        >>>     md_trajectory
        >>>     >> gr.ev_nls(df_data=df_trajectory_full)
        >>> )
        >>>
        >>> print(df_fit)

    """
    ## Check `out` invariants
    if out is None:
        out = model.out
        print("... eval_nls setting out = {}".format(out))
    set_diff = set(out).difference(set(df_data.columns))
    if len(set_diff) > 0:
        raise ValueError(
            "out must be subset of df_data.columns\n"
            + "difference = {}".format(set_diff)
        )

    ## Determine variables to be fixed
    if var_fix is None:
        var_fix = set()
    else:
        var_fix = set(var_fix)
    for var in model.var_det:
        wid = model.domain.get_width(var)
        if wid == 0:
            var_fix.add(var)
    print("... eval_nls setting var_fix = {}".format(list(var_fix)))

    ## Determine variables for evaluation
    var_feat = set(model.var).intersection(set(df_data.columns))
    print("... eval_nls setting var_feat = {}".format(list(var_feat)))

    ## Determine variables for fitting
    var_fit = set(model.var).difference(var_fix.union(var_feat))
    if len(var_fit) == 0:
        raise ValueError(
            "No var selected for fitting!\n"
            + "Try checking model bounds and df_data.columns."
        )

    ## Separate var_fit into det and rand
    var_fit_det = list(set(model.var_det).intersection(var_fit))
    var_fit_rand = list(set(model.var_rand).intersection(var_fit))

    ## Construct bounds, fix var_fit order
    var_fit = var_fit_det + var_fit_rand
    bounds = []
    var_prob = []
    for var in var_fit_det:
        if not isfinite(model.domain.get_nominal(var)):
            var_prob.append(var)
        bounds.append(model.domain.get_bound(var))
    if len(var_prob) > 0:
        raise ValueError(
            "all variables to be fitted must finite nominal value\n"
            + "offending var = {}".format(var_prob)
        )

    for var in var_fit_rand:
        bounds.append(
            (model.density.marginals[var].q(0), model.density.marginals[var].q(1),)
        )

    ## Determine initial guess points
    df_nom = eval_nominal(model, df_det="nom", skip=True)

    df_init = df_nom[var_fit]
    if nrestart > 1:
        raise NotImplementedError()

    ## Iterate over initial guesses
    df_res = DataFrame()
    for i in range(df_init.shape[0]):
        x0 = df_init[var_fit].iloc[i].values
        ## Build evaluator
        def objective(x):
            """x = [var_fit]"""
            ## Evaluate model
            df_var = tran_outer(
                df_data[var_feat],
                concat(
                    (df_nom[var_fix].iloc[[0]], df_make(**dict(zip(var_fit, x)))),
                    axis=1,
                ),
            )
            df_res = eval_df(model, df=df_var)

            ## Compute joint MSE
            return ((df_res[out].values - df_data[out].values) ** 2).mean()

        ## Run optimization
        res = minimize(
            objective,
            x0,
            args=(),
            method="SLSQP",
            jac=False,
            tol=tol,
            options={"maxiter": maxiter, "disp": False},
            bounds=bounds,
        )

        df_res = concat(
            (
                df_res,
                df_make(
                    **dict(zip(var_fit, res.x)),
                    **dict(zip(map(lambda s: s + "_0", var_fit), x0)),
                    status=res.status,
                    mse=res.fun,
                ),
            ),
            axis=0,
        )

    ## Post-process
    if append:
        return df_res
    else:
        return df_res[var_fit]


ev_nls = add_pipe(eval_nls)

## Minimize
# --------------------------------------------------
@curry
def eval_min(
    model,
    out_min=None,
    out_geq=None,
    out_eq=None,
    method="SLSQP",
    tol=1e-6,
    nrestart=1,
    maxiter=50,
    df_start=None,
):
    r"""Constrained minimization using functions from a model

    Perform constrained minimization using functions from a model. Model must
    have deterministic variables only.

    Wrapper for scipy.optimize.minimize

    Args:
        model (gr.Model): Model to analyze. All model variables must be
            deterministic.
        out_min (str): Output to use as minimization objective.
        out_geq (None OR list of str): Outputs to use as geq constraints; var >= 0
        out_eq (None OR list of str): Outputs to use as equality constraints; var == 0

        method (str): Optimization method;
        tol (float): Optimization objective convergence tolerance
        nrestart (int): Number of restarts; beyond nrestart=1 random
            restarts are used.
        df_start (None or DataFrame):

    Returns:
        DataFrame: Results of optimization

    Examples:
        >>> import grama as gr
        >>> md = (
        >>>     gr.Model("Constrained Rosenbrock")
        >>>     >> gr.cp_function(
        >>>         fun=lambda x: (1 - x[0])**2 + 100*(x[1] - x[0]**2)**2,
        >>>         var=["x", "y"],
        >>>         out=["c"],
        >>>     )
        >>>     >> gr.cp_function(
        >>>         fun=lambda x: -( (x[0] - 1)**3 - x[1] + 1 ),
        >>>         var=["x", "y"],
        >>>         out=["g1"],
        >>>     )
        >>>     >> gr.cp_function(
        >>>         fun=lambda x: -( x[0] + x[1] - 2 ),
        >>>         var=["x", "y"],
        >>>         out=["g2"],
        >>>     )
        >>> )
        >>> md >> gr.ev_min(
        >>>     out_min="c",
        >>>     out_geq=["g1", "g2"]
        >>> )

    """
    ## Check that model has only deterministic variables
    if model.n_var_rand > 0:
        raise ValueError("model must have no random variables")
    ## Check that objective is in model
    if not (out_min in model.out):
        raise ValueError("model must contain out_min")
    ## Check that constraints is in model
    if not (out_geq is None):
        out_diff = set(out_geq).difference(set(model.out))
        if len(out_diff) > 0:
            raise ValueError(
                "model must contain each out_geq; missing {}".format(out_diff)
            )
    if not (out_eq is None):
        out_diff = set(out_eq).difference(set(model.out))
        if len(out_diff) > 0:
            raise ValueError(
                "model must contain each out_eq; missing {}".format(out_diff)
            )

    ## Formulate initial guess
    if df_start is None:
        df_start = eval_nominal(model, df_det="nom", skip=True)
    x0 = df_start[model.var]

    ## Factory for wrapping model's output
    def make_fun(out):
        def fun(x):
            df = DataFrame([x], columns=model.var)
            df_res = eval_df(model, df)
            return df_res[out]

        return fun

    ## Create helper functions for constraints
    constraints = []

    if not (out_geq is None):
        for out in out_geq:
            constraints.append(
                {"type": "ineq", "fun": make_fun(out),}
            )

    if not (out_eq is None):
        for out in out_eq:
            constraints.append(
                {"type": "eq", "fun": make_fun(out),}
            )

    ## Run optimization
    res = minimize(
        make_fun(out_min),
        x0,
        args=(),
        method=method,
        jac=False,
        tol=tol,
        options={"maxiter": maxiter, "disp": False},
        constraints=constraints,
        # bounds=bounds,
    )

    df_res = df_make(**dict(zip(model.var, res.x)))

    return df_res


ev_min = add_pipe(eval_min)
