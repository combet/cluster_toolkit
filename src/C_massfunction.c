#include "C_massfunction.h"
#include "C_bias.h"

#include "gsl/gsl_integration.h"
#include "gsl/gsl_sf.h"
#include "gsl/gsl_spline.h"
#include <math.h>

#define TOL 1e-6 //Used for the tinker bias
#define rhomconst 2.77533742639e+11
//1e4*3.*Mpcperkm*Mpcperkm/(8.*PI*G); units are SM h^2/Mpc^3
#define workspace_size 8000
#define del 1e-8

///////////////// G(sigma) multiplicity below ///////////////////
double G_at_sigma(double sigma, double d, double e, double f, double g){
  double*sig = (double*)malloc(sizeof(double));
  sig[0] = sigma;
  double*G = (double*)malloc(sizeof(double));
  G_at_sigma_arr(sig, 1, d, e, f, g, G);
  double res = G[0];
  free(sig);
  free(G);
  return res;
}

int G_at_sigma_arr(double*sigma, int Ns, double d, double e, double f, double g, double*G){
  //Compute the prefactor B
  double d2 = 0.5*d;
  double gamma_d2 = gsl_sf_gamma(d2);
  double f2 = 0.5*f;
  double gamma_f2 = gsl_sf_gamma(f2);
  double B = 2./(pow(e, d)*pow(g, -d2)*gamma_d2 + pow(g, -f2)*gamma_f2);
  int i;
  for(i = 0; i < Ns; i++){
    G[i] = B*exp(-g/(sigma[i]*sigma[i]))*(pow(sigma[i]/e, -d)+pow(sigma[i], -f));
  }
  return 0;
}

double G_at_M(double M, double*k, double*P, int Nk, double om, double d, double e, double f, double g){
  double*Marr = (double*)malloc(sizeof(double));
  Marr[0] = M;
  double*G = (double*)malloc(sizeof(double));
  G_at_M_arr(Marr, 1, k, P, Nk, om, d, e, f, g, G);
  double res = G[0];
  free(Marr);
  free(G);
  return res;
}

int G_at_M_arr(double*M, int NM, double*k, double*P, int Nk, double om, double d, double e, double f, double g, double*G){
  double*sigma = (double*)malloc(sizeof(double)*NM);
  sigma2_at_M_arr(M, NM, k, P, Nk, om, sigma);
  int i;
  for(i = 0; i < NM; i++){
    sigma[i] = sqrt(sigma[i]);
  }
  G_at_sigma_arr(sigma, NM, d, e, f, g, G);
  free(sigma);
  return 0;
}

///////////////// dndM functions below ///////////////////

double dndM_at_M(double M, double*k, double*P, int Nk, double om, double d, double e, double f, double g){
  double*Marr = (double*)malloc(sizeof(double));
  double*dndM = (double*)malloc(sizeof(double));
  double result;
  Marr[0] = M;
  dndM_at_M_arr(Marr, 1, k, P, Nk, om, d, e, f, g, dndM);
  result = dndM[0];
  free(Marr);
  free(dndM);
  return result;
}

int dndM_at_M_arr(double*M, int NM, double*k, double*P, int Nk, double om, double d, double e, double f, double g, double*dndM){
  double rhom = om*rhomconst;
  //Compute all sigma(M) arrays
  double*M_top = (double*)malloc(sizeof(double)*NM);
  double*M_bot = (double*)malloc(sizeof(double)*NM);
  double*sigma = (double*)malloc(sizeof(double)*NM);
  double*sigma_top = (double*)malloc(sizeof(double)*NM);
  double*sigma_bot = (double*)malloc(sizeof(double)*NM);
  int i;
  double dM = 0;
  for(i = 0; i < NM; i++){
    dM = del*M[i];
    M_top[i] = M[i]-dM*0.5;
    M_bot[i] = M[i]+dM*0.5;
  }
  //Can reduce these to one function call by using a longer array
  sigma2_at_M_arr(M, NM, k, P, Nk, om, sigma);
  sigma2_at_M_arr(M_top, NM, k, P, Nk, om, sigma_top);
  sigma2_at_M_arr(M_bot, NM, k, P, Nk, om, sigma_bot);
  for(i = 0; i < NM; i++){
    sigma[i] = sqrt(sigma[i]);
    sigma_top[i] = sqrt(sigma_top[i]);
    sigma_bot[i] = sqrt(sigma_bot[i]);
  }
  //Compute g(sigma)
  double*Gsigma = (double*)malloc(sizeof(double)*NM);
  G_at_sigma_arr(sigma, NM, d, e, f, g, Gsigma);
  double*dlnsiginvdm = (double*)malloc(sizeof(double)*NM);
  for(i = 0; i < NM; i++){
    dM = del*M[i];
    dlnsiginvdm[i] = log(sigma_top[i]/sigma_bot[i])/dM;
    dndM[i] = Gsigma[i]*rhom/M[i]*dlnsiginvdm[i];
  }
  free(M_top);
  free(M_bot);
  free(sigma);
  free(sigma_top);
  free(sigma_bot);
  free(Gsigma);
  free(dlnsiginvdm);
  return 0;
}

///////////////// N in bin functions below ///////////////////

double n_in_bin(double Mlo, double Mhi, double*M, double*dndM, int NM){
  double*N = (double*)malloc(sizeof(double));
  double*edges = (double*)malloc(2*sizeof(double));
  edges[0] = Mlo;
  edges[1] = Mhi;
  n_in_bins(edges, 2, M, dndM, NM, N);
  double res = N[0];
  free(N);
  free(edges);
  return res;
}

int n_in_bins(double*edges, int Nedges, double*M, double*dndM, int NM, double*N){
  //Note: N is one element less long than edges
  gsl_spline*spline = gsl_spline_alloc(gsl_interp_cspline, NM);
  gsl_spline_init(spline, M, dndM, NM);
  gsl_interp_accel*acc = gsl_interp_accel_alloc();
  int i;
  for(i = 0; i < Nedges-1; i++){
    N[i] = gsl_spline_eval_integ(spline, edges[i], edges[i+1], acc);
  }
  gsl_spline_free(spline);
  gsl_interp_accel_free(acc);
  return 0;
}
