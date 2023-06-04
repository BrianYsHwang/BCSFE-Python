from typing import Any
from bcsfe.core import io, game_version


class EquipSlot:
    def __init__(self, cat_id: int):
        self.cat_id = cat_id

    @staticmethod
    def read(stream: io.data.Data) -> "EquipSlot":
        return EquipSlot(stream.read_int())

    def write(self, stream: io.data.Data):
        stream.write_int(self.cat_id)

    def serialize(self) -> int:
        return self.cat_id

    @staticmethod
    def deserialize(data: int) -> "EquipSlot":
        return EquipSlot(data)

    def __repr__(self):
        return f"EquipSlot({self.cat_id})"

    def __str__(self):
        return f"EquipSlot({self.cat_id})"


class EquipSlots:
    def __init__(self, slots: list[EquipSlot]):
        self.slots = slots
        self.name = ""

    @staticmethod
    def read(stream: io.data.Data) -> "EquipSlots":
        length = 10
        slots = [EquipSlot.read(stream) for _ in range(length)]
        return EquipSlots(slots)

    def write(self, stream: io.data.Data):
        for slot in self.slots:
            slot.write(stream)

    def read_name(self, stream: io.data.Data):
        self.name = stream.read_string()

    def write_name(self, stream: io.data.Data):
        stream.write_string(self.name)

    def serialize(self) -> dict[str, Any]:
        return {
            "slots": [slot.serialize() for slot in self.slots],
            "name": self.name,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "EquipSlots":
        slots = EquipSlots([EquipSlot.deserialize(slot) for slot in data["slots"]])
        slots.name = data["name"]
        return slots

    def __repr__(self):
        return f"EquipSlots({self.slots}, {self.name})"

    def __str__(self):
        return self.__repr__()


class LineUps:
    def __init__(self, slots: list[EquipSlots]):
        self.slots = slots
        self.selected_slot = 0
        self.unlocked_slots = 0

    @staticmethod
    def read(stream: io.data.Data, gv: game_version.GameVersion) -> "LineUps":
        if gv < 90700:
            length = 10
        else:
            length = stream.read_byte()
        slots = [EquipSlots.read(stream) for _ in range(length)]
        return LineUps(slots)

    def write(self, stream: io.data.Data, gv: game_version.GameVersion):
        if gv >= 90700:
            stream.write_byte(len(self.slots))
        for slot in self.slots:
            slot.write(stream)

    def read_2(self, stream: io.data.Data, gv: game_version.GameVersion):
        self.selected_slot = stream.read_int()
        if gv < 90700:
            unlocked_slots_l = stream.read_bool_list(10)
            unlocked_slots = sum(unlocked_slots_l)
        else:
            unlocked_slots = stream.read_byte()
        self.unlocked_slots = unlocked_slots

    def write_2(self, stream: io.data.Data, gv: game_version.GameVersion):
        stream.write_int(self.selected_slot)
        if gv < 90700:
            unlocked_slots_l = [False] * 10
            for i in range(self.unlocked_slots):
                unlocked_slots_l[i] = True
            stream.write_bool_list(unlocked_slots_l, write_length=False)
        else:
            stream.write_byte(self.unlocked_slots)

    def read_slot_names(
        self, stream: io.data.Data, game_version: game_version.GameVersion
    ):
        if game_version >= 110600:
            total_slots = stream.read_byte()
        else:
            total_slots = 15
        for i in range(total_slots):
            self.slots[i].read_name(stream)

        self.slot_names_length = total_slots

    def write_slot_names(
        self, stream: io.data.Data, game_version: game_version.GameVersion
    ):
        if game_version >= 110600:
            stream.write_byte(self.slot_names_length)
        for i in range(self.slot_names_length):
            self.slots[i].write_name(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "slots": [slot.serialize() for slot in self.slots],
            "selected_slot": self.selected_slot,
            "unlocked_slots": self.unlocked_slots,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "LineUps":
        line_ups = LineUps([EquipSlots.deserialize(slot) for slot in data["slots"]])
        line_ups.selected_slot = data["selected_slot"]
        line_ups.unlocked_slots = data["unlocked_slots"]
        return line_ups

    def __repr__(self):
        return f"LineUps({self.slots}, {self.selected_slot}, {self.unlocked_slots})"

    def __str__(self):
        return self.__repr__()
