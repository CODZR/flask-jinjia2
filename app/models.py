import dataclasses
from dataclasses import dataclass, field
import datetime
import enum
from typing import List
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import text
from sqlalchemy.ext.associationproxy import association_proxy


db = SQLAlchemy()


class UpdateMixin:
    def update(self, values):
        for k, v in values.items():
            setattr(self, k, v)


class UnitCondition(enum.Enum):
    GOOD = "good"
    SCRAP = "scrap"
    DAMAGED = "damaged"
    FIXED_A = "fixed_a"
    FIXED_B = "fixed_b"
    FIXED_C = "fixed_c"


class PackageUnitStatus(enum.Enum):
    DELIVERING = "Delivering"
    DELIVERED_BUT_UNCHECKED = "Delivered but unchecked"
    COMPLETE_WITH_DELIVERED = "Complete with delivered"
    COMPLETE_WITH_RETURNED = "Complete with returned"
    RETURNING = "Returning"
    RETURNED_BUT_UNCHECKED = "Returned but unchecked"
    LOST = "Lost"
    CONSIDERED_LOST = "Considered lost"


class PackageBoxCondition(enum.Enum):
    GOOD = "good"
    MISSING = "missing"
    DAMAGED = "damaged"


@dataclass
class RawOrderAttachment(db.Model, UpdateMixin):
    business_verified: bool
    finance_verified: bool
    cs_verified: bool

    __tablename__ = "log2_raw_order_attachment"

    order_id = db.Column(db.String, primary_key=True)
    business_verified = db.Column(db.Boolean, nullable=True)
    finance_verified = db.Column(db.Boolean, nullable=True)
    cs_verified = db.Column(db.Boolean, nullable=True)


@dataclass
class RawOrder(db.Model):
    id: str
    created_at: datetime.datetime
    latest_ship_date: datetime.datetime
    latest_delivery_date: datetime.datetime
    shopify_id: int
    email: str
    shipping_phone: str
    shipping_name: str
    shipping_address1: str
    shipping_address2: str
    shipping_company: str
    shipping_city: str
    shipping_state: str
    shipping_zip: str
    shipping_country: str
    order_from: str
    marketplace: str
    business_verification_required: bool
    finance_verification_required: bool
    cs_review_required: bool
    items: List
    attachment: RawOrderAttachment

    __tablename__ = "log2_raw_order"

    id = db.Column(db.String, primary_key=True)
    shopify_id = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime)
    latest_ship_date = db.Column(db.DateTime)
    latest_delivery_date = db.Column(db.DateTime)
    email = db.Column(db.String)
    shipping_phone = db.Column(db.String)
    shipping_name = db.Column(db.String)
    shipping_address1 = db.Column(db.String)
    shipping_address2 = db.Column(db.String)
    shipping_company = db.Column(db.String)
    shipping_city = db.Column(db.String)
    shipping_state = db.Column(db.String)
    shipping_zip = db.Column(db.String)
    shipping_country = db.Column(db.String)
    order_from = db.Column(db.String)
    marketplace = db.Column(db.String)
    business_verification_required = db.Column(db.Boolean)
    finance_verification_required = db.Column(db.Boolean)
    cs_review_required = db.Column(db.Boolean)

    items = db.relationship(
        "RawOrderItem", primaryjoin="RawOrder.id==RawOrderItem.order_id", foreign_keys="RawOrderItem.order_id"
    )
    attachment = db.relationship(
        "RawOrderAttachment",
        primaryjoin="RawOrder.id==RawOrderAttachment.order_id",
        foreign_keys="RawOrderAttachment.order_id",
        uselist=False,
    )


@dataclass
class RawOrderItem(db.Model):
    product_code: str
    quantity: int

    __tablename__ = "log2_raw_order_item"

    order_id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    product_code = db.Column(db.String, primary_key=True)
    quantity = db.Column(db.Integer)


class AssignedRawOrder(db.Model):
    __tablename__ = "log2_assigned_raw_order"

    raw_order_id = db.Column("raw_order_id", db.String, primary_key=True)
    order_id = db.Column("order_id", db.Integer, db.ForeignKey("log2_order.id"), index=True)


@dataclass
class PackageUnitAccessory(db.Model):
    product_code: str
    quantity: int

    __tablename__ = "log2_package_unit_accessory"

    package_unit_id = db.Column(db.Integer, db.ForeignKey("log2_package_unit.id"), primary_key=True)
    product_code = db.Column(db.String(60), db.ForeignKey("log2_product.code"), primary_key=True)

    quantity = db.Column(db.Integer, nullable=False)


@dataclass
class PackageUnit(db.Model, UpdateMixin):
    id: int
    package_id: int
    serial: str
    product_code: str
    status: str
    shipment_damage: bool
    shipment_damage_note: str
    package_box_condition: str
    insurance_cost: float
    checked: bool
    restocked: bool
    if_stylus: bool
    if_powercord: bool
    accessories: List[PackageUnitAccessory]
    item: "Item"

    __tablename__ = "log2_package_unit"

    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey("log2_package.id"), nullable=False)
    serial = db.Column(db.String, db.ForeignKey("log2_item.serial"), nullable=True)
    product_code = db.Column(db.String(60), db.ForeignKey("log2_product.code"), nullable=True)
    status = db.Column(
        db.Enum(PackageUnitStatus),
    )
    shipment_damage = db.Column(db.Boolean, nullable=True)
    shipment_damage_note = db.Column(db.String, nullable=True)
    package_box_condition = db.Column(
        db.Enum(PackageBoxCondition),
        nullable=True,
    )
    insurance_cost = db.Column(db.Float, nullable=True)
    checked = db.Column(db.Boolean, nullable=False, default=False)
    restocked = db.Column(db.Boolean, nullable=False, default=False)
    if_stylus = db.Column(db.Boolean, nullable=True)
    if_powercord = db.Column(db.Boolean, nullable=True)

    accessories = db.relationship("PackageUnitAccessory", lazy=True, cascade="all, delete-orphan")
    item = db.relationship("Item", lazy=True)


@dataclass
class PackageAccessory(db.Model):
    product_code: str
    quantity: int
    status: str

    __tablename__ = "log2_package_accessory"

    package_id = db.Column(db.Integer, db.ForeignKey("log2_package.id"), primary_key=True)
    product_code = db.Column(db.String(60), db.ForeignKey("log2_product.code"), primary_key=True)
    status = db.Column(
        db.Enum(PackageUnitStatus),
        nullable=True,
    )

    quantity = db.Column(db.Integer, nullable=False)


@dataclass
class Package(db.Model, UpdateMixin):
    id: int
    task_id: int
    unit_system: str
    weight: int
    length: int
    width: int
    height: int
    sizes: str
    tracking_number: str
    created_at: datetime.datetime
    delivered_at: datetime.datetime
    scanned_serials: str
    units: List[PackageUnit]
    accessories: List[PackageAccessory]
    pkg_fulfilled_at: datetime.datetime

    class UnitSystem(enum.Enum):
        SI = "SI"
        BS = "BS"

    __tablename__ = "log2_package"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("log2_warehouse_task.id"), nullable=False)
    tracking_number = db.Column(db.String(60), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    delivered_at = db.Column(db.DateTime, nullable=True)
    weight = db.Column(db.Integer, nullable=True)
    length = db.Column(db.Integer, nullable=True)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    sizes = db.Column(db.JSON, nullable=True)
    unit_system = db.Column(
        db.Enum(UnitSystem),
        nullable=True,
    )
    scanned_serials = db.Column(db.String(200), nullable=True)
    pkg_fulfilled_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())

    units = db.relationship("PackageUnit", lazy=True, cascade="all, delete-orphan")
    accessories = db.relationship("PackageAccessory", lazy=True, cascade="all, delete-orphan")


@dataclass
class WarehouseTaskProduct(db.Model):
    id: int
    product_code: str
    sku: str
    quantity: int
    serial_note: str
    condition: str

    __tablename__ = "log2_warehouse_task_product"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("log2_warehouse_task.id"), nullable=False)
    product_code = db.Column(db.String(60), db.ForeignKey("log2_product.code"), nullable=False)
    sku = db.Column(db.String(60), db.ForeignKey("log2_sku.sku"), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    serial_note = db.Column(db.JSON, nullable=True)
    condition = db.Column(
        db.Enum(UnitCondition),
        nullable=True,
    )

    product = db.relationship("Product", lazy=True)


@dataclass
class LightningOrder(db.Model):
    outbound_order_no: int
    data: dict

    __tablename__ = "log2_lightning_order"

    outbound_order_no = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON, nullable=True)


@dataclass
class TaskFile(db.Model):
    file_id: int
    file_name: str

    __tablename__ = "log2_task_file"

    file_id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("log2_warehouse_task.id"), nullable=False, index=True)


@dataclass
class WarehouseTask(db.Model, UpdateMixin):
    id: int
    task_type: str
    order_id: int
    source_id: int
    target_id: int
    new_address: str
    note: str
    products: List[WarehouseTaskProduct]
    created_at: datetime.datetime

    carrier: str
    transport_mode: str
    delivery_cost: float
    liftgate_cost: float
    limited_cost: float
    residential_cost: float
    inside_cost: float
    insure_cost: float
    return_reason: str
    return_details: str
    on_hold: bool
    tracking_number_note: str
    ref_task_id: int
    fulfilled_at: datetime.datetime
    onhold_modified_at: datetime.datetime
    email_sended: bool
    scheduled_date: datetime.datetime

    packages: List[Package]
    lightning_order: LightningOrder
    files: List[TaskFile]

    __tablename__ = "log2_warehouse_task"

    class TaskType(enum.Enum):
        FULFILLMENT = "fulfillment"
        REPLACE = "replace"
        RETURN = "return"
        RETURN_TO_REPAIR = "return to repair"
        MOVE = "move"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    task_type = db.Column(db.Enum(TaskType), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("log2_order.id"), nullable=True)
    source_id = db.Column(db.Integer, db.ForeignKey("log2_warehouse.id"), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey("log2_warehouse.id"), nullable=False)
    new_address = db.Column(db.Text(), nullable=True)
    note = db.Column(db.Text(), nullable=True)

    carrier = db.Column(db.String(40), nullable=True)
    transport_mode = db.Column(db.String(40), nullable=True)
    delivery_cost = db.Column(db.Float, nullable=True)
    liftgate_cost = db.Column(db.Float, nullable=True)
    limited_cost = db.Column(db.Float, nullable=True)
    residential_cost = db.Column(db.Float, nullable=True)
    inside_cost = db.Column(db.Float, nullable=True)
    insure_cost = db.Column(db.Float, nullable=True)
    return_reason = db.Column(
        db.String(40),
        nullable=True,
    )
    return_details = db.Column(db.String(100), nullable=True)
    on_hold = db.Column(db.Boolean, nullable=False, default=False)
    tracking_number_note = db.Column(db.Text(), nullable=True)
    fulfilled_at = db.Column(db.DateTime, nullable=True)
    onhold_modified_at = db.Column(db.DateTime, nullable=True)
    email_sended = db.Column(db.Boolean, nullable=False, default=False)
    scheduled_date = db.Column(db.DateTime, server_default=db.func.now())

    ref_task_id = db.Column(db.Integer, db.ForeignKey("log2_warehouse_task.id"), nullable=True)
    lightning_order_no = db.Column(db.Integer, db.ForeignKey("log2_lightning_order.outbound_order_no"), nullable=True)

    products = db.relationship("WarehouseTaskProduct", lazy=True, cascade="all, delete-orphan")
    packages = db.relationship("Package", lazy=True, cascade="all, delete-orphan")
    files = db.relationship("TaskFile", lazy=True, cascade="all, delete-orphan")
    lightning_order = db.relationship("LightningOrder", lazy=True)

    def is_fulfilled(self):
        return self.fulfilled_at != None


@dataclass
class Order(db.Model):
    id: int
    created_at: datetime.datetime
    assigned_to: int
    raw_orders: List[RawOrder]
    tasks: List[WarehouseTask]

    __tablename__ = "log2_order"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    assigned_to = db.Column(db.Integer, db.ForeignKey("log2_warehouse.id"), nullable=False)

    raw_orders = db.relationship(
        "RawOrder",
        secondary=AssignedRawOrder.__table__,
        secondaryjoin="AssignedRawOrder.raw_order_id==RawOrder.id",
        lazy=True,
    )

    tasks = db.relationship(
        "WarehouseTask",
        secondary=WarehouseTask.__table__,
        secondaryjoin="WarehouseTask.order_id==Order.id",
        lazy=True,
    )


@dataclass
class Warehouse(db.Model):
    id: int
    code: str
    name: str
    is_vendor: bool

    __tablename__ = "log2_warehouse"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(40), nullable=False)
    is_vendor = db.Column(db.Boolean, nullable=False)


@dataclass
class Freight(db.Model, UpdateMixin):
    class Status(enum.Enum):
        IN_TRANSIT = "In Transit"
        DELIVERED = "Delivered"
        CANCELLED = "Cancelled"
        PICKED_UP = "Picked Up"

    class Mode(enum.Enum):
        AIR = "Air"
        OCEAN = "Ocean"
        TRUCK = "Truck"

    class ContainerType(enum.Enum):
        GP20 = "20GP"
        GP40 = "40GP"
        HQ40 = "40HQ"
        HQ45 = "45HQ"
        LCL = "LCL"

    class Forwarder(enum.Enum):
        FPL = "FPL"
        FLEXPORT = "FLEXPORT"
        LIGHTNING = "LIGHTNING"
        AGL = "AGL"
        SF = "SF"
        DHL = "DHL"

    id: int
    number: str
    ata_wh: datetime.datetime
    eta_wh: datetime.datetime
    eta_dp: datetime.datetime
    ata_dp: datetime.datetime
    etd_op: datetime.datetime
    atd_op: datetime.datetime
    pickup: datetime.datetime
    target_id: int
    status: str
    mode: str
    ori_port: str
    dest_port: str
    container: str
    container_num: str
    ocean_forwarder: str
    cost: float

    __tablename__ = "log2_freight"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), nullable=False)
    ata_wh = db.Column(db.DateTime)
    eta_wh = db.Column(db.DateTime)
    eta_dp = db.Column(db.DateTime)
    ata_dp = db.Column(db.DateTime)
    etd_op = db.Column(db.DateTime)
    atd_op = db.Column(db.DateTime)
    pickup = db.Column(db.DateTime)
    target_id = db.Column(db.Integer, db.ForeignKey("log2_warehouse.id"), nullable=False)
    status = db.Column(
        db.Enum(Status),
    )
    mode = db.Column(
        db.Enum(Mode),
    )
    ori_port = db.Column(db.String)
    dest_port = db.Column(db.String)
    container = db.Column(
        db.Enum(ContainerType),
    )
    container_num = db.Column(db.String(30), nullable=True)
    ocean_forwarder = db.Column(
        db.Enum(Forwarder),
    )
    cost = db.Column(db.Float)

    batches = db.relationship("FreightBatch", backref="freight", lazy=True, cascade="all, delete-orphan")


class Product(db.Model):
    __tablename__ = "log2_product"

    code = db.Column(db.String(60), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    is_accessory = db.Column(db.Boolean, nullable=False)


class Sku(db.Model):
    __tablename__ = "log2_sku"

    sku = db.Column(db.String(60), primary_key=True)


class ProductSku(db.Model):
    __tablename__ = "log2_product_sku"

    sku = db.Column(db.String(60), primary_key=True)
    condition = db.Column(db.Enum(UnitCondition), primary_key=True)
    product_code = db.Column(db.String(60), db.ForeignKey("log2_product.code"), nullable=False)


@dataclass
class Item(db.Model, UpdateMixin):
    sku: str
    serial: str
    condition: str

    __tablename__ = "log2_item"

    serial = db.Column(db.String(60), primary_key=True)
    sku = db.Column(db.String(60), db.ForeignKey("log2_sku.sku"), nullable=False)
    condition = db.Column(
        db.Enum(UnitCondition),
        nullable=True,
    )


@dataclass
class FreightBatch(db.Model, UpdateMixin):
    id: int
    source_id: int
    items: List[Item]
    costs: dict

    __tablename__ = "log2_freight_batch"

    id = db.Column(db.Integer, primary_key=True)
    freight_id = db.Column(db.Integer, db.ForeignKey("log2_freight.id"), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey("log2_warehouse.id"), nullable=False)
    costs = db.Column(JSON)

    items = db.relationship("FreightBatchItem", lazy=True, cascade="all, delete-orphan")


@dataclass
class FreightBatchItem(db.Model):
    serial: str
    batch_condition: str
    sku: str
    item: Item

    __tablename__ = "log2_freight_batch_item"

    batch_id = db.Column("batch_id", db.Integer, db.ForeignKey("log2_freight_batch.id"), primary_key=True)
    serial = db.Column("item_serial", db.String, db.ForeignKey("log2_item.serial"), primary_key=True)
    batch_condition = db.Column(
        "condition",
        db.Enum(UnitCondition),
        nullable=True,
    )

    item = db.relationship("Item", lazy=True)
    sku = association_proxy("item", "sku")


@dataclass
class User(db.Model):
    id: int
    email: str
    username: str
    role: str
    warehouse_id: str

    class Role(enum.Enum):
        GUEST = "guest"
        VIBE_OPERATOR = "vibe operator"
        VIBE_MANAGER = "vibe manager"
        WAREHOUSE = "warehouse"
        ADMIN = "admin"

    __tablename__ = "log2_user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(
        db.Enum(Role),
    )
    warehouse_id = db.Column(db.Integer, db.ForeignKey("log2_warehouse.id"), nullable=True)

    @property
    def password(self):
        raise AttributeError("passowrd is not readable")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


@dataclass
class SyncState(db.Model):
    __tablename__ = "log2_sync_state"

    task = db.Column(db.String, primary_key=True)
    state = db.Column(db.JSON, nullable=True)


def raw_order_filter(q, search):
    return q.filter(
        RawOrder.id.ilike(f"%{search}%")
        | RawOrder.shipping_address1.ilike(f"%{search}%")
        | RawOrder.shipping_address2.ilike(f"%{search}%")
        | RawOrder.shipping_name.ilike(f"%{search}%")
        | RawOrder.shipping_company.ilike(f"%{search}%")
        | RawOrder.shipping_city.ilike(f"%{search}%")
        | RawOrder.shipping_state.ilike(f"%{search}%")
        | RawOrder.email.ilike(f"%{search}%")
    )
