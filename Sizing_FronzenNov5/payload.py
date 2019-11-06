import gpkit
from gpkit import Model, Variable
from gpkit.constraints.tight import Tight
from gpkit.constraints.bounded import Bounded
from gpkit import ureg


class Payload(Model):

    def setup(self):
        constraints = []
        components = self.components = []

        ######### components ##########

        m = self.m = Variable("m", 4, "kg", "Mass of Payload")

        if len(components) > 0:
            constraints += [Tight([m >= sum(comp.m for comp in components)])]

        ######### constraints #########

        # constraints += [m >= 4.5 * ureg.kg]

        return [constraints, components]
