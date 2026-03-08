from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import os

import locket
from config import TOKEN_SETS

app = Flask(__name__)
CORS(app)


# Trang chính (để Replit preview không lỗi)
@app.route("/")
def home():
    return "Locket Gold API Running"


# API unlock
@app.route("/api/unlock", methods=["POST"])
def unlock():

    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No data"})

    username = data.get("username")

    if not username:
        return jsonify({"status": "error", "message": "Missing username"})

    try:
        result = asyncio.run(run_unlock(username))
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })


async def run_unlock(username):

    # lấy UID từ username
    uid = await locket.resolve_uid(username)

    if not uid:
        return {
            "status": "error",
            "message": "User not found"
        }

    # check gold trước
    status = await locket.check_status(uid)

    if status and status.get("active"):
        return {
            "status": "already_gold",
            "uid": uid,
            "expires": status.get("expires")
        }

    # thử từng token
    for token in TOKEN_SETS:

        success, msg = await locket.inject_gold(uid, token)

        if success:
            return {
                "status": "success",
                "uid": uid,
                "message": msg
            }

    return {
        "status": "failed",
        "uid": uid
    }


# chạy server (Replit compatible)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)