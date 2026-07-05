import sys
import json
import sqlite3
import datetime

DB_NAME = "bot.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # Foydalanuvchilar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            fullname TEXT,
            username TEXT,
            date TEXT
        )
    """)
    # Kinolar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            title TEXT,
            description TEXT,
            video_file_id TEXT
        )
    """)
    # Kanallar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    
    # users count
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    
    # movies count
    cursor.execute("SELECT COUNT(*) FROM movies")
    movies_count = cursor.fetchone()[0]
    
    # today users count
    today_start = datetime.datetime.now().strftime("%Y-%m-%d") + " 00:00:00"
    cursor.execute("SELECT COUNT(*) FROM users WHERE date >= ?", (today_start,))
    today_users = cursor.fetchone()[0]
    
    conn.close()
    return {
        "users_count": users_count,
        "movies_count": movies_count,
        "today_users": today_users,
        "total_clicks": users_count # Start bosganlar
    }

def get_movies():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, code, title, description, video_file_id FROM movies ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    movies = []
    for r in rows:
        movies.append({
            "id": r[0],
            "code": r[1],
            "title": r[2],
            "description": r[3],
            "video_file_id": r[4]
        })
    return movies

def add_movie(code, title, description, video_file_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO movies (code, title, description, video_file_id) VALUES (?, ?, ?, ?)",
            (code, title, description, video_file_id)
        )
        conn.commit()
        res = {"success": True, "error": None}
    except sqlite3.IntegrityError as e:
        res = {"success": False, "error": f"Kino kodi allaqachon mavjud ({code})"}
    except Exception as e:
        res = {"success": False, "error": str(e)}
    finally:
        conn.close()
    return res

def delete_movie(code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE code = ?", (code,))
    changes = conn.total_changes
    conn.commit()
    conn.close()
    return {"success": changes > 0}

def get_channels():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, channel_id FROM channels ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    channels = []
    for r in rows:
        channels.append({
            "id": r[0],
            "channel_id": r[1]
        })
    return channels

def add_channel(channel_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO channels (channel_id) VALUES (?)", (channel_id,))
        conn.commit()
        res = {"success": True, "error": None}
    except sqlite3.IntegrityError:
        res = {"success": False, "error": "Ushbu kanal allaqachon qo'shilgan."}
    except Exception as e:
        res = {"success": False, "error": str(e)}
    finally:
        conn.close()
    return res

def delete_channel(channel_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
    changes = conn.total_changes
    conn.commit()
    conn.close()
    return {"success": changes > 0}

def get_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, telegram_id, fullname, username, date FROM users ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    users = []
    for r in rows:
        users.append({
            "id": r[0],
            "telegram_id": r[1],
            "fullname": r[2],
            "username": r[3],
            "date": r[4]
        })
    return users

def add_user(telegram_id, fullname, username):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO users (telegram_id, fullname, username, date) VALUES (?, ?, ?, ?)",
            (telegram_id, fullname, username, now)
        )
        conn.commit()
        res = {"success": True, "error": None}
    except Exception as e:
        res = {"success": False, "error": str(e)}
    finally:
        conn.close()
    return res

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command provided"}))
        return

    cmd = sys.argv[1]
    
    try:
        init_db() # MB mavjudligini kafolatlash
        
        if cmd == "init":
            res = {"status": "ok"}
        elif cmd == "get_stats":
            res = get_stats()
        elif cmd == "get_movies":
            res = get_movies()
        elif cmd == "add_movie":
            if len(sys.argv) < 6:
                res = {"error": "Missing args. Expected: code title desc file_id"}
            else:
                res = add_movie(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        elif cmd == "delete_movie":
            if len(sys.argv) < 3:
                res = {"error": "Missing args. Expected: code"}
            else:
                res = delete_movie(sys.argv[2])
        elif cmd == "get_channels":
            res = get_channels()
        elif cmd == "add_channel":
            if len(sys.argv) < 3:
                res = {"error": "Missing args. Expected: channel_id"}
            else:
                res = add_channel(sys.argv[2])
        elif cmd == "delete_channel":
            if len(sys.argv) < 3:
                res = {"error": "Missing args. Expected: channel_id"}
            else:
                res = delete_channel(sys.argv[2])
        elif cmd == "get_users":
            res = get_users()
        elif cmd == "add_user":
            if len(sys.argv) < 5:
                res = {"error": "Missing args. Expected: id name username"}
            else:
                res = add_user(int(sys.argv[2]), sys.argv[3], sys.argv[4])
        else:
            res = {"error": f"Unknown command: {cmd}"}
            
        print(json.dumps(res))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
