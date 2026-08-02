import time
class BaseCall:
    def __init__(self, caller: str, callee: str):
        # TODO: сохрани caller и callee как атрибуты self,
        # а также заведи атрибуты connected = False и duration = 0
        self.caller = caller
        self.callee = callee
        self.connected = False
        self.duration = 0
        pass

    def connect(self):
        # TODO: переключи self.connected на True
        self.startTime = time.time() 
        self.connected = True
        pass

    def disconnect(self, duration: int):
        # TODO: сохрани duration в self.duration,
        # и переключи self.connected обратно на False
        self.duration = duration
        self.connected = False
        pass


class OutgoingCall(BaseCall):
    def __init__(self, caller: str, callee: str, cost_per_minute: float):
        # TODO: вызови конструктор родителя (BaseCall) через super(),
        # передав ему caller и callee,
        # а затем сохрани cost_per_minute как собственный атрибут этого класса
        super().__init__(caller, callee)
        self.cost_per_minute = cost_per_minute
        pass

    def calculate_cost(self) -> float:
        # TODO: верни стоимость звонка:
        # (self.duration в секундах / 60) * self.cost_per_minute
        return (self.duration/60) * self.cost_per_minute
        pass


def test_base_call_starts_disconnected():
    call = BaseCall("alice", "bob")
    assert call.connected is False
    assert call.duration == 0


def test_base_call_connect_sets_flag():
    call = BaseCall("alice", "bob")
    call.connect()
    assert call.connected is True


def test_base_call_disconnect_stores_duration():
    call = BaseCall("alice", "bob")
    call.connect()
    call.disconnect(42)
    assert call.connected is False
    assert call.duration == 42


def test_outgoing_call_inherits_base_behavior():
    call = OutgoingCall("alice", "bob", cost_per_minute=2.0)
    assert call.caller == "alice"
    assert call.callee == "bob"
    assert call.connected is False


def test_outgoing_call_calculates_cost():
    call = OutgoingCall("alice", "bob", cost_per_minute=2.0)
    call.connect()
    call.disconnect(120)  # 120 секунд = 2 минуты
    assert call.calculate_cost() == 4.0