import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
import os
from datetime import datetime
import blockChain

file_path = "blockChainDataBase.json"

if not os.path.exists(file_path):
    b=blockChain.blockchain(gen=True)
    b.create_block()
    print(f"{file_path} has been created.")
else:
    b=blockChain.blockchain()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Initialize database
def init_db():
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            role TEXT NOT NULL,
            user_name TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()
roles=['Student','Class Representative','Teacher','HOD','Principal','Dean','University Representative']
@app.route('/')
def index():
    # return render_template('login.html')
    return render_template('landing.html')

@app.route('/login', methods=['POST','GET'])
def login():
    username = request.args.get('email')
    password = request.args.get('password')
 
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()

    c.execute('SELECT * FROM users WHERE email=?', (username,))
    user = c.fetchone()
    conn.close()
    if not user:
        print("no user")
        return render_template('landing.html', error='Invalid username or password')
    print(user)
    if user[4]!=password:
        print("wrong password")
        return render_template('landing.html', error='Invalid username or password')

    session['firstname'] = user[1]
    session['email'] = user[3]
    session['lastname'] = user[2]
    session['role'] = user[5]
    session['userid'] = user[0]
        
    return redirect('/chat')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        print(data)
        try:
            conn = sqlite3.connect('chat_app.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO users (firstname, lastname, email, password, role)
                VALUES (?, ?, ?, ?, ? )
            ''', (
                data['firstname'], data['lastname'], data['email'], data['password'], 
                 data['role']
            ))
            conn.commit()
            conn.close()
            return redirect(url_for('register'))
        except sqlite3.IntegrityError:
            return "User with this email already exists!", 400
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/chat')
def chat():
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()

    c.execute('SELECT id, user_id, message, role, status, user_name FROM messages')
    all_messages = c.fetchall()
    conn.close()

    messages = {
        'pending': [],
        'approved': [],
        'rejected': []
    }
    approved_msg=[]
    pending_msg=[]
    print(all_messages)
    for message in all_messages:
        message_id, user_id, message_text, role, status,user_name = message
        message_data = {
            'id': message_id,
            'user_id': user_id,
            'message': message_text,
            'role': role,
            "user_name":user_name
        }
        if status =='pending' and role<session['role']:
           pending_msg.append(message_data)
        # if status =='approved':
        #    approved_msg.append(message_data)
    block_msg=b.getAllMessage()
    for message in block_msg:
        if message['index']!=0:
            message_data = {
                'id': message['index'],
                'user_id': message['sender_id'],
                'message': message["message"],
                'role': message['role'],
                "user_name":message['user_name'],
                'time':message['time']
            }
            approved_msg.append(message_data)
    print(pending_msg)
    if session['role']=='6':
        roles=['Student','Class Representative','Teacher','HOD','Principal','Dean','University Representative']
        return render_template('index_reg.html', username=session['firstname']+' '+session['lastname'], role=roles[int(session['role'])],userid=session['userid'],a_message=approved_msg,p_message=pending_msg)
    else:
        roles=['Student','Class Representative','Teacher','HOD','Principal','Dean','University Representative']
        return render_template('index.html', username=session['firstname']+' '+session['lastname'], role=roles[int(session['role'])],userid=session['userid'],a_message=approved_msg,p_message=pending_msg)
@socketio.on('send_message')
def handle_send_message(data):
    print("Received data:",data)
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute('SELECT id, role FROM users WHERE id = ?', (data['userid'],))
    user = c.fetchone()
    print(user)
    formatted_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if user:
        if user[1]!='6':
            c.execute('''
                INSERT INTO messages (user_id, message, role,user_name,time)
                VALUES (?, ?, ?, ?,?)
            ''', (user[0], data['message'], user[1],session['email'],formatted_datetime ))
            conn.commit()
        if user[1]=='6':
            c.execute('''
                INSERT INTO messages (user_id, message, role,user_name,time, status)
                VALUES (?, ?, ?, ?, ?,?)
            ''', (user[0], data['message'], user[1],'University',formatted_datetime,'approved'))
            conn.commit()
            result_block=b.create_block(sender_id=user[0],user_name=session['email'],approver_id=session['userid'],message=data['message'],role=user[1],time=formatted_datetime)
    conn.close()
    print('done')

    return redirect('/chat')
@app.route('/approve_message/<int:message_id>', methods=['POST'])
def approve_message(message_id):
    
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()

    c.execute("UPDATE messages SET status = 'approved' WHERE id = ?", (message_id,))
    conn.commit()

    conn.close()
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute('SELECT * FROM messages WHERE id=?', (message_id,))
    mssg = c.fetchone()
    print(mssg[1])
    result_block=b.create_block(sender_id=mssg[1],user_name=mssg[4],approver_id=session['userid'],message=mssg[2],role=mssg[3],time=mssg[5])
    conn.close()
    return jsonify({"success": result_block})
    # except Exception as e:
    #     return jsonify({"success": False, "error": str(e)})

@app.route('/reject_message/<int:message_id>', methods=['POST'])
def reject_message(message_id):
    try:
        conn = sqlite3.connect('chat_app.db')
        c = conn.cursor()
        c.execute("UPDATE messages SET status = 'rejected' WHERE id = ?", (message_id,))
        conn.commit()

        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@socketio.on('approve_message')
def handle_approve_message(data):
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute('UPDATE messages SET status = "approved" WHERE id = ?', (data['message_id'],))
    conn.commit()
    conn.close()
    c.execute('SELECT * FROM users WHERE id=?', (data['message_id'],))
    mssg = c.fetchone()
    conn.close()
    result_block=b.create_block(sender_id=mssg[1],user_name=mssg[4],approver_id=session['userid'],message=mssg[2],role=mssg[3],time=mssg[5])

    emit('message_approved', data, broadcast=True)

@socketio.on('reject_message')
def handle_reject_message(data):
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute('UPDATE messages SET status = "rejected" WHERE id = ?', (data['message_id'],))
    conn.commit()
    conn.close()
    emit('message_rejected', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
