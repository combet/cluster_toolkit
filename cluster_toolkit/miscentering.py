"""Miscentering effects for projected profiles.

"""
import cluster_toolkit
from cluster_toolkit import _dcast
import numpy as np

def Sigma_mis_single_at_R(R, Rsigma, Sigma, M, conc, Omega_m, Rmis, delta=200):
    """Miscentered surface mass density [Msun h/pc^2 comoving] of a profile miscentered by an 
    amount Rmis Mpc/h comoving. Units are Msun h/pc^2 comoving.

    Args:
        R (float or array like): Projected radii Mpc/h comoving.
        Rsigma (array like): Projected radii of the centered surface mass density profile.
        Sigma (float or array like): Surface mass density Msun h/pc^2 comoving.
        M (float): Halo mass Msun/h.
        conc (float): concentration.
        Omega_m (float): Matter density fraction.
        Rmis (float): Miscentered distance in Mpc/h comoving.
        delta (int; optional): Overdensity, default is 200.

    Returns:
        float or array like: Miscentered projected surface mass density.

    """
    R = np.asarray(R)
    scalar_input = False
    if R.ndim == 0:
        R = R[None] #makes R 1D
        scalar_input = True
    if R.ndim > 1:
        raise Exception("R cannot be a >1D array.")
    if np.min(R) < np.min(Rsigma):
        raise Exception("Minimum R must be >= min(R_Sigma)")
    if np.max(R) > np.max(Rsigma):
        raise Exception("Maximum R must be <= max(R_Sigma)")
    Sigma_mis = np.zeros_like(R)
    cluster_toolkit._lib.Sigma_mis_single_at_R_arr(_dcast(R), len(R), _dcast(Rsigma), _dcast(Sigma),
                                                   len(Rsigma), M, conc, delta, Omega_m, Rmis, _dcast(Sigma_mis))
    if scalar_input:
        return np.squeeze(Sigma_mis)
    return Sigma_mis

def Sigma_mis_at_R(R, Rsigma, Sigma, M, conc, Omega_m, Rmis, delta=200, kernel="rayleigh"):
    """Miscentered surface mass density [Msun h/pc^2 comoving] 
    convolved with a distribution for Rmis. Units are Msun h/pc^2 comoving.

    Args:
        R (float or array like): Projected radii Mpc/h comoving.
        Rsigma (array like): Projected radii of the centered surface mass density profile.
        Sigma (float or array like): Surface mass density Msun h/pc^2 comoving.
        M (float): Halo mass Msun/h.
        conc (float): concentration.
        Omega_m (float): Matter density fraction.
        Rmis (float): Miscentered distance in Mpc/h comoving.
        delta (int; optional): Overdensity, default is 200.
        kernel (string; optional): Kernal for convolution. Options: rayleigh or gamma.

    Returns:
        float or array like: Miscentered projected surface mass density.

    """
    R = np.asarray(R)
    scalar_input = False
    if R.ndim == 0:
        R = R[None] #makes R 1D
        scalar_input = True

    #Exception checking
    if R.ndim > 1:
        raise Exception("R cannot be a >1D array.")
    if np.min(R) < np.min(Rsigma):
        raise Exception("Minimum R must be >= min(R_Sigma)")
    if np.max(R) > np.max(Rsigma):
        raise Exception("Maximum R must be <= max(R_Sigma)")
    if kernel == "rayleigh":
        integrand_switch = 0
    elif kernel == "gamma":
        integrand_switch = 1
    else:
        raise Exception("Miscentering kernel must be either "+
                        "'rayleigh' or 'gamma'")

    Sigma_mis = np.zeros_like(R)
    cluster_toolkit._lib.Sigma_mis_at_R_arr(_dcast(R), len(R), _dcast(Rsigma), _dcast(Sigma), len(Rsigma),
                                            M, conc, delta, Omega_m, Rmis, integrand_switch, _dcast(Sigma_mis))
    if scalar_input:
        return np.squeeze(Sigma_mis)
    return Sigma_mis

def DeltaSigma_mis_at_R(R, Rsigma, Sigma_mis):
    """Miscentered excess surface mass density profile at R. Units are Msun h/pc^2 comoving.

    Args:
        R (float or array like): Projected radii to evaluate profile.
        Rsigma (array like): Projected radii of miscentered Sigma profile.
        Sigma_mis (array like): Miscentered Sigma profile.

    Returns:
        float array like: Miscentered excess surface mass density profile.

    """
    R = np.asarray(R)
    scalar_input = False
    if R.ndim == 0:
        R = R[None] #makes R 1D
        scalar_input = True
    if R.ndim > 1:
        raise Exception("R cannot be a >1D array.")
    if np.min(R) < np.min(Rsigma):
        raise Exception("Minimum R must be >= min(R_Sigma)")
    if np.max(R) > np.max(Rsigma):
        raise Exception("Maximum R must be <= max(R_Sigma)")
    
    DeltaSigma_mis = np.zeros_like(R)
    cluster_toolkit._lib.DeltaSigma_mis_at_R_arr(_dcast(R), len(R), _dcast(Rsigma), _dcast(Sigma_mis),
                                                 len(Rsigma), _dcast(DeltaSigma_mis))
    if scalar_input:
        return np.squeeze(DeltaSigma_mis)
    return DeltaSigma_mis
