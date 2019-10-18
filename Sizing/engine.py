import gpkit
from gpkit import Model, Variable
from gpkit.constraints.tight import Tight
from gpkit.constraints.loose import Loose
from gpkit.constraints.bounded import Bounded
from gpkit import ureg


class SimpleEngine(Model):

    def setup(self):
        constraints = []
        components = []

        ######## components ###########

        m = self.m = Variable("m", "kg", "Mass of Engine")
        if len(components) > 0:
            constraints += [Tight([m >= sum(comp.m for comp in components)])]

        ########## constraints #########

        m_prop = self.m_prop = Variable("m_{prop}", "kg", "Mass of Propellant")

        m_dry = self.m_dry = Variable("m_{dry}", "kg", "Dry mass of engine")

        # constraints += [m_dry >= 0.7 * m]

        c = self.c = Variable("c", 2100, "m/s", "effective exhaust speed of engine")

        F = self.F = Variable("F", 1000, "N", "Engine thrust")

        OF = self.OF = Variable("OF", 6, "", "Ox to fuel ratio")

        m_ox = self.m_ox = Variable("m_{ox}", "kg", "ox mass")

        m_fuel = self.m_fuel = Variable("m_{fuel}", "kg", "fuel mass")

        constraints += [Tight([m_prop >= m_ox + m_fuel])]

        constraints += [Tight([m_fuel * (OF + 1) >= m_prop])]
        # constraints += [m_fuel * (OF + 1) <= m_prop]

        constraints += [Tight([m_ox * (1 / OF + 1) >= m_prop])]
        # constraints += [m_ox * (1 / OF + 1) <= m_prop]

        constraints += [Tight([m >= m_prop + m_dry])]

        # size the ox tank
        v_ox = self.v_ox = Variable("V_{ox}", "cm^3", "Volume of ox tank")
        l_ox = self.l_ox = Variable("L_{ox}", "m", "Length of ox tank")
        t_wall = self.t = Variable("t_{wall}", "mm", "Wall Thickness of ox tank")
        d = self.d = Variable("d_ox", 18, "cm", "Diameter of ox tank")
        P_ox = self.P = Variable("Tank P", 80, "bar", "Max Ox Tank pressure")
        sigma_max = Variable("\sigma_{max}", 430, "MPa", "Max stress of tank, Al-7075-T6")

        # determine the wall thickness needed
        SF = Variable("SF", 5, "", "Wall thickness safety factor")
        constraints += [t_wall >= SF * P_ox * d / (2 * sigma_max)]

        # determine volume required
        # R = Variable("R", 8.314, "J/mol/K", "Ideal gas constant")
        # T = Variable("T", 350, "K", "Tank temperature ")
        # MM = Variable("MM", 44.1, "g/mol", "Molar mass of Nitrous")
        rho_ox = Variable("rho_{ox}", 490, "kg/m^3", "density of liquid ox")
        constraints += [v_ox >= (m_ox / rho_ox)]

        # determine length of ox tank
        constraints += [l_ox >= 4 * v_ox / (3.14 * d ** 2)]

        m_ox_tank = Variable("m_{ox tank}", "kg", "Mass of ox tank")
        rho_tank = Variable("rho_{ox, tank}", 2700, "kg/m^3", "Density of ox tank (if al)")
        constraints += [m_ox_tank >= rho_tank * (3.14 * d * l_ox * t_wall)]  # the 2 is for safety factor and endcaps

        # grain tank sizing

        m_grain_tank = Variable("m_{grain tank}", "kg", "Mass of combustion chamber")

        rho_fuel = Variable("rho_{wax}", 900, "kg/m^3", "Density of fuel")

        v_fuel = Variable("v_{fuel}", "cm^3", "Volume of fuel")

        constraints += [Tight([v_fuel >= m_fuel/rho_fuel])]

        # estimate port such that the grain area is half the cross section area
        A_grain = Variable("A_{grain}", "cm^2","cross section area of grain")
        constraints += [Tight([A_grain <= 0.5*3.14*(d/2)**2])]

        #estimate length
        l_grain = Variable("L_{grain}", "m", "Length of the grain")
        constraints += [l_grain >= v_fuel/A_grain]

        # estimate mass, assuming the thickness is the same as the ox
        constraints += [Tight([m_grain_tank >= rho_tank * (3.14 * d * l_grain * t_wall)])]

        m_valves = Variable("m_{valves}", 1, "kg", "Mass of valves and plumbing")

        m_nozzle = Variable("m_{nozzle}", 1, "kg", "Mass of nozzle assembly")

        constraints += [Tight([m_dry >= m_ox_tank + m_valves + m_grain_tank + m_nozzle])]

        # impose bounds
        constraints += [Loose([l_ox >= 0.5 * ureg.m, l_ox <= 2 * ureg.m])]
        constraints += [Loose([t_wall >= 1 * ureg.mm, t_wall <= 20 * ureg.mm])]

        return [components, constraints]


class Engine(Model):

    def setup(self):
        constraints = []
        components = self.components = []

        ######### components ##########

        ox_assembly = self.ox_assembly = EngineOxAssembly()
        valve_assembly = self.valve_assembly = EngineValveAssembly()
        fuel_assembly = self.fuel_assembly = EngineFuelAssembly()
        nozzle_assembly = self.nozzle_assembly = EngineNozzleAssembly()

        components += [ox_assembly, valve_assembly, fuel_assembly, nozzle_assembly]

        m = self.m = Variable("m", "kg", "Mass of Engine")
        if len(components) > 0:
            constraints += [Tight([m >= sum(comp.m for comp in components)])]

        ######### constraints #########

        # constraints += [m >= 6 * ureg.kg]

        # define m_prop
        m_prop = self.m_prop = Variable("m_{prop}", "kg", "Propellant Mass")
        constraints += [Tight([m_prop >= ox_assembly.ox.m + fuel_assembly.fuel.m])]

        # define by mass fraction
        # constraints += [m >= m_prop/0.3]

        c = Variable("c", 2000, "m/s", "Main engine effective exhaust speed")

        return [constraints, components]


class EngineOxAssembly(Model):

    def setup(self):
        constraints = []
        components = self.components = []

        ####### components ######

        oxtank = self.oxtank = EngineOxTank()
        ox = self.ox = EngineOx()

        components += [oxtank, ox]

        m = self.m = Variable("m", "kg", "Mass of Engine Tank")
        if len(components) > 0:
            constraints += [Tight([m >= sum(comp.m for comp in components)])]

        #######

        constraints += [m >= 2 * ureg.kg]

        return [components, constraints]


class EngineOxTank(Model):

    def setup(self):
        constraints = []
        components = self.components = []

        ####### components ######

        m = self.m = Variable("m", "kg", "Mass of Engine Tank")
        if len(components) > 0:
            constraints += [Tight([m >= sum(comp.m for comp in components)])]

        #######

        constraints += [m >= 2 * ureg.kg]

        return [components, constraints]


class EngineOx(Model):

    def setup(self):
        constraints = []
        components = self.components = []

        ####### components ######

        m = self.m = Variable("m", "kg", "Mass of Engine Tank")
        if len(components) > 0:
            constraints += [Tight([m >= sum(comp.m for comp in components)])]

        #######

        constraints += [m >= 2 * ureg.kg]

        return [components, constraints]


class EngineValveAssembly(Model):

    def setup(self):
        constraints = []
        components = self.components = []

        ####### components ######

        m = self.m = Variable("m", "kg", "Mass of Engine Tank")
        if len(components) > 0:
            constraints += [Tight([m >= sum(comp.m for comp in components)])]

        #######

        constraints += [m >= 2 * ureg.kg]

        return [components, constraints]


class EngineFuelAssembly(Model):

    def setup(self):
        constraints = []
        components = self.components = []

        ####### components ######

        fuel = self.fuel = EngineFuel()
        enclosure = self.enclosure = EngineFuelEnclosure()

        components += [fuel, enclosure]

        m = self.m = Variable("m", "kg", "Mass of Engine Tank")
        if len(components) > 0:
            constraints += [Tight([m >= sum(comp.m for comp in components)])]

        #######

        constraints += [m >= 2 * ureg.kg]

        return [components, constraints]


class EngineFuel(Model):

    def setup(self):
        constraints = []
        components = self.components = []

        ####### components ######

        m = self.m = Variable("m", "kg", "Mass of Engine Tank")
        if len(components) > 0:
            constraints += [Tight([m >= sum(comp.m for comp in components)])]

        #######

        constraints += [m >= 2 * ureg.kg]

        return [components, constraints]


class EngineFuelEnclosure(Model):

    def setup(self):
        constraints = []
        components = self.components = []

        ####### components ######

        m = self.m = Variable("m", "kg", "Mass of Engine Tank")
        if len(components) > 0:
            constraints += [Tight([m >= sum(comp.m for comp in components)])]

        #######

        constraints += [m >= 2 * ureg.kg]

        return [components, constraints]


class EngineNozzleAssembly(Model):

    def setup(self):
        constraints = []
        components = self.components = []

        ####### components ######

        m = self.m = Variable("m", "kg", "Mass of Engine Tank")
        if len(components) > 0:
            constraints += [Tight([m >= sum(comp.m for comp in components)])]

        #######

        constraints += [m >= 2 * ureg.kg]

        return [components, constraints]
