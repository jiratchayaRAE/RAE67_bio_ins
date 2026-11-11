"""Lab04: complete the two TODOs. Use only the Python standard library."""
import math

def receptor(h, h_min=0.0, h_max=1.0):
    """Normalize then clamp to [0,1]. Reject nonfinite values or invalid range."""
    if not math.isfinite(h):
        raise ValueError(f"Hormone concentration h must be finite, got {h}")
    if not math.isfinite(h_min) or not math.isfinite(h_max):
        raise ValueError(f"Receptor bounds must be finite, got h_min={h_min}, h_max={h_max}")
    if h_max <= h_min:
        raise ValueError(f"Invalid range: h_max ({h_max}) <= h_min ({h_min})")
    
    r_raw = (h - h_min) / (h_max - h_min)
    return max(0.0, min(r_raw, 1.0))


def step(h, stimulus, dt, prod, clear, bind):
    """Return dict with h,r,raw,p,c,b,fault.

    Invalid stimulus (NaN, infinity, outside [0,1]): reset to h=r=0,
    set raw=p=c=b=0 and fault=1. Valid: use OLD h and receptor(h)
    for all rates; update once, clamp h, read NEW receptor, fault=0.
    dt and rates have already been validated by the runner.
    """
    # 1. ตรวจสอบ Stimulus (Invalid handling)
    if (not math.isfinite(stimulus)) or (stimulus < 0.0) or (stimulus > 1.0):
        return {
            "h": 0.0,
            "r": 0.0,
            "raw": 0.0,
            "p": 0.0,
            "c": 0.0,
            "b": 0.0,
            "fault": 1
        }

    # 2. ใช้ OLD h และ OLD receptor(h) สำหรับคำนวณอัตรา (Rates) ทั้งหมดในสเต็ปนี้
    h_old = h
    r_old = receptor(h_old)

    # คำนวณ Production (p), Clearance (c), และ Binding (b)
    p = prod * stimulus
    c = clear * h_old
    b = bind * r_old

    # 3. สมการ Euler Update (อัปเดตครั้งเดียวโดยไม่เปลี่ยน h กลางสเต็ป)
    h_raw = h_old + dt * (p - c - b)
    h_new = max(0.0, min(h_raw, 1.0))
    r_new = receptor(h_new)

    return {
        "h": h_new,
        "r": r_new,
        "raw": h_raw,
        "p": p,
        "c": c,
        "b": b,
        "fault": 0
    }