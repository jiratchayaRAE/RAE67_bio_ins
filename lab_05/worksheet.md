# ใบงาน Lab 05 — Prediction, timing, evidence

ฉบับพิมพ์: [Word](Lab05_Student_Worksheet_TH.docx) / [PDF](Lab05_Student_Worksheet_TH.pdf)

ชื่อ/รหัส________________ กลุ่ม________ วันที่________

**ขอบเขต:** main runner เป็น proposed course model ใช้ scheduled stimulus และ kinematic body; contact demo ใช้ synthetic signals ไม่ใช่ ALCS terrain experiment ของ paper

## 1. ก่อนรัน: hypothesis และ architecture (10 นาที)

1. Architecture: `S → controller/AHM → R_used → φ/stride → SO(2) CPG → decoder → kinematic body`. ยังไม่มี independent sensory feedback จาก body กลับเข้า controller; contact ใน runner มาจาก decoder/`o₂` ไม่ใช่ sensor อิสระ.
2. **ทบทวนย้อนหลัง ไม่ใช่ prediction ที่บันทึกก่อนรัน:** เทียบ B1/B2 คาดว่า AHM จะลด `max Δφ/step` และเพิ่ม command latency/recovery เพราะ H สะสมและ decay ช้า; ตรวจด้วยตัวเลขในตารางข้อ 3.
3. B3 ตัด binding term `B=k_bind*R` ออกจาก B2; H ยังมี memory ผ่าน production/clearance Euler state.
4. Provenance: source architecture หนึ่งรายการคือ AHM hormone/receptor pathway ที่อ้างใน `SOURCES.md`; proposed course equation คือ Euler update ของ H จาก P−C−B; expected measurement คือ command latency/φ total variation จาก CSV; วัดไม่ได้คือ stability/พลังงานจริงของ robot เพราะไม่มี rigid-body dynamics, force หรือ power sensor.

## 2. รัน comparison และตรวจเวลา (15 นาที)

รัน comparison ตาม README เปิด report เลือก B2 เลื่อน timeline ไป 10.00/10.05s แล้วเปิด B2_states.csv/B2_intervals.csv เพื่อยืนยัน

| command/input time | state end time | H_start | H_end | R_used | φที่ใช้ | stride_half ที่ใช้ |
|---|---|---|---|---|---|---|
| 10.00 | 10.05 | 0.000000 | 0.040000 | 0.000000 | 0.200000 | 0.055000 |
| 10.05 | 10.10 | 0.040000 | 0.078400 | 0.040000 | 0.208000 | 0.055400 |
| 20.00 | 20.05 | 0.999715 | 0.959727 | 0.999715 | 0.399943 | 0.064997 |

CSV ใช้ `input_time_s` เป็นต้น interval และ state เป็นปลาย interval. B1 ใช้ `S_k` ตรงกับ command ในเวลา 10.00 จึง command latency 0; state ที่บันทึกจาก post-update เริ่มเปลี่ยนที่ 10.05 (state latency 0.05 s). เป็น numerical scheduling ไม่ใช่ sensor/actuator latency.

ใช่: `config.json` ระบุ CPG warmup 10 s ด้วย φ=.20 และ initial oscillator (.10,0) เหมือนกัน แล้ว reset H/R, body origin, foot anchors และ log origin ก่อนเก็บผลทุก condition.

## 3. เปรียบเทียบผลและข้อจำกัด (15 นาที)

เติมจาก metrics และ segment_metrics พร้อมหน่วย ห้ามคัดลอกผล source paper มาใส่เป็นผล run นี้

| condition | TV φ(rad) | maxΔφ/step(rad) | TV stride(m) | cmd latency(s) | cmd recovery(s) | on frequency(Hz) | on distance(m) |
|---|---|---|---|---|---|---|---|
| B0 | 0.000000 | 0.000000 | 0.000000 | N/A | N/A | 0.624877 | 0.778743 |
| B1 | 0.400000 | 0.200000 | 0.020000 | 0.00 | 0.00 | 1.268366 | 1.825152 |
| B2 | 0.399827 | 0.008000 | 0.019991 | 0.15 | 2.85 | 1.202760 | 1.706250 |
| B3 | 0.399534 | 0.008000 | 0.019977 | 0.15 | 3.80 | 1.225791 | 1.727498 |

ผลจาก `metrics.json` และ `segment_metrics.csv`; on distance คำนวณจาก mean speed × 10 s. B0 ไม่มี command latency/recovery เพราะไม่มี step command path.
1. `max Δφ/step` ของ B2 ลดจาก B1 .20 เป็น .008 rad/step, แต่ φ TV เกือบเท่ากัน (.399827 vs .400000) และ B2 latency/recovery สูงกว่า (0.15/2.85 s vs 0/0). จึงสนับสนุนการเปลี่ยนแบบค่อยเป็นค่อยไป แต่ไม่ยืนยัน TV ลดลง.
2. ไม่ได้ยืนยันการไม่ล้มหรือใช้พลังงานน้อยลง; ต้องมี CoM/support polygon, force/torque, power และ physical robot measurement.
3. ไม่เท่ากัน: ช่วง on ค่า φ เฉลี่ย B1=.400000, B2=.375007, B3=.381836 rad; stride_half B1=.065000, B2=.063750, B3=.064092 m. Bounds จำกัดเพียงขอบเขต ไม่บังคับให้ trace/amplitude เท่ากัน.
4. ค่าเฉลี่ย 30 s ผสม pre/on/off และซ่อน transient; แยก segment เพื่ออ่านผล stimulus และ recovery.

## 4. เปลี่ยนหนึ่งปัจจัยและตรวจ fault (20 นาที)

เลือก phi-only หรือ stride-only ตั้ง prediction ก่อนรัน ตรวจ parameter ที่คงที่จาก intervalCSV แล้วเปรียบเทียบ B1/B2 กับ bothmapping

เลือก `phi-only` จาก `results/phi_only`: เปลี่ยนเฉพาะ φ mapping; คง stride_half=.055 m, gains, dt, stimulus, bounds และ initial condition; metric หลักคือ on frequency/speed. **ทบทวนย้อนหลัง:** frequency ควรเปลี่ยน แต่ stride command ต้องคงเดิม.

ใน phi-only B2, stride TV=0 และ on frequency=1.202760 Hz; on speed=.146719 m/s (distance=1.467193 m ใน 10 s). เทียบ `stride_only` B2 ซึ่ง φ TV=0, on frequency=.624877 Hz และ speed=.090167 m/s. เป็นการเปรียบเทียบภายใน deterministic course model ไม่ใช่หลักฐาน causal/robot ทั่วไป.

รัน faultprofile เปิด input15.00 แล้วบันทึก:

| field | B2 value |
|---|---|
| fault at command15.00 | 1 |
| H_used / R_used | 0 / 0 |
| φ / stride ที่ใช้ | 0.20 rad / 0.055 m |
| H state15.05 | 0 |
| H state15.10 | 0.040000 |

Fallback ทำก่อนสร้าง command ใน interval 15.00–15.05; จากนั้นเริ่มสะสม H ใหม่ใน update ถัดไป. นี่เป็น software policy เท่านั้น ไม่ตรวจ actuator, timing จริง, torque, watchdog หรือ independent emergency stop.

## 5. Contact mini-lab (20 นาที)

เปิด contactreport เลือก cases ด้านล่าง เปรียบเทียบ SI, SIF, absoluteerror และ validity

| case | SI ของแต่ละขาโดยทั่วไป | SIF | absoluteerror | สิ่งที่อนุมานไม่ได้ |
|---|---|---|---|---|
| matched | SI=1 ทุกขา | 0 | 0.000000 | synthetic signals เท่านั้น |
| gain-offset | SI=1 ทุกขา | ≈0 | 0.162844 | correlation ไม่แสดงความคลาดเคลื่อนขนาดสัญญาณ |
| mixed-delay | 3 ขา SI=1, 3 ขา SI≈0.000009 | 0.499995 | 0.226007 | synthetic delay ไม่ใช่ gait/contact force |
| all-inverted | SI=−1 ทุกขา | 0 | 0.631375 | sign inversion/error สูงไม่ถูกจับโดย SIF |
| constant | SI=N/A ทุกขา | N/A | 0.000000 | zero variance ทำให้ correlation undefined |

1. Pearson ไม่เปลี่ยนภายใต้ positive gain/offset จึง SI=1 ได้แม้ absolute error ไม่เป็น 0.
2. SIF คือ population SD ของ SI ทั้งหก; เมื่อทุกขามี SI=−1 เท่ากัน SD=0. จาก Eq.(1) ที่ CI=1, release=`1/(1+exp(−0))`=.5.
3. N/A เพราะ variance เป็นศูนย์; ห้ามแทน undefined เป็น SI=0.
4. fault หนึ่ง sample กระทบ 50 rolling windows เพิ่มจาก startup unavailable 49 rows: fault case มี unavailable 99 เทียบ matched 49.
5. paired Pearson เป็น proposed course definition ไม่ใช่การยืนยันสมการ source; demo ไม่ได้คำนวณ Cg/HR/MI_H ต่อ.

## 6. ส่งงานและ exit ticket (10 นาที)

ไฟล์ที่ตรวจใน checkout: `results/comparison`, `results/phi_only`, `results/stride_only`, `results/fault`, `results/contact` พร้อม config/manifest/CSV/metrics ตามที่มี. ช่อง prediction ที่กรอกในฉบับนี้เป็นการทบทวนย้อนหลัง ไม่ใช่หลักฐานว่าได้ preregister ก่อนรัน; ตารางผลอ้างอิง model output เท่านั้น.

Exit — claim ที่รองรับ: ใน course model B2 ลด `max Δφ/step` จาก 0.20 เป็น 0.008 rad/step เทียบ B1 (`metrics.json`). Claim ที่ยังรองรับไม่ได้: B2 ทำให้ robot ใช้พลังงานน้อยลงหรือไม่ล้ม; ต้องเพิ่ม physical robot trials, force/torque/CoM และ power measurement.

**Rubric20 คะแนน:** architecture/provenance4; timing/fault4; reproducibility/data3; quantitativecomparison/one-factor5; interpretation/contact/N/A4 คะแนนมาจากเหตุผลกับหลักฐาน ไม่ได้ให้เต็มเพราะ runner รันผ่านหรือเพราะผล “ดีขึ้น” ตามคาด

**Workshop 25 นาทีในคาบ Week05:** ทำข้อ 1 แบบย่อ 5 นาที, ข้อ 2 10 นาที, ข้อ 3 10 นาที ส่วน one-factor/fault/contact เป็น extended lab หรือการบ้าน ใช้เวลารวม 90 นาทีตามใบงาน ไม่รวมเวลาติดตั้ง Python
