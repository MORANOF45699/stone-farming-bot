"""
stone_main.py - บอทขุดหินอัตโนมัติ (FiveM Stone Farming Bot)

วิธีใช้:
  1. เอารถไปจอดใกล้จุดขุด แล้วยืนในระยะที่กด L เปิดท้ายรถได้
  2. รัน: python stone_main.py
  3. สลับไปหน้าเกม แล้วกด F10 เพื่อเริ่ม (บอทจะกด G เริ่มออโต้ฟาร์มให้)
  4. กด F10 อีกครั้งเพื่อหยุดชั่วคราว / Esc ในคอนโซลเพื่อปิดโปรแกรม

Flow:
  ออโต้ฟาร์ม (G) → อ่านเลข Stone จาก HUD ทุก 2 วิ
  → เต็ม 100/100 → กด L → เปิดหลังรถ → ลาก Stone → Max → O → ESC → G → วนต่อ
"""

import sys
import time

import keyboard
import mss

sys.stdout.reconfigure(encoding='utf-8')

import config
import stone_input as inp
from stone_detector import full_match_score, is_map_open
from stone_actions import deposit_to_trunk

MAX_DEPOSIT_FAILS = 2  # ฝากพลาดติดกันกี่ครั้งถึงหยุดบอท


def print_banner():
    print("=" * 55)
    print("    ⛏️  FiveM Stone Farming Bot (บอทขุดหิน) ⛏️    ")
    print("=" * 55)
    print("วิธีใช้งาน:")
    print(f"  - กด [ {config.KEY_TOGGLE.upper()} ] เพื่อ เปิด/ปิด บอท")
    print("  - กด [ Esc ] ในคอนโซลนี้เพื่อปิดโปรแกรม")
    print("เงื่อนไข: ต้องยืนใกล้รถ (กด L เปิดท้ายรถได้) ตลอดเวลา")
    print(f"  - Check Interval: {config.CHECK_INTERVAL}s")
    print("=" * 55)


def main():
    print_banner()

    state = {"active": False}

    def toggle():
        state["active"] = not state["active"]
        if state["active"]:
            print("\n[บอท] ▶ เริ่มทำงาน — กด G เริ่มออโต้ฟาร์ม")
            time.sleep(0.3)
            inp.press_g()
        else:
            print("\n[บอท] ⏸ หยุดชั่วคราว")

    keyboard.add_hotkey(config.KEY_TOGGLE, toggle)

    deposit_fails = 0

    with mss.mss() as sct:
        while True:
            if keyboard.is_pressed("esc"):
                print("\n[บอท] ปิดโปรแกรม")
                break

            if not state["active"]:
                time.sleep(0.2)
                continue

            # กันเคส ESC พลาดไปเปิดแผนที่/เมนู → ปิดแล้วฟาร์มต่อ
            if is_map_open(sct):
                print("[บอท] ⚠ เจอแผนที่/เมนูเปิดค้าง → กด ESC ปิด แล้วฟาร์มต่อ")
                inp.press_esc()
                time.sleep(1.0)
                inp.press_g()
                time.sleep(1.5)
                continue

            score, width = full_match_score(sct)
            full = score >= config.FULL_MATCH_THRESHOLD and width >= config.FULL_TEXT_MIN_WIDTH
            print(f"[บอท] score={score:.2f} w={width} {'🔴 เต็ม!' if full else '⏳ ฟาร์มอยู่...'}")

            if full:
                print(f"\n===== Stone เต็ม 100/100 → รอ {config.FULL_DETECTED_DELAY} วิ ก่อนเริ่มฝาก =====")
                time.sleep(config.FULL_DETECTED_DELAY)
                ok = deposit_to_trunk(sct)
                if ok:
                    deposit_fails = 0
                    print("===== ฝากเสร็จ กลับไปฟาร์มต่อ =====\n")
                else:
                    deposit_fails += 1
                    print(f"[บอท] ⚠ ฝากไม่สำเร็จ ({deposit_fails}/{MAX_DEPOSIT_FAILS})")
                    if deposit_fails >= MAX_DEPOSIT_FAILS:
                        print("[บอท] ✗ ฝากพลาดติดกันหลายครั้ง — หยุดบอท (กด F10 เริ่มใหม่)")
                        state["active"] = False
                        deposit_fails = 0
                time.sleep(1.0)

            time.sleep(config.CHECK_INTERVAL)


if __name__ == '__main__':
    main()
