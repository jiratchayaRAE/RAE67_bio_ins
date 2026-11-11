# ใบงาน Lab06 — Student

**แบบจำลองทั้งหมดใน runner เป็น proposed course model** โปรแกรมเป็น simulation ไม่ใช่ข้อมูลจาก robot และไม่มี learning

1. **ทบทวนย้อนหลัง ไม่ใช่ prediction ก่อนรัน:** bounce/noise น่าจะเพิ่ม switching ใน C0 ส่วน debounce/hysteresis ของ C1 น่าจะลด switching โดยอาจเพิ่ม latency; invalid/stale/fault ไม่ควรสร้าง positive onset ใหม่. ผลจำลองในตารางข้อ 5 สนับสนุนเรื่อง switching แต่ไม่ได้พิสูจน์ผลกับ hardware.
2. FSM มี priority `fault > near > clear > touch > button > approach > timeout > idle`; `afraid` hold จน clear/fault, `interested/happy` กลับ normal เมื่อ timeout และ normal เข้า sleepy เมื่อ idle.
3. Transition table (None = hold/no transition):

| State | fault | near | clear | touch | button | approach | timeout | idle |
|---|---|---|---|---|---|---|---|---|
| normal | normal | afraid | normal | happy | interested | interested | None | sleepy |
| interested | normal | afraid | normal | happy | interested | interested | normal | None |
| happy | normal | afraid | normal | happy | interested | interested | normal | None |
| afraid | normal | afraid | normal | None | None | None | None | None |
| sleepy | normal | afraid | normal | happy | interested | interested | None | None |

4. `python check_submission.py --contract group` ผ่าน 40 transition pairs; policy ใช้ touch→happy และ button/approach→interested โดยคง safety/recovery. ไม่มี failed-run log เก็บไว้ใน checkout จึงไม่อ้างว่ามี failed case ที่นำไปแก้.
5. ผลจาก `results/completed/metrics.csv` (synthetic paired seeds; all 10 external sources retained) สรุปไว้ในตารางด้านล่าง. Across these three seeds C0 had 19/30 both-onsets and 202 transitions; C1 had 21/30 and 28 transitions. These are synthetic repeats from the model, not independent human/robot trials.
6. ตัวอย่าง `touch_01`, C1 seed 41, `events_C1_r01.csv`: source 3.00 s → recognized/decision 3.06 s → actual apply 3.10 s → motion/RGB onset 3.10 s; both latency 0.10 s. This is simulated command onset, not physical latency.
7. Same-tick near+touch uses near priority and enters afraid; if recognized on different ticks, a temporary earlier touch response can occur. Stale/invalid input produces fault → normal/neutral fallback. Normal inactivity can enter sleepy; button from sleepy enters interested. `discarded_priority` means lower priority lost that tick; `None` means held/no transition; censored means no observed onset before trial end and must not be counted as zero latency.
8. The checked-in `completed` folder contains source input and event logs for seeds 41–43, but no separately identified replay run or replay manifest to compare; equality with an original replay cannot be claimed from these files.
9. Evidence-based summary: C1 reduced transition count in all three pairs (C0 63–72 vs C1 9–10), while both-onset counts were 7/10 for C1 and 6–7/10 for C0. This supports lower switching for this synthetic profile only; it does not prove lower physical latency, actuator safety, or better hardware performance. No personal prediction timestamp is available, so the prediction above is explicitly retrospective.

## ตารางบันทึกของนักศึกษา

| Condition/seed | All external inputs | Both onset | ≤1s both observed | No both onset/status | Max observed latency [s] | State transitions |
|---|---:|---:|---:|---|---:|---:|
| C0/41 | 10 | 7 | 7 | 3/10; conflict priority + fault no-change | 0.24 | 67 |
| C1/41 | 10 | 7 | 7 | 3/10; conflict held + fault no-change | 0.14 | 9 |
| C0/42 | 10 | 6 | 6 | 4/10; conflict/preemption + no-change records | 0.18 | 72 |
| C1/42 | 10 | 7 | 7 | 3/10; conflict held + fault no-change | 0.14 | 10 |
| C0/43 | 10 | 6 | 6 | 4/10; conflict priority + no-change records | 0.04 | 63 |
| C1/43 | 10 | 7 | 7 | 3/10; conflict held + fault no-change | 0.14 | 9 |

| Input ID | Source s | Recognized s | Decision s | Actual apply s | Motion onset s | RGB onset s | Both latency s | Status/reason |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| touch_01 (C1/41) | 3.00 | 3.06 | 3.06 | 3.10 | 3.10 | 3.10 | 0.10 | responded; simulated command onset |

ก่อนส่งตรวจ: ทุก state/movement/input ครบ; bounds/slewไม่ถูกปิด; latencyใช้ออนเซ็ตจริงของmodel; missingไม่แทน0; ระบุ3seedsเป็นsynthetic replications; ส่งpolicy/config/raw/events/metrics; student filesไม่มีเฉลยหรือข้อมูลผู้สอน

Expected set ของ group: ประกาศ input IDs ก่อนรัน ใช้ชุดเดียวกัน C0/C1 แล้วนับ pass/misses จาก source_outcomes ใน metrics.json ตามชุดนั้น ค่า primary_* ที่ runner สร้างใช้ baseline 7 IDs เสมอ; รายงาน all 10 sources พร้อมเหตุผลไว้ครบ ห้ามปรับ subset หลังเห็นผล
