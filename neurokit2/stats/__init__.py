"""Submodule for NeuroKit."""

from .cluster import cluster
from .cluster_findnumber import cluster_findnumber
from .cluster_quality import cluster_quality
from .correlation import cor
from .density import density
from .distance import distance
from .fit_error import fit_error, fit_mse, fit_r2, fit_rmse
from .fit_loess import fit_loess
from .fit_mixture import fit_mixture
from .fit_polynomial import fit_polynomial, fit_polynomial_findorder
from .hdi import hdi
from .mad import mad
from .rescale import rescale
from .standardize import standardize
from .summary import summary_plot

__all__ = [
    "standardize",
    "hdi",
    "mad",
    "cor",
    "density",
    "distance",
    "rescale",
    "fit_loess",
    "fit_polynomial",
    "fit_polynomial_findorder",
    "fit_mixture",
    "fit_error",
    "fit_mse",
    "fit_rmse",
    "fit_r2",
    "summary_plot",
    "cluster",
    "cluster_quality",
    "cluster_findnumber",
]
