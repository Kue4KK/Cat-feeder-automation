from flask import Flask, jsonify, request, render_template
from datetime import datetime

app = Flask(__name__)

# ฐานข้อมูลแมว 4 ตัวตามที่คุณระบุไว้
cats_db = {
    "TAG_ORANGE_01": {"name": "เจ้าส้ม", "status": "ยังไม่ได้กิน", "last_fed": "-"},
    "TAG_BLACK_02":  {"name": "เจ้าดำ", "status": "ยังไม่ได้กิน", "last_fed": "-"},
    "TAG_WHITE_03":  {"name": "เจ้าขาว", "status": "ยังไม่ได้กิน", "last_fed": "-"},
    "TAG_GRAY_04":   {"name": "เจ้าเทา", "status": "ยังไม่ได้กิน", "last_fed": "-"},
}

system_log = "ระบบพร้อมทำงาน รอการทาบ Tag..."
current_active_cat = "-"
food_level = 0  

@app.route('/')
def index():
    # ดึงไฟล์จาก templates/index.html มาแสดงผลโดยตรง
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "cats": cats_db,
        "system_log": system_log,
        "current_active_cat": current_active_cat,
        "food_level": food_level  
    })

@app.route('/api/check-tag', methods=['GET'])
def check_tag():
    global system_log, current_active_cat, food_level
    tag_id = request.args.get('tag_id')
    
    if tag_id not in cats_db:
        system_log = f"❌ ปฏิเสธ: พบ Tag แปลกปลอม ({tag_id})"
        return jsonify({"access": "NO", "reason": "Unknown Tag"})
    
    cat = cats_db[tag_id]
    
    if cat["status"] == "กินแล้ว":
        system_log = f"❌ ปฏิเสธ: {cat['name']} กินไปแล้ว ห้ามเข้าซ้ำ!"
        return jsonify({"access": "NO", "reason": "Already Fed"})
    
    system_log = f"🟢 อนุมัติ: {cat['name']} เข้าเครื่อง จ่ายอาหารลงจานแล้ว (ขังรอจนกว่าจะกินหมด)"
    current_active_cat = cat["name"]
    food_level = 100  
    return jsonify({"access": "YES", "reason": "Access Granted"})

@app.route('/api/update-food', methods=['POST'])
def update_food():
    global food_level, system_log
    data = request.get_json() or {}
    food_level = int(data.get('food_level', 0))
    if food_level > 0:
        system_log = f"🥣 {current_active_cat} กำลังกินอาหาร... เหลือในจาน {food_level}% (ประตูยังล็อคอยู่)"
    return jsonify({"status": "updated"})

@app.route('/api/feed-success', methods=['GET', 'POST']) # 💡 แก้ตรงนี้ เพิ่ม 'GET'
def feed_success():
    global system_log, current_active_cat, food_level
    
    # ให้รองรับทั้งการพิมพ์บนเว็บ (GET) และรับจากบอร์ดจำลอง (POST)
    if request.method == 'GET':
        tag_id = request.args.get('tag_id')
    else:
        data = request.get_json() or {}
        tag_id = data.get('tag_id')
    
    if tag_id in cats_db:
        now = datetime.now().strftime("%H:%M:%S")
        cats_db[tag_id]["status"] = "กินแล้ว"
        cats_db[tag_id]["last_fed"] = now
        system_log = f"🔒 อาหารหมดจานแล้ว! เปิดประตูให้ {cats_db[tag_id]['name']} ออก"
        current_active_cat = "-"
        food_level = 0
        return jsonify({"result": "success"})
    
    return jsonify({"result": "fail"}), 400

@app.route('/api/reset', methods=['POST'])
def reset_system():
    global system_log, current_active_cat, food_level
    for tag in cats_db:
        cats_db[tag]["status"] = "ยังไม่ได้กิน"
        cats_db[tag]["last_fed"] = "-"
    system_log = "🔄 รีเซ็ตระบบเริ่มต้นวันใหม่เรียบร้อย"
    current_active_cat = "-"
    food_level = 0
    return jsonify({"result": "reset done"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)