import gpkit
from gpkit import Model, Variable
from gpkit.constraints.tight import Tight
from gpkit.constraints.bounded import Bounded
from gpkit import ureg


class Structures(Model):

    def setup(self):
        # define the structures of the rocket.
        # includes upper rocket airframe, nosecone, fins
        constraints = []
        components = self.components = []

        ######### components ##########

        m = self.m = Variable("m", "kg", "Mass of Structures")
        if len(components) > 0:
            constraints += [Tight([m >= sum(comp.m for comp in components)])]

        ######### constraints #########

        constraints += [m >= 6 * ureg.kg]

        m_fins = Variable("m_{fins}", 1.2, "kg", "Mass of fins and mounting of fins")
        m_nc = Variable("m_{nc}", 0.5, "kg", "Mass of nose cone")
        m_tube = Variable("m_{tube}", 1.2, "kg")

        #TODO

        return [constraints, components]




