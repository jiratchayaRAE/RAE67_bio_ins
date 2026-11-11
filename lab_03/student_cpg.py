"""
Lab 03 — SO(2) CPG & Hexapod Kinematic Gait Simulation
Student Implementation File (student_cpg.py)
"""

import math
from typing import Dict, Tuple, Any, Optional

# Global state สำหรับรองรับการเรียกใช้ระดับฟังก์ชันแบบ standalone
_g_o1 = 0.1
_g_o2 = 0.0


def reset_cpg(o1_init: float = 0.1, o2_init: float = 0.0):
    """Reset global CPG state"""
    global _g_o1, _g_o2
    _g_o1 = o1_init
    _g_o2 = o2_init


def so2_step(
    o1: Optional[float] = None,
    o2: Optional[float] = None,
    alpha: float = 1.10,
    phi: float = 0.20
) -> Tuple[float, float]:
    """
    คำนวณ SO(2) CPG แบบ Simultaneous Update
    """
    global _g_o1, _g_o2
    
    if o1 is None:
        o1 = _g_o1
    if o2 is None:
        o2 = _g_o2

    # Simultaneous Update: เก็บค่าเดิมไว้ใช้พร้อมกันทั้งสองสมการ
    o1_prev = o1
    o2_prev = o2

    # สมการ SO(2) Neural Oscillator (lec5.pptx slide 18)
    a1_next = alpha * (math.cos(phi) * o1_prev + math.sin(phi) * o2_prev)
    a2_next = alpha * (-math.sin(phi) * o1_prev + math.cos(phi) * o2_prev)

    # Output Activation Function (tanh)
    o1_next = math.tanh(a1_next)
    o2_next = math.tanh(a2_next)

    _g_o1 = o1_next
    _g_o2 = o2_next

    return o1_next, o2_next


def decode_tripod(
    o1: float,
    o2: float,
    stride_m: float = 0.055,
    lift_m: float = 0.020
) -> Dict[str, Dict[str, float]]:
    """
    แปลงสัญญาณ CPG (o1, o2) เป็นการเคลื่อนที่ของขาหกขาแบบ Alternating Tripod
    """
    sign_A = 1.0
    sign_B = -1.0

    # Tripod A
    x_A = sign_A * o1 * (stride_m / 2.0)
    lift_A = max(0.0, sign_A * o2 * lift_m)
    contact_A = 1.0 if sign_A * o2 <= 0 else 0.0

    # Tripod B
    x_B = sign_B * o1 * (stride_m / 2.0)
    lift_B = max(0.0, sign_B * o2 * lift_m)
    contact_B = 1.0 if sign_B * o2 <= 0 else 0.0

    legs = {
        'LF': {'x_rel': x_A, 'lift': lift_A, 'contact': contact_A},
        'RM': {'x_rel': x_A, 'lift': lift_A, 'contact': contact_A},
        'LH': {'x_rel': x_A, 'lift': lift_A, 'contact': contact_A},
        'RF': {'x_rel': x_B, 'lift': lift_B, 'contact': contact_B},
        'LM': {'x_rel': x_B, 'lift': lift_B, 'contact': contact_B},
        'RH': {'x_rel': x_B, 'lift': lift_B, 'contact': contact_B},
    }
    return legs


def bounded_modulation(m: float) -> Tuple[float, float]:
    """
    แมปค่าสัญญาณควบคุม m (0.0 ถึง 1.0) ไปยัง phi และ stride พร้อม Clamping
    """
    phi_raw = 0.20 + (0.20 * m)
    stride_raw = 0.055 + (0.010 * m)

    phi_cmd = max(0.10, min(phi_raw, 0.45))
    stride_cmd = max(0.040, min(stride_raw, 0.070))

    return phi_cmd, stride_cmd


class StudentCPG:
    """Class wrapper สำหรับรองรับการใช้งานผ่านสคริปต์จำลอง"""
    def __init__(self, alpha: float = 1.10, phi: float = 0.20, dt: float = 0.05):
        self.alpha = alpha
        self.phi = phi
        self.dt = dt
        self.o1 = 0.1
        self.o2 = 0.0

    def reset(self, o1_init: float = 0.1, o2_init: float = 0.0):
        self.o1 = o1_init
        self.o2 = o2_init

    def so2_step(self, alpha: float = None, phi: float = None) -> Tuple[float, float]:
        if alpha is None:
            alpha = self.alpha
        if phi is None:
            phi = self.phi
        self.o1, self.o2 = so2_step(self.o1, self.o2, alpha=alpha, phi=phi)
        return self.o1, self.o2

    def decode_tripod(self, o1: float = None, o2: float = None, stride_m: float = 0.055, lift_m: float = 0.020):
        if o1 is None:
            o1 = self.o1
        if o2 is None:
            o2 = self.o2
        return decode_tripod(o1, o2, stride_m=stride_m, lift_m=lift_m)

    def bounded_modulation(self, m: float) -> Tuple[float, float]:
        return bounded_modulation(m)