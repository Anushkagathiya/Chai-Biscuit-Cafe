import os,sqlite3
from datetime import datetime,timezone
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB=os.getenv("CAFE_DB_PATH",os.path.join(BASE,"instance","cafe.db"))
MENU=[
("Coffee","Beverages",20,"coffee.jpg","Classic hot coffee brewed for a smooth, comforting cup."),
("Chai","Beverages",15,"Chai.jpg","Indian masala chai with a warm aromatic finish."),
("Cold Coffee","Beverages",50,"Cold-Coffe.jpeg","Chilled creamy coffee for a refreshing pick-me-up."),
("Biscuit","Snacks",10,"buscuit.jpg","Crispy cafe biscuits, perfect with tea or coffee."),
("Pastry","Desserts",30,"pastreis (1).jpg","Soft, sweet pastry made for a little indulgence."),
("Burger","Meals",70,"burger-8869971_640 (2).jpg","Juicy cafe-style burger with fresh toppings."),
("Pizza","Meals",70,"pizza-6664791_640 (4).jpg","Cheesy personal pizza with a delicious baked crust."),
("French Fries","Snacks",40,"French-Fries.jpeg","Golden crispy fries with a light seasoning."),
("Mocktail","Beverages",60,"Mocktail.jpeg","Bright and refreshing fruit mocktail."),
("Noodles","Meals",80,"Noodles.jpeg","Hot wok-tossed noodles with fresh vegetables."),
("Tea","Beverages",25,"Tea.jpeg","Freshly brewed tea served the classic cafe way.")]
def connect():
 os.makedirs(os.path.dirname(DB),exist_ok=True); c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init_db():
 c=connect()
 c.executescript("CREATE TABLE IF NOT EXISTS menu_items(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE,category TEXT,price REAL,image TEXT,description TEXT,available INTEGER DEFAULT 1,created_at TEXT);CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT,customer_name TEXT,phone TEXT,email TEXT,address TEXT,payment_method TEXT,subtotal REAL,delivery_fee REAL,total REAL,status TEXT DEFAULT 'pending',created_at TEXT);CREATE TABLE IF NOT EXISTS order_items(id INTEGER PRIMARY KEY AUTOINCREMENT,order_id INTEGER,menu_item_id INTEGER,item_name TEXT,unit_price REAL,quantity INTEGER,line_total REAL,FOREIGN KEY(order_id) REFERENCES orders(id),FOREIGN KEY(menu_item_id) REFERENCES menu_items(id));CREATE TABLE IF NOT EXISTS contact_messages(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,email TEXT,phone TEXT,message TEXT,created_at TEXT);")
 if c.execute("SELECT COUNT(*) n FROM menu_items").fetchone()["n"]==0:
  now=datetime.now(timezone.utc).isoformat();c.executemany("INSERT INTO menu_items(name,category,price,image,description,created_at) VALUES(?,?,?,?,?,?)",[(a,b,c,d,e,now) for a,b,c,d,e in MENU])
 c.commit();c.close()
def get_menu_items():
 c=connect();r=[dict(x) for x in c.execute("SELECT id,name,category,price,image,description,available FROM menu_items WHERE available=1 ORDER BY id")];c.close();return r
def create_order(customer_name,phone,email,address,payment_method,items):
 c=connect();clean=[];sub=0
 try:
  for x in items:
   iid=int(x["id"]);q=int(x.get("quantity",0));m=c.execute("SELECT * FROM menu_items WHERE id=? AND available=1",(iid,)).fetchone()
   if not m or not 1<=q<=20: raise ValueError("Invalid cart item or quantity")
   line=m["price"]*q;sub+=line;clean.append({"id":iid,"name":m["name"],"price":m["price"],"quantity":q,"line_total":line})
  delivery=0 if sub>=299 else 30;total=sub+delivery;now=datetime.now(timezone.utc).isoformat()
  cur=c.execute("INSERT INTO orders(customer_name,phone,email,address,payment_method,subtotal,delivery_fee,total,status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",(customer_name,phone,email,address,payment_method,sub,delivery,total,"pending",now));oid=cur.lastrowid
  c.executemany("INSERT INTO order_items(order_id,menu_item_id,item_name,unit_price,quantity,line_total) VALUES(?,?,?,?,?,?)",[(oid,x["id"],x["name"],x["price"],x["quantity"],x["line_total"]) for x in clean]);c.commit()
  return {"order_id":oid,"customer_name":customer_name,"status":"pending","items":clean,"subtotal":sub,"delivery_fee":delivery,"total":total,"payment_method":payment_method,"created_at":now}
 except: c.rollback();raise
 finally:c.close()
def get_orders():
 c=connect();out=[]
 for r in c.execute("SELECT * FROM orders ORDER BY id DESC"):
  d=dict(r);d["items"]=[dict(x) for x in c.execute("SELECT item_name,unit_price,quantity,line_total FROM order_items WHERE order_id=?",(r["id"],))];out.append(d)
 c.close();return out
def update_order_status(i,s):
 c=connect();r=c.execute("UPDATE orders SET status=? WHERE id=?",(s,i));c.commit();c.close();return r.rowcount>0
def create_contact_message(n,e,p,m):
 c=connect();now=datetime.now(timezone.utc).isoformat();r=c.execute("INSERT INTO contact_messages(name,email,phone,message,created_at) VALUES(?,?,?,?,?)",(n,e,p,m,now));c.commit();c.close();return r.lastrowid
