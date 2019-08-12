#create basic components useful for creating a gpkit model

from gpkit import Model, Variable
from gpkit.constraints.tight import Tight

class Motor(Model):

    def setup(self):
        constraints = []

        # define masses
        self.m_dry = Variable("m_{dry}", "kg", "Dry Mass of Motor")
        self.m_propellant = Variable("m_{prop}", "kg", "Propellant Mass of Motor")
        self.m = Variable("m", "kg", "Total mass of motor")

        constraints += [self.m >= self.m_dry + self.m_propellant]

        # define impulse
        self.c = Variable("c", "m/s", "Exhaust speed of motor")
        self.t_burn = Variable("t_{burn}", "s", "Burn Time")
        self.I_t = Variable("I_t", "N s", "Total impulse of motor")

        self.F_avg = Variable("T_{avg}", "N", "Average force of motor")

        constraints += [Tight([self.F_avg <= self.m_propellant * self.c / self.t_burn])]
        constraints += [Tight([self.F_avg >= self.m_propellant * self.c / self.t_burn])]

        constraints += [Tight([self.I_t <= self.m_propellant * self.c])]
        constraints += [Tight([self.I_t >= self.m_propellant * self.c])]


        return constraints


class Tube(Model):

    def setup(self):
        constraints = []

        self.m = Variable("m", "kg", "Mass of Tube")

        self.l = Variable("l", "m", "Length of Tube")

        self.C_d = Variable("C_d", 0.2, "", "Drag contribution of Tube")

        return constraints
