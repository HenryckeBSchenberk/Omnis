from bson import ObjectId
from numpy import ndarray, ndenumerate, generic, fliplr, rot90, flipud, array, integer, floating, fromiter
from json import loads, dumps
from cv2 import (
    drawMarker,
    rectangle,
    putText,
    FONT_HERSHEY_SIMPLEX,
    LINE_AA
)
from json import JSONEncoder
from src.crud import CRUD
from threading import Event

def convert_to_array(dict_, type_=float):
    return fromiter(dict_.values(), dtype=type_)

def parser(kwargs):
    slots = kwargs["slots"]
    subdivisions = kwargs["subdivisions"]
    kwargs.update({
        "name": kwargs["name"],
        "shape": (convert_to_array(slots["qtd"], int) * convert_to_array(subdivisions["qtd"], int)).tolist(),
        "order": kwargs.get("order", "TLR"),
        "slot_config": {
            "sizes": convert_to_array(slots["size"]).tolist(),
            "borders": convert_to_array(slots["margin"]).tolist(),
            "origin": convert_to_array(kwargs["origin"]).tolist(),
            "counter": convert_to_array(slots["qtd"], int).tolist(),
            "extra": convert_to_array(subdivisions["margin"]).tolist(),
            "scale": float(kwargs.get("scale", 1)),
        },
        "_id": ObjectId(kwargs.get("_id", kwargs['_id']))
    })
    return kwargs

class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, integer):
            return int(obj)
        elif isinstance(obj, floating):
            return float(obj)
        elif isinstance(obj, ndarray):
            return obj.tolist()
        elif isinstance(obj, ObjectId):
            return str(obj)
        else:
            return super(CustomEncoder, self).default(obj)

class Slot:
    """
    @position,
    @origin,
    @sizes,
    @borders,
    @counter=[0, 0],
    @extra=[0, 0],
    @item=None,
    @_id=None,

    Slot is a class that represents a slot in a grid/blister of slots.
    all the attributes except (item, empty, counter and _id) are dimensions in an unit 'x'
    or coordinates in a world of this unit. eg.
    all coordinates are the distance from the origin of the world (0,0)
     at top left corner.

    origin = (20,10), means that the FIRST SLOT start 20mm from the
    left and 10mm from the top.
    position = (0,0), means that THIS SLOT in the first column and first row in the grid.
    sizes = (100,100), means that the slots is 100mm wide and 100mm high
    borders = (10,10), means that the slots has 10mm of border on the
    left and top.
    counter = (2, 1), means that every 2 slots at X axis and 1 slot at Y axis will sum
    extra border.
    extra = (10,0), means that 10mm of extra border will be added to the slots at X axis,
    after counter.
    Example:
        origin = (20,10)
        sizes = (100,100)
        borders = (10,10)
        counter = (2, 1)
        extra = (10,0)

        Slot at postion (0,0):
            start at: (20, 10)
            ends at: (120, 110)
            center at: (70, 60)

        Slot at postion (1,0):
            start at: (130, 10) | x not is 120 because of border X10mm
            ends at: (230, 110) | x not is 220 because of border X10mm
            center at: (180, 60)

        Slot at postion (0,1):
            (20, 110) (120, 210) [ 70. 160.]
            start at: (20, 110) | y not is 100 because of border Y10mm
            ends at: (120, 210) | y not is 200 because of border Y10mm
            center at: (70, 160)

        Slot at postion (1,1):
            (130, 110) (230, 210) [180. 160.]
            start at: (130, 110) | not is (120, 100) because of border at both axis
            ends at: (230, 210) | not is (220, 200) because of border at both axis
            center at: (180, 160)

    """

    def __init__(
        self,
        position,
        origin,
        sizes,
        borders,
        counter=[0, 0],
        extra=[0, 0],
        item=None,
        _id=None,
        **kwargs,
    ):
        self._id = ObjectId(_id)
        self.scale = kwargs.get("scale", 1.0)
        self.sizes = array(sizes)     * self.scale
        self.borders = array(borders) * self.scale
        self.extra = array(extra)     * self.scale
        self.origin = array(origin)
        self.position = array(position)
        self.counter = array(counter)
        self.item = item
        M = array(
            list(
                (p / c) if c > 0 else 0
                for p, c in zip(self.position[::-1], self.counter)
            )
        ).astype(int)

        self.center = array(
            (self.borders * self.position[::-1])
            + (
                self.origin
                + (((self.sizes) * (self.position[::-1] + 1)) - (self.sizes / 2))
            )
            + ((self.extra * M) - (self.borders * M))
        )

        self.start = tuple((self.center[:2] - (self.sizes[:2] / 2)).astype(int))
        self.end = tuple((self.center[:2] + (self.sizes[:2] / 2)).astype(int))
        self.unscaled = Slot(position, origin, sizes, borders, counter, extra, item, _id, **{**kwargs, "scale": 1, "copy": False}) if (self.scale != 1 and kwargs.get('copy', self.scale!=1)) else self
        # (BN * P)+(O + (S / 2)) + int((BE * (P / C)) - (BN * (P / C)))

    def __call__(self):
        return {i: getattr(self, i) for i in vars(self) if i not in ["_id", "unscaled"] }

    def __str__(self) -> str:
        # return f"((item slot) {self.item} at center:{self.center}, position:{self.position[::-1]})"
        return f"{self.item or self.center}"

    def __repr__(self):
        return str(self)

    def __len__(self):
        return bool(self.item)

    def export(self):
        _ = loads(dumps(self.unscaled(), cls=CustomEncoder))
        _["_id"] = self._id
        _["scale"] = self.scale
        return _


class matrix_sorter:
    def __init__(self, matrix):
        self.matrix = matrix
    
    def BLU(m, S=False):
        """
        Matrix will start from bottom-let.
        3  6  9 
        2  5  8
        1  4  7
        """
        return rot90(m, 3)
    
    def BRU(m,S=False):
        """
        Matrix will start from bottom-right.
        9  6  3 
        8  5  2 
        7  4  1 
        """
        return flipud(rot90(m, 3))



    def BRL(m,S=False):
        """
        Matrix will start from bottom-right.
        9  8  7
        6  5  4
        3  2  1
        """
        return rot90(m, 2)
    
    def TLR(m,S=False):
        """
        Matrix will start from top-left.
        1  2  3
        4  5  6
        7  8  9
        """
        return rot90(m, 4)
    
    def TRB(m,S=False):
        """
        Matrix will start from top-right.
        7  4  1
        8  5  2
        9  6  3
        """
        return rot90(m, 1)

    def TRL(m,S=False): return fliplr(m)

    def TLB(m,S=False): return m.transpose()

    def BLR(m,S=False):
        """
        Matrix will start from bottom-left.
        7  8  9
        4  5  6
        1  2  3
        """
        return fliplr(rot90(m, 2))

    def get(tag, matrix):
        return getattr(matrix_sorter, tag[0:3])(matrix)


class Blister:
    """
    Blister is a class that represents a 2D matrix of slots.\n
    It is used to store the data of the blister, and dynamically generate the slots.\n
    It is also used to iterate over the slots.

    blister_example = Blister(shape=(10, 10), slot_config={'origin':[0, 0], 'sizes':[50, 50], 'borders':[15, 0]})

    next(blister_example) -> (0, 0), Slot(position = [0, 0], center = [25., 25.])\n
    next(blister_example) -> (0, 1), Slot(position = [1, 0], center = [90., 25.])

    update_all_items(item): Change all slots item the new item.
    update_item(item, position): Change the slot at position with the new item.
    update_data(data): Change the data of the blister. data must be a 2Dnp array of Slot objects.
    generate_data(shape, **kwargs): Generate the data of the blister. kwargs must be a dict with the slot_config.
    reset_iterator(): Reset the iterator to the first slot. (when iterating over the slots this method is called automatically)
    draw(image): Draw the blister slots on the image.
    roi(image): crop all slots for the given image, and return as another blister (same shape and config) with the items as the respective crop.
    get_slot(position): Return the slot at position.
    blister(): Return 2D np array of Slot objects.
    blister(i,j): Return the slot at position (i,j).
    blister(i,j,v): Change the slot at position (i,j) with the new value.
    export(): Return the data of the blister as a dict with numpy types converted.

    ** Note **

    Slots.position is not same as the position of the slot in the blister.
    Slots.position is the position as a coordinate (X,Y) in the blister.
    blister.data[i,j] is the slot at data[i,j] position (y,x).\n
    [[00,10,20,30],  i=0, j(x)=0,1,2,3 | blister.data[0,2].position = (2,0) or 20\n
     [01,11,21,31],  i=1, j(x)=0,1,2,3 |\n
     [02,12,22,32],  i=2, j(x)=0,1,2,3 |\n
     [03,13,23,33]]  i=3, j(x)=0,1,2,3 |\n
    """

    def __init__(self, unparsed={}, shape=None, name=None, slot_config=None, _id=None, order='TLR', **kwargs) -> None:
        if unparsed:
            self = Blister.__init__(self, **parser(unparsed))
        else:
            self._id = ObjectId(_id)
            self.slot_config = (
                slot_config if not isinstance(slot_config, Slot) else slot_config.export()
            )
            
            self.name = name
            self.shape = tuple(shape)
            self.kwargs = kwargs
            self.empty = Event()
            self.data = self.re_order(self.generate_data(shape, **self.slot_config), order)
            self.reset_iterator()

    def __str__(self) -> str:
        return f"((Blister) shape:{self.shape}, slots:{len(self)})"

    def __repr__(self):
        return str(self)

    def __len__(self):
        return self.data.size

    @staticmethod
    def is_array(array):
        return isinstance(array, (ndarray, list, generic))

    @staticmethod
    def is_slot(slot):
        return isinstance(slot, Slot)

    def update_item(self, item, position):
        self.data[position[0], position[1]].item = item
        self.data[position[0], position[1]].empty = False
        self.reset_iterator()
        return self.data

    def update_all_items(self, item):
        for _, slot in ndenumerate(self.data):
            slot.item = item
            slot.empty = False
        self.reset_iterator()
        return self.data

    def update_data(self, data):
        assert all(
            map(
                lambda x: Blister.is_array(x)
                and all(map(lambda y: Blister.is_slot(y), x)),
                array(data),
            )
        ), "Data must be a ('N'D | N>=2) arrayof Slot objects."
        self.data = data
        self.reset_iterator()
        return self.data

    @staticmethod
    def generate_data(
        shape, origin, sizes, borders, counter=[0, 0], extra=[0, 0], **kwargs
    ):
        return array(
            [
                [
                    Slot(
                        position=[y, x],
                        origin=origin,
                        sizes=sizes,
                        borders=borders,
                        counter=counter,
                        extra=extra,
                        item=kwargs.get("new_item", kwargs.get("item", None)),
                        scale=kwargs.get("scale", 1),
                    )
                    for x in range(shape[0])
                ]
                for y in range(shape[1])
            ]
        )

    def get_slot(self, position):
        return self.data[position[0], position[1]]

    def reset_iterator(self):
        self.iterator = ndenumerate(self.data)
        self.empty.clear()
        # self.iterator = 
        # pass
        # self.iterator = ndenumerate(self.order_matrix)
        # return self.iterator

    def __next__(self):
        # _id = next(self.iterator)
        try:
            if not self.empty.is_set():
                return next(self.iterator)
        except StopIteration:
            self.empty.set()

            #self.data[_id[0], _id[1]]
        # return self.get_slot(next(self.iterator)).center
        # return self.get_slot(next(self.iterator))

    def __call__(self, y=None, x=None, v=None):
        if y is not None and x is not None:
            if v is not None:
                self.update_item(v, [y, x])
            return self.get_slot([y, x])
        else:
            return self.data

    def draw(self, image=None, thickness=1, color=(0, 0, 0), **kwargs):
        for _, slot in ndenumerate(self.data):
            drawMarker(image, tuple((slot.center[:2].astype(int))), (0, 0, 255), thickness=thickness)
            rectangle(image, slot.start, slot.end, color, thickness)
            putText(
                image,
                str(slot.position[:2]),
                tuple(
                    (slot.center[:2].astype(int))
                    + [int((slot.sizes[0] * -1) / 2) + 5, int(slot.sizes[1] / 4) - 5]
                ),
                FONT_HERSHEY_SIMPLEX,
                1.2,
                color,
                thickness,
                lineType=LINE_AA,
            )
        return image

    def roi(self, image, pointer=True):
        """_summary_
        Args:
            image (_type_): Image to be Cropped using edges of every Slot in  blister.
            pointer (bool, optional): If enabled, will return a pointer for this instance, else a copy. Defaults to True.

        Returns:
            Blister: An blister with the same shape and slot_config, but with the items as the respective crop.
        """
        temp = Blister(shape=self.shape, name=self.name, slot_config=self.slot_config)
        for _, slot in ndenumerate(self.data):
            pos = image[slot.start[1] : slot.end[1], slot.start[0] : slot.end[0]]
            if pointer:
                self.update_item(pos, _)
            else:
                temp.update_item(pos, _)
        return temp if not pointer else self

    def transpose(self):
        self.data = self.data.transpose()
        self.reset_iterator()
        return self.data

    def export(self):
        data = {
                    "shape": self.shape,
                    "slot_config": self.slot_config,
                    "name":self.name,
                    "kwargs": self.kwargs,
                }
        data["_id"] = self._id
        return data

    @staticmethod
    def re_order(M, tag='TLR'):
        return matrix_sorter.get(tag, M)

    def __iter__(self):
        return self

