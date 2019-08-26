import gpkit
from gpkit import Model, Variable
from gpkit.constraints.tight import Tight
from gpkit.constraints.loose import Loose
from gpkit.constraints.bounded import Bounded
from gpkit import ureg

from payload import Payload
from avionics import Avionics
from recovery import Recovery
from engine import Engine, SimpleEngine
from boosters import Boosters
from structures import Structures


class Rocket(Model):

    def setup(self):
        constraints = []
        components = self.components = []

        ####### components #########

        # payload
        payload = self.payload = Payload()

        # avionics
        avionics = self.avionics = Avionics()

        # recovery
        recovery = self.recovery = Recovery()

        # main engine
        engine = self.engine = SimpleEngine()

        # boosters
        boosters = self.boosters = Boosters()

        # structures
        structures = self.structures = Structures()

        components += [payload, avionics, recovery, engine, boosters, structures]

        m = self.m = Variable("m", "kg", "Mass of Rocket")
        constraints += [Tight([m >= sum(comp.m for comp in components)])]

        ########## constraints ######

        # total impulse of main engine
        # main_impulse = Variable("I_t", 20000, "N s", "Total impulse of main engine")

        # constraints += [engine.c * engine.m_prop >= main_impulse]
        pmf = self.pmf = Variable('PMF', 0.20, '', 'Propellant Mass Fraction required')
        constraints += [engine.m_prop >= pmf * m]

        # launch rail requirements

        launch_accel = Variable("a_{launch}", "m/s^2", "Acceleration off launch rail")
        g = Variable("g", 9.81, "m/s^2", "Acceleration due to gravity")
        min_a = Variable("min_a", "m/s^2", "minimum launch acceleration")

        launch_rail_v = Variable("v_{launch}", 30, "m/s", "Velocity off launch rail")
        launch_rail_l = Variable("L_{launch}", 5, "m", "Length of launch rail")

        constraints += [min_a >= launch_rail_v**2/(2*launch_rail_l)]

        constraints += [Tight([launch_accel <= (engine.F + boosters.F - m * g) / m])]

        constraints += [Tight([launch_accel >= min_a])]

        constraints += [0.5 * launch_accel * boosters.t_burn ** 2 >= launch_rail_l]

        constraints += [Loose([boosters.m_prop >= 0.2 * ureg.kg])]  # from estimate of propellant mass required
        constraints += [
            boosters.m_prop * boosters.c >= boosters.F * boosters.t_burn]  # from estimate of propellant mass required

        constraints += [Loose([m <= 100 * ureg.kg, m >= 10 * ureg.kg])]

        TW_main = self.TW_main = Variable("TW_{main, min}", 2, "", "Main engine thrust to take off weight")
        constraints += [Loose([engine.F >= TW_main * m * g])]

        return [components, constraints]
