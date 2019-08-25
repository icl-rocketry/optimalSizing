import gpkit
from gpkit import Model, Variable
from gpkit.constraints.tight import Tight
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

        constraints += [engine.m_prop >= 0.17 * m]

        # launch rail requirements

        launch_accel = Variable("a_{launch}", "m/s^2", "Acceleration off launch rail")

        constraints += [launch_accel <= (engine.F + boosters.F) / m]

        g = Variable("g", 9.81, "m/s^2", "Acceleration due to gravity")
        TW = Variable("T/W", 10, "", "Launch Thrust to weight ratio")
        constraints += [launch_accel >= TW * g]

        constraints += [0.5 * launch_accel * boosters.t_burn ** 2 >= 5 * ureg.m]

        constraints += [boosters.m_prop >= 0.2 * ureg.kg]  # from estimate of propellant mass required
        constraints += [
            boosters.m_prop * boosters.c >= boosters.F * boosters.t_burn]  # from estimate of propellant mass required

        constraints += [m <= 100 * ureg.kg]
        constraints += [m >= 10 * ureg.kg]
        return [components, constraints]
