"""
config.py - ค่าพิกัด/ปุ่ม/เวลา ของ Stone Bot

รองรับทุกจอ 16:9 อัตโนมัติ:
  พิกัดทั้งหมดเก็บเป็น "สัดส่วน" (0.0-1.0) อิงจอ แล้วคูณด้วยขนาดจอจริงตอนรัน
  template (ภาพ) จะถูกย่อ/ขยายตาม SCALE ในตัว detector เอง
  → ใช้ได้กับ 1280x720 / 1920x1080 / 2560x1440 / 3840x2160 โดยไม่ต้องแก้อะไร

ถ้าจอไม่ใช่ 16:9 เป๊ะ หรือพิกัดเพี้ยน → รัน calibrate.py เพื่อบันทึกพิกัดจริง
(calibration.json จะ override ทั้งหมด)
"""

import json
import os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*mss.mss is deprecated.*")

import mss

# ===== ตรวจขนาดจอจริง (primary monitor) =====
with mss.mss() as _sct:
    _mon = _sct.monitors[1]
SCREEN_W = _mon["width"]
SCREEN_H = _mon["height"]
SCREEN_LEFT = _mon["left"]
SCREEN_TOP = _mon["top"]

# สเกลเทียบจออ้างอิง 1080p (ใช้ย่อ/ขยาย template + ค่าที่เป็น px)
SCALE = SCREEN_H / 1080.0


def _pt(fx, fy):
    """สัดส่วน (0-1) → พิกัดจอจริง (px)"""
    return (int(SCREEN_LEFT + fx * SCREEN_W), int(SCREEN_TOP + fy * SCREEN_H))


def _region(fl, ft, fw, fh):
    """สัดส่วน (0-1) → region dict สำหรับ mss.grab"""
    return {
        "left": int(SCREEN_LEFT + fl * SCREEN_W),
        "top": int(SCREEN_TOP + ft * SCREEN_H),
        "width": int(fw * SCREEN_W),
        "height": int(fh * SCREEN_H),
    }


# ===== บริเวณตัวเลข Stone บน HUD (ล่างกลางจอ) =====
# อ้างอิง 1920x1080: left=850 top=970 w=175 h=30
COUNTER_REGION = _region(850 / 1920, 970 / 1080, 175 / 1920, 30 / 1080)

# ===== พิกัดคลิก (สัดส่วนอิง 1920x1080) =====
BTN_OPEN_TRUNK = _pt(1212 / 1920, 752 / 1080)   # ปุ่ม "เปิดหลังรถ"
DROP_POINT = _pt(1440 / 1920, 520 / 1080)        # จุดปล่อยของ ฝั่ง SECONDARY
BTN_MAX = _pt(1102 / 1920, 559 / 1080)           # ปุ่ม Max ใน dialog
BTN_CONFIRM = _pt(920 / 1920, 618 / 1080)        # ปุ่ม O (ยืนยัน)

# ===== บริเวณค้นหาช่อง Stone ใน INVENTORY (ฝั่งซ้าย) =====
# อ้างอิง 1920x1080: left=140 top=270 w=730 h=520
INVENTORY_REGION = _region(140 / 1920, 270 / 1080, 730 / 1920, 520 / 1080)
STONE_TEMPLATE = os.path.join(os.path.dirname(__file__), "stone_template.png")
TEMPLATE_MATCH_THRESHOLD = 0.70
INV_SCROLL_RETRIES = 4       # หาช่อง Stone ไม่เจอ → เลื่อนขึ้นแล้วหาใหม่ได้กี่รอบ

# ===== เกณฑ์ตัดสินว่าเต็ม 100/100 (ต้องผ่านทั้งสองข้อ) =====
FULL_TEMPLATE = os.path.join(os.path.dirname(__file__), "full_template.png")
FULL_MATCH_THRESHOLD = 0.80              # template matching mask "100/100"
FULL_TEXT_MIN_WIDTH = int(59 * SCALE)    # ความกว้างข้อความ px (สเกลตามจอ)

# ===== ตรวจว่าแผนที่/เมนู pause เปิดค้างไหม (กัน ESC พลาดไปเปิดแผนที่) =====
# region ครอบโลโก้ "FiveM" + แถบแท็บ ด้านบนซ้าย (โผล่เฉพาะตอนเมนูเปิด)
# อ้างอิง 1920x1080: left=300 top=115 w=380 h=120
MAP_CHECK_REGION = _region(300 / 1920, 115 / 1080, 380 / 1920, 120 / 1080)
MAP_TEMPLATE = os.path.join(os.path.dirname(__file__), "map_template.png")
MAP_MATCH_THRESHOLD = 0.65

# ===== ตรวจว่าหน้า GARAGE (เมนูรถ) เปิดจริงหลังกด L =====
# region ครอบคำว่า "SYSTEM GARAGE" ด้านบนซ้ายของหน้าต่าง
# อ้างอิง 1920x1080: left=450 top=250 w=330 h=60
GARAGE_CHECK_REGION = _region(450 / 1920, 250 / 1080, 330 / 1920, 60 / 1080)
GARAGE_TEMPLATE = os.path.join(os.path.dirname(__file__), "garage_template.png")
GARAGE_MATCH_THRESHOLD = 0.70
GARAGE_OPEN_RETRIES = 3      # กด L ซ้ำได้กี่ครั้งถ้าเมนูยังไม่เปิด

# ===== เวลา (วินาที) — เมนูเกมเปิดช้า ปรับเพิ่ม/ลดตรงนี้ =====
CHECK_INTERVAL = 2.0        # อ่าน counter ทุกกี่วินาทีระหว่างฟาร์ม
FULL_DETECTED_DELAY = 3.0   # เจอเต็ม 100 แล้วรอกี่วิ ก่อนเริ่มกด L
GARAGE_OPEN_DELAY = 3.0     # รอหน้า GARAGE เปิดหลังกด L
TRUNK_OPEN_DELAY = 3.0      # รอหน้า INVENTORY/SECONDARY เปิดหลังคลิก "เปิดหลังรถ"
DIALOG_OPEN_DELAY = 1.5     # รอ dialog "นำเข้าท้ายรถ" เด้งหลังลากไอเทม
CLICK_DELAY = 0.8           # ดีเลย์ระหว่างคลิกแต่ละจุด (Max → O)
DRAG_DURATION = 0.8         # เวลาลากไอเทม
AFTER_DEPOSIT_DELAY = 2.0   # รอหลังยืนยันฝากของ ก่อนกด ESC
AFTER_CLOSE_DELAY = 1.5     # รอหลังกด ESC ก่อนเช็ค counter / กด G

# ===== ปุ่ม =====
KEY_TOGGLE = "f10"          # เปิด/ปิดบอท


def _load_calibration():
    """โหลด calibration.json ถ้ามี มา override ค่าที่คำนวณจากสัดส่วน"""
    path = os.path.join(os.path.dirname(__file__), "calibration.json")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    g = globals()
    for key in ("BTN_OPEN_TRUNK", "DROP_POINT", "BTN_MAX", "BTN_CONFIRM"):
        if key in data:
            g[key] = tuple(data[key])
    for key in ("COUNTER_REGION", "INVENTORY_REGION"):
        if key in data:
            g[key] = data[key]


_load_calibration()

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"จอ: {SCREEN_W}x{SCREEN_H}  SCALE={SCALE:.3f}")
    print(f"COUNTER_REGION   = {COUNTER_REGION}")
    print(f"INVENTORY_REGION = {INVENTORY_REGION}")
    print(f"BTN_OPEN_TRUNK   = {BTN_OPEN_TRUNK}")
    print(f"DROP_POINT       = {DROP_POINT}")
    print(f"BTN_MAX          = {BTN_MAX}")
    print(f"BTN_CONFIRM      = {BTN_CONFIRM}")
    print(f"FULL_TEXT_MIN_WIDTH = {FULL_TEXT_MIN_WIDTH}")
