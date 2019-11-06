import gpkit
from gpkit import Model, Variable
from gpkit.constraints.tight import Tight
from gpkit.constraints.loose import Loose
from gpkit.constraints.bounded import Bounded
from gpkit import ureg


class Boosters(Model):

    def setup(self):
        constraints = []
        components = self.components = []

        ######### components ##########

        m = self.m = Variable("m", "kg", "Mass of Boosters")
        if len(components) > 0:
            constraints += [Tight([m >= sum(comp.m for comp in components)])]

        ######### constraints #########

        constraints += [Loose([m >= 0.1 * ureg.kg])]

        F = self.F = Variable("F", "N", "Boosters cumulative thrust")

        t_burn = self.t_burn = Variable("t_{burn}", "s", "Booster burn time")

        c = self.c = Variable("c", 2000, "m/s", "boosters exhaust speed")

        m_prop = self.m_prop = Variable("m_{prop}", "kg", "Propellant mass of boosters")
        m_dry = self.m_dry = Variable("m_{dry}", "kg", "Dry mass of boosters")
        dmf = self.dmf = Variable("DMF", 0.7, "", "Dry mass fraction of boosters")

        constraints += [Tight([m >= m_prop + m_dry])]
        constraints += [m_dry >= dmf * m]

        # constraints += [m_prop >= F*t_burn/c]

        return [constraints, components]
