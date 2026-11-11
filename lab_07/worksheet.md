# Lab 07 — Student worksheet

ชื่อกลุ่ม: __________ วันที่: __________ policy version/SHA: `489e58f9744281a79b5169fcd34ea5f61b830e85459e3646ab079463d9b95d0f`

> **ขอบเขตหลักฐาน:** ผลด้านล่างมาจาก offline single-process simulation บน virtual clock เท่านั้น ไม่ใช่ ROS/DDS benchmark, physical latency หรือผลจากหุ่นยนต์จริง ข้อมูลทุกชุดเป็น proposed course model

## 1. Architecture, topics, units, QoS

```text
button/touch/distance sensors → interaction guards + FSM/policy
  → bounded/slew-limited semantic pose + RGB
  → servo/RGB adapters → actuators/LEDs
```

ROS deployment ที่ต้องทำต่อ: sensor MCU/adapter → ROS 2 topics → interaction node → servo/RGB adapter; ยังต้องพัฒนาและทดสอบ MCU firmware, micro-ROS Agent และ actuator driver จริง

| Topic | Type | หน่วย/ความหมาย | QoS |
|---|---|---|---|
| `/lamp/input/button` | `std_msgs/msg/Bool` | true/false | RELIABLE, KEEP_LAST depth 10, VOLATILE |
| `/lamp/input/touch` | `std_msgs/msg/Bool` | true/false | RELIABLE, KEEP_LAST depth 10, VOLATILE |
| `/lamp/input/distance` | `std_msgs/msg/Float32` | m | RELIABLE, KEEP_LAST depth 10, VOLATILE |
| `/lamp/interaction` | `std_msgs/msg/String` | event name | RELIABLE, KEEP_LAST depth 10, VOLATILE |
| `/lamp/emotion` | `std_msgs/msg/String` | emotion state | RELIABLE, KEEP_LAST depth 10, VOLATILE |
| `/lamp/servo_command` | `std_msgs/msg/Float32MultiArray` | rad, order `[tilt, extend, nod]` | RELIABLE, KEEP_LAST depth 10, VOLATILE |
| `/lamp/rgb_command` | `std_msgs/msg/ColorRGBA` | normalized `[0,1]`, alpha=1 | RELIABLE, KEEP_LAST depth 10, VOLATILE |

`extend` เป็น semantic joint ชื่อ extend แต่ค่าบน interface ยังเป็น rad ไม่ใช่ linear distance. RGB integer จาก policy ต้องหาร 255 ก่อน publish. ก่อนต่อ actuator ต้อง calibrate zero/direction/linkage และ hard/software limits แยกกัน; model bounds ไม่ใช่ safety certification.

## 2. Hypothesis, protocol และ run provenance

การทบทวนนี้เขียนหลังการรัน จึง **ไม่ใช่หลักฐาน preregistration ก่อนรัน**. เปรียบเทียบ C0 ideal transport กับ C1 jitter+drop profile โดยใช้ policy และ input protocol เดียวกัน; คาดว่า C1 เพิ่ม transport loss/reordering และอาจเพิ่ม misses/command latency เทียบกับ C0.

รัน offline ด้วยคำสั่ง:

```bash
python offline_lab.py --condition all --repeats 3 --output-dir results/worksheet_run
```

ผลอยู่ที่ `results/worksheet_run/`: 6 trials (C0/C1 × seeds 41, 42, 43), dt=0.02 s, duration=22 s, 1101 ticks/trial; C0 ไม่มี transport drop/delay, C1 ใช้ delay choices 0/.02/.04/.06/.10/.14/.18 s, random drop probability .08 และ burst-drop 12.50–12.70 s. Policy SHA-256 ตรงกับ run manifest: `489e58f9744281a79b5169fcd34ea5f61b830e85459e3646ab079463d9b95d0f`. Python ที่ใช้คือ 3.13.15. `manifest.json` บันทึก SHA-256 ของ configs, raw traces, metrics และ source snapshots.

## 3. ผล paired runs

ประกาศ denominator ก่อนสรุป: ใช้ baseline expected IDs ทั้ง 7 (`button_01`, `touch_01`, `approach_01`, `clear_01`, `near_01`, `clear_02`, `button_02`) ซึ่งตรงกับ policy mapping ที่ checker ผ่าน. `pass/7` นับ input ที่มีทั้ง motion และ RGB onset ภายใน 1 s; median/max latency คำนวณเฉพาะ expected IDs ที่มีทั้งคู่. Missing ไม่แทนด้วย 0. `C1 drop/reorder` นับ messages ใน 3303 published ต่อ trial; transitions นับการเปลี่ยน emotion ตลอด 1101 ticks.

| Pair/seed | C0 pass/7 | C1 pass/7 | C0 median/max latency (s) | C1 median/max latency (s) | C1 missing expected ID(s) | C1 dropped / out-of-order | C0/C1 transitions |
|---|---:|---:|---|---|---|---:|---:|
| 1/41 | 7/7 | 6/7 | 0.04 / 0.14 | 0.15 / 0.20 | `clear_02` | 257 / 1413 | 9 / 17 |
| 2/42 | 7/7 | 6/7 | 0.06 / 0.14 | 0.14 / 0.22 | `button_02` | 287 / 1421 | 10 / 36 |
| 3/43 | 7/7 | 7/7 | 0.04 / 0.14 | 0.10 / 0.18 | none | 300 / 1393 | 9 / 17 |

รวม C0 มี expected both-onset 21/21; C1 มี 19/21 โดย miss 2 รายการจาก 21 expected IDs. C1 dropped 844/9909 published messages (8.52%) และมี 4227 out-of-order receipts; state transitions รวม C0=28, C1=70. ผลนี้สอดคล้องกับ hypothesis ว่า transport profile นี้ทำให้ delivery สูญหาย/สลับลำดับและอาจทำให้ onset หายหรือ latency เพิ่ม แต่มีเพียง 3 synthetic paired repeats และ C1 เปลี่ยน jitter กับ drop พร้อมกัน จึงแยกสาเหตุไม่ได้และสรุปทั่วไปไปยัง ROS/DDS หรือ hardware ไม่ได้.

## 4. Faults, missing และ protocol limits

แต่ละ trial มี 3303 publish records (3 input channels × 1101 ticks). C0 รับครบ 3303/3303 ไม่มี drop/reordering. C1 received 3031, 3007, 2991 messages ใน seeds 41, 42, 43 ตามลำดับ; นอกเหนือจาก transport drop ยังมี accepted/out-of-order status ที่บันทึกใน `input_trace.csv`. Fault ticks ใน C0 เท่ากับ 20/1101 ทุก seed; C1 เท่ากับ 54/1101, 81/1101, 56/1101. ตัวเลข fault รวม invalid **หรือ** stale channels จึงไม่ใช่จำนวน message drop.

ทุก trial เก็บ source input 10 IDs. `touch_conflict` เป็น non-response ตาม priority/afraid guard; `invalid_01` และ `stale_01` เป็น fault ที่อาจไม่มี expression onset ใหม่เมื่อ policy อยู่ normal อยู่แล้ว. จึงไม่รวม 3 IDs นี้ใน expected-7 denominator และไม่เรียกการไม่มี onset ว่า miss. ส่วน C1 missing expected IDs ในตารางเป็น censored/no both onset ภายใน observation window ของ trial; ต้องรายงานเป็น missing ไม่ใช่ latency ศูนย์.

`C1` รวม random jitter และ drop/burst-drop จึงบอกผลของ profile รวม แต่ระบุไม่ได้ว่าปัจจัยใดทำให้เกิด miss หรือ transition เพิ่ม; ต้องเพิ่ม delay-only และ drop-only controls เพื่อแยกสาเหตุ. Offline stale probe ใช้ acquisition timestamps ที่ fixture รู้ แต่ ROS `Bool` ไม่มี timestamp บน wire; ใน ROS track ต้องหยุด publisher เพื่อทดสอบ receipt-stale fallback แยกต่างหาก.

## 5. Clock boundary และความหมายของ latency

Offline run ใช้ virtual clock เดียวใน process; `both_latency_s` คือเวลาจาก source input ถึง simulated applied-command onset ที่มีทั้ง motion และ RGB. จึงใช้เปรียบเทียบภายใน offline model ได้ แต่ไม่ใช่ callback/network/physical response latency. บน ROS `Bool`, `String` และ `Float32` ไม่มี Header timestamp หรือ input ID; ห้ามจับคู่ publish/receive ด้วย ordinal หรือ payload ซ้ำโดยเดา. ต้องเก็บ source ID และ monotonic timestamps ใน sidecar, บันทึก host clock offset/error bound และใช้ independent logger/video marker สำหรับ actual apply/physical motion. ถ้า clock uncertainty มากกว่า latency ที่วัด ให้สรุป latency ไม่ได้.

## 6. Proposal และงานที่ยังไม่รัน

`proposal.json` ระบุ AHM หนึ่งตัว, SO(2) CPG, integration path, B1/B2, metrics, ≥3 repeats, controls, clock plan, conditional real-robot plan, safety/calibration และ human scenario 600 s; `check_proposal.py` ผ่านการตรวจความครบถ้วนของ fields เท่านั้น. ยังไม่ได้รัน ROS 2 Jazzy, real robot หรือ human scenario 600 s; ไม่มีข้อมูลพอจะกรอกผลเหล่านั้น และ proposal ไม่ใช่การรับรอง scientific validity, ethics approval หรือ hardware readiness.

**Claim ที่รองรับ:** ใน offline C1 profile พบ 2 missing จาก 21 expected input IDs และ 844/9909 dropped messages; C0 ไม่พบ expected miss และไม่มี transport drop ใน simulation นี้. **Claim ที่ยังรองรับไม่ได้:** ROS/DDS หรือหุ่นยนต์จริงจะมี latency/ความปลอดภัยเท่าใด; ต้องรัน ROS track บน environment ที่เตรียมไว้, calibrate hardware, วัด physical onset ด้วย independent logger และผ่าน safety/ethics approval ก่อน.

Checklist: [x] seven topics/types/units/QoS documented [x] policy checker passes [x] paired offline traces/config/metrics/manifest saved [x] expected IDs and denominator declared for analysis [x] misses retained [x] measurement limitations stated [x] proposal fields validated [ ] ROS 2 run [ ] real-robot calibration/trials [ ] approved 600 s human scenario
