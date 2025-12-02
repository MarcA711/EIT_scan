import numpy as np
from iminuit import Minuit


class CsAbsorb:
    def __init__(self, y):
        self.x = np.arange(len(y))
        self.y = y
    
    def __call__(self, x0, scaling, C, slope,
                sigma1, Cgauss1, gamma1, Clorentz1,
                sigma2, Cgauss2, gamma2, Clorentz2,
                sigma3, Cgauss3, gamma3, Clorentz3,
                sigma4, Cgauss4, gamma4, Clorentz4
                ):
        
        y_fit = self.cs_absorb(x0, scaling, C, slope,
                sigma1, Cgauss1, gamma1, Clorentz1,
                sigma2, Cgauss2, gamma2, Clorentz2,
                sigma3, Cgauss3, gamma3, Clorentz3,
                sigma4, Cgauss4, gamma4, Clorentz4
                )
        
        return np.sqrt(np.sum(((y_fit-self.y)**2)/self.y))

    def cs_absorb(self, x0, scaling, C, slope,
                sigma1, Cgauss1, gamma1, Clorentz1,
                sigma2, Cgauss2, gamma2, Clorentz2,
                sigma3, Cgauss3, gamma3, Clorentz3,
                sigma4, Cgauss4, gamma4, Clorentz4
                ):
        return (C + slope*self.x - (CsAbsorb.gauß_min_lorentz(self.x, x0, sigma1, Cgauss1, gamma1, Clorentz1) + 
                CsAbsorb.gauß_min_lorentz(self.x, scaling*1.167 + x0, sigma2, Cgauss2, gamma2, Clorentz2) +
                CsAbsorb.gauß_min_lorentz(self.x, scaling*9.2 + x0, sigma3, Cgauss3, gamma3, Clorentz3) +
                CsAbsorb.gauß_min_lorentz(self.x, scaling*(9.2 + 1.167) + x0, sigma4, Cgauss4, gamma4, Clorentz4)))

    def gauß_min_lorentz(x, x0, sigma, Cgauss, gamma, Clorentz):
        return CsAbsorb.centered_gauss(x-x0, sigma, Cgauss) - CsAbsorb.centered_lorentz(x-x0, gamma, Clorentz)

    def centered_gauss(x, sigma, C):
        return C*np.exp(-((x**2)/(2*sigma**2)))

    def centered_lorentz(x, gamma, C):
        return (C*gamma)/(gamma**2 + x**2)
    
class CsFit:
    def __init__(self, data):
        self.data = data
        self.initial_values = {
            "x0": 1200,
            "scaling": 4400/9.2,
            "C": 12,
            "slope": -1/1000,
            "sigma1": 100,
            "Cgauss1": 3,
            "gamma1": 20,
            "Clorentz1": 30,
            "sigma2": 100,
            "Cgauss2": 2,
            "gamma2": 20,
            "Clorentz2": 30,
            "sigma3": 100,
            "Cgauss3": 1.5,
            "gamma3": 20,
            "Clorentz3": 30,
            "sigma4": 100,
            "Cgauss4": 2,
            "gamma4": 20,
            "Clorentz4": 30,
        }

    def fit(self):
        cs_absorb = CsAbsorb(self.data)
        m = Minuit(cs_absorb, *self.initial_values.values())
        m.migrad()

        fitted_values = {}
        for entry in m.params:
            fitted_values[entry.name] = entry.value

        x_scaled = (self.x - fitted_values["x0"]) / fitted_values["scaling"]

        return x_scaled