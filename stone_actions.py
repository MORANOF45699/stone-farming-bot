"""
stone_actions.py - ลำดับการฝากหินเข้าท้ายรถ

ขั้นตอน (ตัวละครต้องยืนใกล้รถ):
  1. กด L        → เปิดหน้า GARAGE
  2. คลิก "เปิดหลังรถ" → เปิดหน้า INVENTORY / SECONDARY
  3. หา slot Stone แล้วลากไปฝั่ง SECONDARY
  4. คลิก Max → คลิก O (ยืนยัน)
  5. กด ESC ปิดหน้าต่าง
  6. กด G เริ่มออโต้ฟาร์มต่อ
"""

import time

import config
import stone_input as inp
from stone_detector import (find_stone_slot, is_stone_empty, is_garage_open,
                            template_available, save_debug_screenshot)


def deposit_to_trunk(sct):
    """
    ฝากหินทั้งหมดเข้าท้ายรถ แล้วกลับไปฟาร์ม
    Returns: True ถ้าสำเร็จ
    """
    # Step 1: เปิดหน้า garage + ยืนยันว่าเปิดจริง (กด L ซ้ำถ้ายังไม่ขึ้น)
    check_garage = template_available(config.GARAGE_TEMPLATE)
    if not check_garage:
        print("[ฝาก] (ข้ามการยืนยันหน้า GARAGE — ยังไม่มี garage_template.png)")

    opened = False
    for attempt in range(1, config.GARAGE_OPEN_RETRIES + 1):
        print(f"[ฝาก] กด L เปิดท้ายรถ (ครั้งที่ {attempt})...")
        inp.press_l()
        time.sleep(config.GARAGE_OPEN_DELAY)
        if not check_garage:          # ไม่มี template → เชื่อว่าเปิดแล้ว เดินหน้าต่อ
            opened = True
            break
        if is_garage_open(sct):
            print("[ฝาก] ✓ หน้า GARAGE เปิดแล้ว")
            opened = True
            break
        print("[ฝาก] ⚠ หน้า GARAGE ยังไม่เปิด — ลองกด L ใหม่")

    if not opened:
        save_debug_screenshot(sct, "garage_not_open")
        print("[ฝาก] ✗ เปิดหน้า GARAGE ไม่ได้ — ยกเลิกรอบนี้")
        inp.press_esc()
        return False

    # Step 2: คลิกปุ่ม "เปิดหลังรถ"
    print(f"[ฝาก] คลิก 'เปิดหลังรถ' ที่ {config.BTN_OPEN_TRUNK}")
    inp.click(*config.BTN_OPEN_TRUNK)
    time.sleep(config.TRUNK_OPEN_DELAY)

    # Step 3: หา slot Stone (ถ้าไม่เจอ เลื่อน inventory ขึ้นบนสุดแล้วหาใหม่)
    inv = config.INVENTORY_REGION
    inv_cx = inv["left"] + inv["width"] // 2
    inv_cy = inv["top"] + inv["height"] // 2

    slot = find_stone_slot(sct)
    if slot is None:
        print("[ฝาก] หาช่อง Stone ไม่เจอ → เลื่อน inventory ขึ้นบนสุดแล้วหาใหม่")
        for i in range(1, config.INV_SCROLL_RETRIES + 1):
            inp.scroll_up(notches=5, x=inv_cx, y=inv_cy)
            time.sleep(0.4)
            slot = find_stone_slot(sct)
            if slot is not None:
                print(f"[ฝาก] เจอหลังเลื่อนขึ้น (ครั้งที่ {i})")
                break

    if slot is None:
        save_debug_screenshot(sct, "no_stone_slot")
        print("[ฝาก] ✗ หาช่อง Stone ไม่เจอ (เลื่อนขึ้นแล้วก็ไม่เจอ) — ปิดหน้าต่าง")
        inp.press_esc()
        return False

    print(f"[ฝาก] ลาก Stone {slot} → {config.DROP_POINT}")
    inp.drag(*slot, *config.DROP_POINT, duration=config.DRAG_DURATION)
    time.sleep(config.DIALOG_OPEN_DELAY)

    # Step 4: Max → ยืนยัน O
    print("[ฝาก] คลิก Max...")
    inp.click(*config.BTN_MAX)
    time.sleep(config.CLICK_DELAY)
    print("[ฝาก] คลิกยืนยัน O...")
    inp.click(*config.BTN_CONFIRM)
    time.sleep(config.AFTER_DEPOSIT_DELAY)

    # Step 5: ปิดหน้าต่าง
    print("[ฝาก] กด ESC ปิดหน้าต่าง")
    inp.press_esc()
    time.sleep(config.AFTER_CLOSE_DELAY)

    # ตรวจว่า counter กลับเป็น 0/100 จริง
    if not is_stone_empty(sct):
        save_debug_screenshot(sct, "deposit_not_empty")
        print("[ฝาก] ⚠ counter ยังไม่เป็น 0 — ฝากอาจไม่สำเร็จ")
        return False

    # Step 6: ฟาร์มต่อ
    print("[ฝาก] ✓ ฝากสำเร็จ — กด G ฟาร์มต่อ")
    inp.press_g()
    return True
