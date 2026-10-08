from flask import Flask, jsonify, request, send_from_directory
from backend.database import init_db, get_menu_items, create_order, get_orders, update_order_status, create_contact_message
import os
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
app=Flask(__name__,static_folder=None)
init_db()
PAGES={"":"index.html","menu":"menu.html","checkout":"checkout.html","about":"about.html","contact":"contact.html","admin":"admin.html"}

@app.get("/")
def home(): return send_from_directory(BASE_DIR,"index.html")
@app.get("/<path:path>")
def pages(path):
    if path in PAGES.values() or path in {"style.css","script.js"} or path.startswith("images/"):
        return send_from_directory(BASE_DIR,path)
    return jsonify({"error":"Not found"}),404
@app.get("/api/health")
def health(): return jsonify({"status":"ok","service":"Chai Biscuit Cafe API"})
@app.get("/api/menu")
def menu(): return jsonify(get_menu_items())

@app.post("/api/orders")
def orders_create():
    data=request.get_json(silent=True) or {}
    missing=[x for x in ("customer_name","phone","address","items") if not data.get(x)]
    if missing: return jsonify({"error":"Missing fields: "+", ".join(missing)}),400
    phone=str(data["phone"]).strip()
    if not phone.isdigit() or len(phone)!=10: return jsonify({"error":"Phone number must be exactly 10 digits"}),400
    try:
        order=create_order(str(data["customer_name"]).strip(),phone,str(data.get("email") or "").strip(),
                           str(data["address"]).strip(),str(data.get("payment_method") or "COD"),data["items"])
        return jsonify(order),201
    except ValueError as e: return jsonify({"error":str(e)}),400
    except Exception:
        app.logger.exception("Order creation failed")
        return jsonify({"error":"Unable to place order right now"}),500

@app.post("/api/contact")
def contact():
    data=request.get_json(silent=True) or {}
    for field in ("name","email","message"):
        if not str(data.get(field) or "").strip(): return jsonify({"error":field.title()+" is required"}),400
    try:
        mid=create_contact_message(str(data["name"]).strip(),str(data["email"]).strip(),str(data.get("phone") or "").strip(),str(data["message"]).strip())
        return jsonify({"message":"Thanks! Your message has been received.","id":mid}),201
    except Exception:
        app.logger.exception("Contact failed")
        return jsonify({"error":"Unable to send message right now"}),500

def authorized(): return request.headers.get("X-Admin-Token","")==os.getenv("ADMIN_TOKEN","admin123")
@app.get("/api/admin/orders")
def admin_orders():
    if not authorized(): return jsonify({"error":"Unauthorized"}),401
    return jsonify(get_orders())
@app.patch("/api/admin/orders/<int:order_id>")
def admin_status(order_id):
    if not authorized(): return jsonify({"error":"Unauthorized"}),401
    status=str((request.get_json(silent=True) or {}).get("status") or "").strip().lower()
    if status not in {"pending","confirmed","preparing","out_for_delivery","delivered","cancelled"}: return jsonify({"error":"Invalid status"}),400
    if not update_order_status(order_id,status): return jsonify({"error":"Order not found"}),404
    return jsonify({"message":"Order status updated"})

if __name__=="__main__": app.run(debug=True,host="127.0.0.1",port=int(os.getenv("PORT","5000")))
