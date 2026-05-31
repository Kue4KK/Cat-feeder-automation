import time
import requests

SERVER_URL = "http://localhost:5000"

print("==================================================")
print(" 🐈 บอร์ดจำลอง PIC24 (Software Simulator)")
print("==================================================")
print("พิมพ์รหัสแมวเพื่อทดสอบ: TAG_ORANGE_01, TAG_BLACK_02, TAG_WHITE_03, TAG_GRAY_04")
print("--------------------------------------------------")

while True:
    try:
        input_tag = input("\n⌨️ [จำลอง] นำ Tag ID มาทาบ (พิมพ์รหัสแล้ว Enter): ").strip()
        
        if not input_tag:
            continue
            
        response = requests.get(f"{SERVER_URL}/api/check-tag", params={"tag_id": input_tag})
        result = response.json()
        
        if result.get("access") == "YES":
            print("🟢 [PIC24] Server อนุมัติสิทธิ์!")
            print("   └─ [SERVO ประตู] -> เปิดให้แมวเดินเข้าซุ้ม")
            print("   └─ [MOTOR อาหาร] -> จ่ายอาหารลงจาน (อาหารเต็ม 100%)")
            print("   └─ [SERVO ประตู] -> ปิดประตูขังแมวไว้ทันที")
            
            current_food = 100
            print("\n--------------------------------------------------")
            print("⚠️ [SYSTEM LOCK] แมวถูกขังอยู่ข้างใน จานอาหารเต็ม 100%")
            print("พิมพ์เลขปริมาณอาหารที่ลดลงเพื่อจำลองการกิน (เช่น 70 -> 30 -> 0)")
            print("--------------------------------------------------")
            
            while current_food > 0:
                user_input = input(f" ระบุอาหารที่เหลืออยู่ (ตอนนี้ {current_food}%): ").strip()
                if not user_input:
                    continue
                try:
                    next_food = int(user_input)
                    if next_food < 0 or next_food > current_food:
                        print("❌ ค่าไม่ถูกต้อง! อาหารต้องลดลงเรื่อยๆ และไม่ต่ำกว่า 0")
                        continue
                    
                    current_food = next_food
                    requests.post(f"{SERVER_URL}/api/update-food", json={"food_level": current_food})
                    
                    if current_food > 0:
                        print(f" [STATUS] อาหารเหลือ {current_food}%... ประตูยังคง 'ล็อคแน่น'")
                except ValueError:
                    print("❌ กรุณากรอกเป็นตัวเลขเท่านั้นครับ")

            print("\n✨ [FOOD IS EMPTY] อาหารหมดจานแล้ว!")
            print("   └─  [SERVO ประตู] -> เปิดประตูให้แมวเดินออกได้")
            time.sleep(2)
            print("   └─  [SERVO ประตู] -> ปิดประตูกลับสู่สภาวะปกติ")
            
            requests.post(f"{SERVER_URL}/api/feed-success", json={"tag_id": input_tag})
            print("🔒 [PIC24] จบกระบวนการเรียบร้อย!\n")
            print("==================================================")
            print("🔄 บอร์ดสแตนด์บาย รอรับแมวตัวต่อไป...")
            
        else:
            print(f"❌ [PIC24] ปฏิเสธสิทธิ์! เหตุผล: {result.get('reason')}\n")
            
    except requests.exceptions.ConnectionError:
        print("❌ [PIC24] ไม่สามารถเชื่อมต่อกับ Server ได้ (คุณลืมเปิด app.py หรือเปล่า?)")
        time.sleep(2)
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")
        time.sleep(2)