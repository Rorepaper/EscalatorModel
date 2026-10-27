import math


class EscalatorModel:
    def __init__(self, h=6.0, l=12.0, z=1.0, v=0.75, angle=30, h_step=0.2):
        self.v = v
        self.d = 0.4
        self.z = z
        self.H = h
        self.L = l
        self.angle = angle
        self.h_step = h_step

        self.k_stand = 2.0
        self.k_walk = 1.2
        self.m_stand = 120.0
        self.k_dyn = 1.3

        self.N_steps = int(self.H / self.h_step)

        self.M_max = 5000 * self.z * self.L

        self.Q_max = 50

        self.C_theor = (self.v * 3600 * self.k_stand) / self.d

    def calc_k_eff(self, p_walk):
        return p_walk * self.k_walk + (1 - p_walk) * self.k_stand

    def real_capacity(self, p_walk):
        k_eff = self.calc_k_eff(p_walk)
        return (self.v * 3600 * k_eff) / self.d

    def calc_total_load(self, p_walk):
        m_walk = self.m_stand * self.k_dyn
        m_step = (1 - p_walk) * self.m_stand + p_walk * m_walk
        total_load = self.N_steps * m_step
        return total_load

    def get_power_kw(self, total_mass):
        g = 9.81
        eta = 0.8
        power = (total_mass * g * self.v * math.sin(math.radians(self.angle))) / eta
        return round(power / 1000, 2)

    def simulate_queue(self, lam, p_walk, current_queue=0, dt_hours=1 / 3600):
        c_real = self.real_capacity(p_walk)

        if lam > c_real:
            queue_growth = (lam - c_real) * dt_hours
            new_queue = current_queue + queue_growth
        else:
            queue_decrease = min(current_queue, (c_real - lam) * dt_hours)
            new_queue = current_queue - queue_decrease

        return max(0, new_queue)

    def get_effective_p_walk(self, p_walk, queue):
        if self.Q_max > 0:
            reduction = min(1.0, queue / self.Q_max)
            return p_walk * (1 - reduction)
        return p_walk

    def simulate(self, lam, p_walk_input, current_queue=0, dt_hours=1 / 3600):
        queue = self.simulate_queue(lam, p_walk_input, current_queue, dt_hours)
        eff_p_walk = self.get_effective_p_walk(p_walk_input, queue)
        final_capacity = self.real_capacity(eff_p_walk)
        total_load = self.calc_total_load(eff_p_walk)
        overload_warning = total_load > self.M_max

        return {
            'lam': lam,
            'p_walk_input': p_walk_input,
            'eff_p_walk': round(eff_p_walk, 3),
            'real_capacity': round(final_capacity),
            'theor_capacity': round(self.C_theor),
            'total_load_kg': round(total_load, 1),
            'load_percent': round((total_load / self.M_max) * 100, 1),
            'overload': overload_warning,
            'current_queue': round(queue),
            'power_kw': self.get_power_kw(total_load)
        }