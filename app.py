from flask import Flask, request, make_response, jsonify
import leolib

app = Flask(__name__)
BASE_USER = "http://seatlib.hpu.edu.cn"


@app.route('/api/', methods=["POST"])
@app.route('/api', methods=["POST"])
def get_user_token():
    """
    获取用户TOKEN
    :return:
    """
    username = request.form["username"]
    password = request.form["password"]
    resp = make_response(leolib.User(username, password, BASE_USER).token)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route('/api/user-info', methods=["POST"])
def get_user_info():
    """
    获取用户信息
    :return:
    """
    # username = request.values.get("username")
    # password = request.values.get("password")
    username = request.form["username"]
    password = request.form["password"]
    resp = make_response(jsonify(leolib.User(username, password, BASE_USER).get_user_info()))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers['Access-Control-Allow-Method'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return resp


@app.route('/api/release', methods=["POST"])
def release_seat():
    """
    释放座位
    :return:
    """
    username = request.form["username"]
    password = request.form["password"]
    resp = make_response(leolib.User(username, password, BASE_USER).release_seat())
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route('/api/cancel/<reserve_id>', methods=["POST"])
def cancel_seat(reserve_id):
    """
    取消预约
    :return:
    """
    username = request.form["username"]
    password = request.form["password"]
    try:
        resp = make_response(leolib.User(username, password, BASE_USER).cancel_book(reserve_id))
    except:
        resp = make_response({
            "code": "1",
            "data": None,
            "message": "预约已过期",
            "status": "fail"
        })

    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route('/api/history', methods=["POST"])
def get_history():
    """
    获取用户信息
    :return:
    """
    username = request.form["username"]
    password = request.form["password"]
    resp = make_response(leolib.User(username, password, BASE_USER).get_history())
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route('/api/reserve', methods=["POST"])
def get_reservation():
    """
    获取用户信息
    :return:
    """
    username = request.form["username"]
    password = request.form["password"]
    reserves = []
    res = leolib.User(username, password, BASE_USER).get_history()
    try:
        for reserve in res["data"]["reservations"]:
            if reserve["stat"] == "RESERVE":
                reserves.append(reserve)
        resp = make_response(reserves)
    except:
        resp = make_response({
            "status": "success",
            "data": {
                "reservations": reserves
            }})
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route('/api/lib/<lib_id>', methods=["POST"])
@app.route('/api/lib/', methods=["POST"])
@app.route('/api/lib', methods=["POST"])
def get_lib(lib_id=0):
    """
    获取图书馆信息
    :param lib_id: 不给定 lib_id 时返回所有图书馆信息
    :return:
    """
    username = request.form["username"]
    password = request.form["password"]
    try:
        if not lib_id:
            libs = leolib.User(username, password, BASE_USER).get_room()["data"]["buildings"]
            res = {
                "status": "success",
                "data": {}
            }
            for lib in libs:
                res["data"][lib[1]] = \
                    leolib.User(username, password, BASE_USER).get_lib_status(lib[0], leolib.get_day(0))["data"]
            resp = make_response(res)
        else:
            resp = make_response(leolib.User(username, password, BASE_USER).get_lib_status(lib_id, leolib.get_day(0)))
    except:
        resp = make_response({'status': 'fail', 'code': '10', 'message': '系统维护中', 'data': None})
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route('/api/search/<start_time>/<end_time>/<date>', methods=["POST"])
def search_seat(start_time, end_time, date):
    """
    预约座位
    :param start_time:
    :param end_time:
    :param date:
    :return:
    """
    username = request.form["username"]
    password = request.form["password"]
    lib_id = request.args.get("lib-id", "0")
    room_id = request.args.get("room-id", "0")
    rooms = leolib.User(username, password, BASE_USER).get_room()["data"]["rooms"]
    res = {
        "status": "success",
        "data": {}
    }
    if lib_id == room_id == "0":
        for _room in rooms:
            res["data"][_room[1]] = leolib.User(username, password, BASE_USER).search_seat(leolib.get_time(start_time),
                                                                                           leolib.get_time(end_time),
                                                                                           date, _room[0])["data"][
                "seats"]
    if room_id == "0":
        for _room in rooms:
            if str(_room[2]) == str(lib_id):
                res["data"][_room[1]] = \
                    leolib.User(username, password, BASE_USER).search_seat(leolib.get_time(start_time),
                                                                           leolib.get_time(end_time), date, _room[0])[
                        "data"]["seats"]
                res["lib_id"] = lib_id
    else:
        res["room_id"] = room_id
        for _room in rooms:
            if str(_room[0]) == str(room_id):
                res["data"][_room[1]] = \
                    leolib.User(username, password, BASE_USER).search_seat(leolib.get_time(start_time),
                                                                           leolib.get_time(end_time), date, room_id)[
                        "data"]["seats"]

    resp = make_response(res)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route('/api/book/<seat_id>/<start_time>/<end_time>/<date>', methods=["POST"])
def book(seat_id, start_time, end_time, date):
    """
    预约座位
    :param seat_id:
    :param start_time:
    :param end_time:
    :param date:
    :return:
    """
    username = request.form["username"]
    password = request.form["password"]
    resp = make_response(leolib.User(username, password, BASE_USER).book_seat(seat_id, leolib.get_time(start_time),
                                                                              leolib.get_time(end_time), date))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route('/api/seat-id/<seat_name>', methods=["POST"])
def get_seat_id(seat_name):
    """
    通过座位地址获取seatId
    :param seat_name:
    :return:
    """
    username = request.form["username"]
    password = request.form["password"]
    res = leolib.get_seat_id(leolib.User(username, password, BASE_USER), seat_name)
    resp = make_response({
        "status": "success",
        "seat_id": res
    })
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8090)
