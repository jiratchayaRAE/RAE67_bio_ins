"""
Lab 02 — Robust Reactive Lamp
Student Controller Implementation
"""

from dataclasses import dataclass, field
import math


@dataclass
class Parameters:
    """Dataclass สำหรับเก็บค่าพารามิเตอร์ของ Controller และ Filter"""
    dt: float = 0.05
    alpha: float = 0.2
    beta: float = 0.2
    single_threshold: float = 0.35
    threshold_m: float = 0.35
    t_near: float = 0.30
    t_far: float = 0.40
    enter_threshold_m: float = 0.30
    exit_threshold_m: float = 0.40
    target_distance: float = 0.25
    target_distance_m: float = 0.25
    kp: float = 4.0
    u_min: float = 0.0
    u_max: float = 1.0
    command_min: float = 0.0
    command_max: float = 1.0
    extra_args: dict = field(default_factory=dict)

    def __init__(
        self,
        dt: float = 0.05,
        alpha: float = 0.2,
        beta: float = None,
        single_threshold: float = 0.35,
        threshold_m: float = 0.35,
        t_near: float = 0.30,
        t_far: float = 0.40,
        enter_threshold_m: float = 0.30,
        exit_threshold_m: float = 0.40,
        target_distance: float = 0.25,
        target_distance_m: float = None,
        kp: float = 4.0,
        u_min: float = 0.0,
        u_max: float = 1.0,
        command_min: float = None,
        command_max: float = None,
        **kwargs
    ):
        self.dt = dt
        self.alpha = alpha
        self.beta = beta if beta is not None else alpha
        self.single_threshold = threshold_m if threshold_m != 0.35 else single_threshold
        self.threshold_m = self.single_threshold
        self.t_near = enter_threshold_m if enter_threshold_m != 0.30 else t_near
        self.t_far = exit_threshold_m if exit_threshold_m != 0.40 else t_far
        self.enter_threshold_m = self.t_near
        self.exit_threshold_m = self.t_far
        self.target_distance = target_distance_m if target_distance_m is not None else target_distance
        self.target_distance_m = self.target_distance
        self.kp = kp
        self.u_min = command_min if command_min is not None else u_min
        self.u_max = command_max if command_max is not None else u_max
        self.command_min = self.u_min
        self.command_max = self.u_max
        self.extra_args = kwargs


class StudentController:
    def __init__(self, dt: float = 0.05, params: Parameters = None):
        self.dt = dt
        self.p = params if params is not None else Parameters(dt=dt)
        self.params = self.p
        self.filtered_distance = None
        self.state = "FAR"
        self.current_state = self.state

    def reset(self):
        """Reset state และ history เมื่อเริ่ม trial ใหม่"""
        self.filtered_distance = None
        self.state = "FAR"
        self.current_state = "FAR"

    def safe_command(self) -> float:
        """คืนค่า command ปลอดภัยกรณี invalid sample"""
        return 0.0

    # ==========================================
    # TODO 1: Low-Pass Filter (Exponential Moving Average)
    # ==========================================
    def update_filter(self, raw_distance: float, alpha: float = None) -> float:
        """
        คำนวณ First-Order Low-Pass Filter (EMA)
        y[k] = alpha * x[k] + (1 - alpha) * y[k-1]
        """
        if alpha is None:
            alpha = getattr(self.p, 'beta', getattr(self.p, 'alpha', 0.2))

        if raw_distance is None or not math.isfinite(raw_distance):
            return self.filtered_distance if self.filtered_distance is not None else 0.60

        if self.filtered_distance is None:
            self.filtered_distance = float(raw_distance)
        else:
            self.filtered_distance = (alpha * raw_distance) + ((1.0 - alpha) * self.filtered_distance)

        return self.filtered_distance

    # ==========================================
    # TODO 2: Single Threshold Classifier (C1)
    # ==========================================
    def classify_single_threshold(self, distance: float, threshold: float = None) -> str:
        """
        จำแนก state ด้วย Single Threshold T = 0.35 m
        """
        if threshold is None:
            threshold = getattr(self.p, 'threshold_m', getattr(self.p, 'single_threshold', 0.35))

        if distance is None or not math.isfinite(distance):
            return self.state

        if distance < threshold:
            self.state = "NEAR"
        else:
            self.state = "FAR"

        self.current_state = self.state
        return self.state

    def update_state_single_threshold(self, distance_m: float) -> str:
        """Alias method สำหรับ Adapter ใน lab02.py"""
        return self.classify_single_threshold(distance_m)

    # ==========================================
    # TODO 3: Hysteresis Threshold Classifier (C2)
    # ==========================================
    def classify_hysteresis(self, distance: float, t_near: float = None, t_far: float = None) -> str:
        """
        จำแนก state ด้วย Hysteresis Threshold
        """
        if t_near is None:
            t_near = getattr(self.p, 'enter_threshold_m', getattr(self.p, 't_near', 0.30))
        if t_far is None:
            t_far = getattr(self.p, 'exit_threshold_m', getattr(self.p, 't_far', 0.40))

        if distance is None or not math.isfinite(distance):
            return self.state

        if distance < t_near:
            self.state = "NEAR"
        elif distance > t_far:
            self.state = "FAR"

        self.current_state = self.state
        return self.state

    def update_state_hysteresis(self, distance_m: float) -> str:
        """Alias method สำหรับ Adapter ใน lab02.py"""
        return self.classify_hysteresis(distance_m)

    # ==========================================
    # TODO 4: Proportional Control with Clamping (C3)
    # ==========================================
    def compute_proportional_command(
        self,
        distance: float,
        target_distance: float = None,
        kp: float = None,
        u_min: float = None,
        u_max: float = None
    ) -> float:
        """
        คำนวณ Proportional Command พร้อม Saturation Clamping
        """
        if target_distance is None:
            target_distance = getattr(self.p, 'target_distance_m', getattr(self.p, 'target_distance', 0.25))
        if kp is None:
            kp = self.p.kp
        if u_min is None:
            u_min = getattr(self.p, 'command_min', getattr(self.p, 'u_min', 0.0))
        if u_max is None:
            u_max = getattr(self.p, 'command_max', getattr(self.p, 'u_max', 1.0))

        if distance is None or not math.isfinite(distance):
            return self.safe_command()

        error = target_distance - distance
        u_raw = kp * error
        u_clamped = max(u_min, min(u_raw, u_max))

        return u_clamped

    def proportional_command(self, distance_m: float) -> float:
        """Alias method สำหรับ Adapter ใน lab02.py"""
        return self.compute_proportional_command(distance_m)
