# ใบงาน Lab04 (รายงาน 1–2 หน้า)

ชื่อ/รหัส __________________ กลุ่ม ______ วันที่ ______ code version/hash ______

## A. ก่อนรัน (10 นาที)

วาด block diagram แล้วเขียนประโยคเชื่อมแต่ละคู่ S, P/C/B, H, R, phi/stride ให้เห็นว่า state เก็บประวัติอย่างไร

| Comparison | prediction ก่อนรัน | เหตุผลจาก term ในสมการ | ผลจริงหลังรัน |
|---|---|---|---|
| C2 vs C1 | *ทบทวนย้อนหลัง ไม่ใช่ prediction ที่บันทึกก่อนรัน:* production สูงขึ้น น่าจะเพิ่ม AUC และทำให้ rise เร็วขึ้น | `P=k_prod*S` เพิ่ม; upper bound ของ H อาจทำให้ peak แยกกันน้อย | peak_H 1.000000 vs 0.999715; AUC 10.672410 vs 9.999644 H·s; rise 1.05 vs 2.70 s |
| C3 vs C1 | *ทบทวนย้อนหลัง:* clearance ที่ต่ำลงน่าจะทำให้ H สะสมและ recovery ช้าลง | `C=k_clear*H_old` ลดลง | peak_H ทั้งคู่ถูกจำกัดใกล้ 1; AUC 11.389145 vs 9.999644 H·s; recovery 5.10 vs 2.85 s |
| C4 vs C1 | *ทบทวนย้อนหลัง:* ตัด binding แล้วน่าจะเพิ่ม H/AUC และยืด recovery | `B=k_bind*R_old` เป็นศูนย์ | peak_H 1.000000 vs 0.999715; AUC 10.754720 vs 9.999644 H·s; recovery 3.80 vs 2.85 s |
| C0 vs C1 | *ทบทวนย้อนหลัง:* direct path น่าจะตอบสนองทันทีและไม่มี hormone state | C0 ใช้ `R=S`; ไม่มี `H` state | C0 peak_H/AUC_H เป็น N/A; latency 0.05 s เทียบ C1 0.15 s |

ผลที่เห็นอาจถูกจำกัดโดย H upper bound=1: peak ของ C1–C4 จึงเกือบเท่ากัน แม้ AUC, rise, recovery และ upper-clamp fraction ต่างกัน (C2 0.2900, C3 0.2733, C4 0.2583 ของ 600 updates)

## B. เติม code และคำนวณมือ (20 นาที)

1. แยก source equation กับ proposed course model คนละกรอบ
2. เติม receptor ก่อน แล้วทดสอบ H=.2, H_min=.1, H_max=.5
3. เติม step: เก็บ H_old และ R_old ก่อนคำนวณ removal
4. เมื่อ H_old=0,S=1 ให้คำนวณ P,C,B,H_raw,H_new,R_new,phi,stride แล้วทำรอบถัดไป
5. รัน checker เก็บ output หากไม่ผ่านให้บันทึก case และเหตุที่แก้

| input_time_s | time_s | P | C | B | H_raw | H | R | phi |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|10.00|10.05|0.8000|0|0|0.0400|0.0400|0.0400|0.20800|
|10.05|10.10|0.8000|0.0240|0.0080|0.0784|0.0784|0.0784|0.21568|

แถว CSV เป็น post-update state: `input_time_s=10.00` ใช้ S=1 กับ H_old=0 แล้วบันทึกผลที่ `time_s=10.05`; แถวถัดไปใช้ H_old=0.04 แล้วจบที่ 10.10

## C. Controlled comparison (20 นาที)

รัน C0–C4 ใช้ dt,duration,H0,stimulus,mapping เดียวกัน เปิด report.html และกรอกค่าจาก metrics.json ไม่อ่านค่าด้วยสายตาอย่างเดียว

| Condition | peak_H | AUC_H | latency s | rise s | recovery s | upper clamp fraction | phi TV rad |
|---|---|---|---|---|---|---|---|
|C0|N/A|N/A|0.05|0.00|0.05|N/A|0.400000|
|C1|0.999715|9.999644|0.15|2.70|2.85|0.000000|0.399829|
|C2|1.000000|10.672410|0.10|1.05|2.85|0.290000|0.399943|
|C3|1.000000|11.389145|0.15|1.45|5.10|0.273333|0.397890|
|C4|1.000000|10.754720|0.15|1.70|3.80|0.258333|0.399548|

จาก `results/comparison/metrics.json`: C3 ฟื้นช้ากว่า C1 **2.25 s** (5.10−2.85); peak_H ที่บันทึกได้ทั้ง C2/C3 เท่ากับ 1.0 หลัง clamp แต่ AUC (10.672410 vs 11.389145), rise (1.05 vs 1.45 s), recovery และ clamp fraction แยกได้; C0 ไม่มี H state จึงเป็น N/A ไม่ใช่ 0; TV ต่ำกว่าอย่างเดียวไม่พิสูจน์ gait, stability หรือความปลอดภัย

## D. Extreme tests และ handoff (10 นาที)

จาก `results/spike/C1_spike.csv`, spike ใช้ stimulus=1 เพียงหนึ่ง update ที่ input_time_s=10.00 แล้วกลับเป็น 0 ใน update ถัดไป ส่วน `results/fault/C1_fault.csv` ที่ input_time_s=15.00 มี stimulus=NaN, fault=1, H/R=0 และ phi/stride กลับเป็น 0.20 rad/0.055 m; state ที่ 15.05 เป็น 0 และที่ 15.10 เริ่มสะสมกลับเป็น H=0.04. Zero/one เป็น software profile checks เท่านั้น ไม่ใช่ hardware limits หรือ emergency-stop test.

Week03 contract ตรวจได้: R=0 → phi=0.20 rad, stride_half=0.055 m; R=1 → phi=0.40 rad, stride_half=0.065 m. Lab04 ยังไม่ทดสอบการทำงานกับ actuator/หุ่นยนต์จริง, การตอบสนองของ sensor, force/torque, physical stability หรือ independent emergency stop

## E. สรุปส่งงาน (10 นาที)

**กลไกและ provenance:** ใช้ proposed course model ตาม `config.json`, dt=0.05 s และ scheduled stimulus; rate ทั้งสามคำนวณจาก H/R เก่าก่อน Euler update แล้ว clamp H และอ่าน R ใหม่ ผลเป็น simulation ไม่ใช่ผลจาก paper หรือ hardware.

**หลักฐาน:** C3 recovery=5.10 s ช้ากว่า C1 2.25 s; C2/C3 มี peak_H=1.0 แต่ AUC ต่างกัน 0.716735 H·s และ rise ต่างกัน 0.40 s; C0 ไม่มี H (N/A). Fault ที่ input_time_s=15.00 ตั้ง flag และ reset H/R ก่อน command; state 15.05=0 และ 15.10=0.04.

**ข้อจำกัด/ขั้นต่อไป:** ไม่มี sensor/actuator, gait dynamics, force, torque, stability หรือ hardware stop test. Week05 ควรตรวจ command timing และ bounds ผ่าน CPG/kinematic pipeline พร้อมใช้ output directory/config/hash ของแต่ละ run; ห้ามอ้างผลจำลองเป็น physical latency.

Checklist: □ code □ comparison CSV 5 files □ extreme CSV 4 files □ config □ plots □ metrics □ report □ คำสั่งรันซ้ำ
