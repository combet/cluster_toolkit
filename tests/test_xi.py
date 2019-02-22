import pytest
from cluster_toolkit import xi
from os.path import dirname, join
import numpy as np
import numpy.testing as npt

#Halo properties that are inputs
r = 1.0 #Mpc/h
ra = np.array([0.1, 1.0, 10.0]) #Mpc/h
Mass = 1e14 #Msun/h
conc = 5 #concentration; no units, for NFW
rscale = 1.0 #Mph/h; for Einasto
alpha = 0.19 #typical value; for Einasto
Omega_m = 0.3 #arbitrary
datapath = "./data_for_testing/"
knl = np.loadtxt(join(dirname(__file__),datapath+"knl.txt")) #h/Mpc; wavenumber
pnl = np.loadtxt(join(dirname(__file__),datapath+"pnl.txt")) #[Mpc/h]^3 nonlinear power spectrum
klin = np.loadtxt(join(dirname(__file__),datapath+"klin.txt")) #h/Mpc; wavenumber
plin = np.loadtxt(join(dirname(__file__),datapath+"plin.txt")) #[Mpc/h]^3 linear power spectrum

def test_exceptions_xi_nfw_at_r():
    with pytest.raises(TypeError):
        xi.xi_nfw_at_r() #No args
        xi.xi_nfw_at_r(r, Mass, conc) #Too few args
        xi.xi_nfw_at_r(r, Mass, conc, Omega_m, Omega_m) #Too many args
        xi.xi_nfw_at_r("a string", Mass, conc, Omega_m, Omega_m) #Wrong type

def test_outputs_xi_nfw_at_r():
    #List vs. numpy.array
    npt.assert_array_equal(xi.xi_nfw_at_r(ra, Mass, conc, Omega_m), xi.xi_nfw_at_r(ra.tolist(), Mass, conc, Omega_m))
    #Single value vs numpy.array
    arrout = xi.xi_nfw_at_r(ra, Mass, conc, Omega_m)
    for i in range(len(ra)):
        npt.assert_equal(xi.xi_nfw_at_r(ra[i], Mass, conc, Omega_m), arrout[i])

def test_exceptions_xi_einasto_at_r():
    with pytest.raises(TypeError):
        xi.xi_einasto_at_r() #No args
        xi.xi_einasto_at_r(r, Mass, conc, alpha) #Too few args
        xi.xi_einasto_at_r(r, Mass, conc, alpha, Omega_m, Omega_m) #Too many args
        xi.xi_einasto_at_r("a string", Mass, conc, alpha, Omega_m, Omega_m) #Wrong type

def test_outputs_xi_einasto_at_r():
    #List vs. numpy.array
    npt.assert_array_equal(xi.xi_einasto_at_r(ra, Mass, conc, alpha, Omega_m), xi.xi_einasto_at_r(ra.tolist(), Mass, conc, alpha, Omega_m))
    #Single value vs numpy.array
    arrout = xi.xi_einasto_at_r(ra, Mass, conc, alpha, Omega_m)
    for i in range(len(ra)):
        npt.assert_equal(xi.xi_einasto_at_r(ra[i], Mass, conc, alpha, Omega_m), arrout[i])

def test_xi_mm_at_r():
    #List vs. numpy.array
    npt.assert_array_equal(xi.xi_mm_at_r(ra, knl, pnl), xi.xi_mm_at_r(ra.tolist(), knl, pnl))
    #Single value vs numpy.array
    arr1 = xi.xi_mm_at_r(ra, knl, pnl)
    arr2 = np.array([xi.xi_mm_at_r(ri, knl, pnl) for ri in ra])
    npt.assert_array_equal(arr1, arr2)

def test_xi_mm_at_r_exact():
    #List vs. numpy.array
    npt.assert_array_equal(xi.xi_mm_at_r(ra, knl, pnl, exact=True), xi.xi_mm_at_r(ra.tolist(), knl, pnl, exact=True))
    #Single value vs numpy.array
    arr1 = xi.xi_mm_at_r(ra, knl, pnl, exact=True)
    arr2 = np.array([xi.xi_mm_at_r(ri, knl, pnl, exact=True) for ri in ra])
    npt.assert_array_equal(arr1, arr2)

def test_xi_DK_at_r():
    #required arguments
    rs = be = se = 1.
    arr1 = xi.xi_DK(ra, Mass, rs, be, se, klin, plin, Omega_m)
    arr2 = np.array([xi.xi_DK(ri, Mass, rs, be, se, klin, plin, Omega_m) for ri in ra])
    npt.assert_array_equal(arr1, arr2)

def test_nfw_mass_dependence():
    masses = np.array([1e13, 1e14, 1e15])
    for i in range(len(masses)-1):
        xi1 = xi.xi_nfw_at_r(ra, masses[i], conc, Omega_m)
        xi2 = xi.xi_nfw_at_r(ra, masses[i+1], conc, Omega_m)
        npt.assert_array_less(xi1, xi2)

def test_einasto_mass_dependence():
    masses = np.array([1e13, 1e14, 1e15])
    for i in range(len(masses)-1):
        xi1 = xi.xi_einasto_at_r(ra, masses[i], conc, alpha, Omega_m)
        xi2 = xi.xi_einasto_at_r(ra, masses[i+1], conc, alpha, Omega_m)
        npt.assert_array_less(xi1, xi2)

def test_combination():
    xinfw = xi.xi_nfw_at_r(ra, Mass, conc, Omega_m)
    ximm = xi.xi_mm_at_r(ra, knl, pnl)
    from cluster_toolkit import bias
    b = bias.bias_at_M(Mass, klin, plin, Omega_m)
    xi2h = xi.xi_2halo(b, ximm)
    xihm = xi.xi_hm(xinfw, xi2h)
    xihm2 = xi.xi_hm(xinfw, xi2h, combination='max')
    npt.assert_array_equal(xihm, xihm2)
    xihm2 = xi.xi_hm(xinfw, xi2h, combination='sum')
    npt.assert_raises(AssertionError, npt.assert_array_equal, xihm, xihm2)
    with pytest.raises(Exception):
        xi.xi_hm(xinfw, xi2h, combination='blah')
if __name__ == "__main__":
    #test_einasto_mass_dependence()
    test_combination()
