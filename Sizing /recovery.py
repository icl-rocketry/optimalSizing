import gpkit
from gpkit import Model, Variable
from gpkit.constraints.tight import Tight
from gpkit.constraints.bounded import Bounded
from gpkit import ureg


class Recovery(Model):

    def setup(self):
        constraints = []
        components = self.components = []

        ######### components ##########

        m = self.m = Variable("m", 3, "kg", "Mass of Recovery")
        if len(components) > 0:
            constraints += [Tight([m >= sum(comp.m for comp in components)])]

        ######### constraints #########

        #constraints += [m >= 3 * ureg.kg]

        return [constraints, components]
