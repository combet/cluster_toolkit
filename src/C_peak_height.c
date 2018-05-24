#include "C_peak_height.h"

#include "gsl/gsl_integration.h"
#include "gsl/gsl_spline.h"

#include <math.h>
#include <stdio.h>

#define ABSERR 0.0
#define RELERR 1e-6
#define delta_c 1.686 //Critical collapse density
#define rhocrit 2.77533742639e+11
//1e4*3.*Mpcperkm*Mpcperkm/(8.*PI*G); units are Msun h^2/Mpc^3
#define workspace_size 8000
#define KEY 4 //Used for GSL QAG function

typedef struct integrand_params{
  gsl_spline *spline;
  gsl_interp_accel *acc;
  double r;
  double*kp; //pointer to wavenumbers
  double*Pp; //pointer to P(k) array
  int Nk; //length of k and P arrays
}integrand_params;

//Redefined these, even though they appear in C_bias.c
double M_to_R(double M, double Omega_m){
  //Lagrangian radius Mpc/h
  return pow(M/(1.33333333333*M_PI*rhocrit*Omega_m),0.3333333333);
}

double R_to_M(double R, double Omega_m){
  //Lagrangian mass Msun/h
  return R*R*R*1.33333333333*M_PI*rhocrit*Omega_m;
}

double sigma2_integrand(double lk, void*params){
  integrand_params pars = *(integrand_params*)params;
  double k = exp(lk);
  double x = k*pars.r;
  double P = gsl_spline_eval(pars.spline, k, pars.acc);
  double w = (sin(x)-x*cos(x))*3.0/(x*x*x); //Window function
  return k*k*k*P*w*w;
}

///////////// linar matter variance functions /////////////

double sigma2_at_R(double R, double*k, double*P, int Nk){
  double*Rs = (double*)malloc(sizeof(double));
  double*s2 = (double*)malloc(sizeof(double));
  double result;
  Rs[0] = R;
  sigma2_at_R_arr(Rs, 1, k, P, Nk, s2);
  result = s2[0];
  free(Rs);
  free(s2);
  return result;
}

double sigma2_at_M(double M, double*k, double*P, int Nk, double om){
  double R=M_to_R(M, om);
  return sigma2_at_R(R, k, P, Nk);
}

int sigma2_at_R_arr(double*R, int NR,  double*k, double*P, int Nk, double*s2){
  //Initialize GSL things and the integrand structure.
  gsl_spline*spline = gsl_spline_alloc(gsl_interp_cspline,Nk);
  gsl_interp_accel*acc = gsl_interp_accel_alloc();
  gsl_integration_workspace*workspace = gsl_integration_workspace_alloc(workspace_size);
  gsl_function F;
  integrand_params*params = (integrand_params*)malloc(sizeof(integrand_params));
  double lkmin = log(k[0]);
  double lkmax = log(k[Nk-1]);
  double result,abserr;
  int i;
  gsl_spline_init(spline,k,P,Nk);
  params->spline = spline;
  params->acc = acc;
  params->kp = k;
  params->Pp = P;
  params->Nk = Nk;
  F.function = &sigma2_integrand;
  F.params = params;
  for(i = 0; i < NR; i++){
    params->r = R[i];
    gsl_integration_qag(&F, lkmin, lkmax, ABSERR, RELERR, workspace_size, KEY, workspace, &result, &abserr);
    s2[i] = result/(2*M_PI*M_PI);
  }
  gsl_spline_free(spline);
  gsl_interp_accel_free(acc);
  gsl_integration_workspace_free(workspace);
  free(params);
  return 0;
}

int sigma2_at_M_arr(double*M, int NM,  double*k, double*P, int Nk, double om, double*s2){
  int i;
  double*R = (double*)malloc(sizeof(double)*NM);
  for(i = 0; i < NM; i++){
    R[i] = M_to_R(M[i], om);
  }
  sigma2_at_R_arr(R, NM, k, P, Nk, s2);
  free(R);
  return 0;
}

///////////PEAK HEIGHT FUNCTIONS///////////

double nu_at_R(double R, double*k, double*P, int Nk){
  return delta_c/sqrt(sigma2_at_R(R, k, P, Nk));
}

double nu_at_M(double M, double*k, double*P, int Nk, double om){
  double R=M_to_R(M, om);
  return nu_at_R(R, k, P, Nk);
}

int nu_at_R_arr(double*R, int NR, double*k, double*P, int Nk, double*nu){
  int i;
  double*s2 = (double*)malloc(sizeof(double)*NR);
  sigma2_at_R_arr(R, NR, k, P, Nk, s2);
  for(i = 0; i < NR; i++){
    nu[i] = delta_c/sqrt(s2[i]);
  }
  free(s2);
  return 0;
}

int nu_at_M_arr(double*M, int NM, double*k, double*P, int Nk, double om, double*nu){
  int i;
  double*R = (double*)malloc(sizeof(double)*NM);
  for(i = 0; i < NM; i++){
    R[i] = M_to_R(M[i], om);
  }
  nu_at_R_arr(R, NM, k, P, Nk, nu);
  free(R);
  return 0;
}