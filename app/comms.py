class SocketHandler:
    def __init__(self, socket_manager):
        self.sio = socket_manager

        self.conn = {}

        self.sio.on("connect", self.on_connect)
        self.sio.on("login", self.on_login)
        self.sio.on("download", self.on_download)
        self.sio.on("disconnect", self.on_disconnect)

    async def on_connect(self, sid, data):
        print("client connected", sid)

    async def on_disconnect(self, sid):
        if self.conn[sid]:
            del self.conn[sid]

    async def on_login(self, sid, data):
        self.conn[sid] = {"id": data["id"], "name": data["name"], "buckets": []}

        print(self.conn)

    async def on_download(self, sid, data):
        if not self.conn[sid]: return

        print(f"{self.conn[sid]['name']} has requested download for {data}")