
from collections import namedtuple
import datetime
from manage import Blueprint, jsonify, render_template

from app.models import Item, Package, PackageUnit, RawOrder, RawOrderItem, WarehouseTask, WarehouseTaskProduct


test_oa = Blueprint(
    "test_oa",
    __name__,
    url_prefix="/api",
)

ProductItemInEmail = namedtuple("ProductItemInEmail", ["code", "name", "quantity"])
TrackingItem = namedtuple("TrackingItem", ["number", "url"])


@test_oa.route("/test/", methods=["GET"])
def test():
    context = {
        'subject': 'Your Vibe order is on the way!',
        'order_id': '13580',
        'raw_orders': [RawOrder(id = 'SHO.13659', created_at = datetime.datetime(2023, 10, 17, 21, 4, 39, tzinfo = datetime.timezone.utc), latest_ship_date = datetime.datetime(1900, 1, 1, 0, 0, tzinfo = datetime.timezone.utc), latest_delivery_date = datetime.datetime(1900, 1, 1, 0, 0, tzinfo = datetime.timezone.utc), shopify_id = 4876387483699, email = 'billy.cosgrove@gmail.com', shipping_phone = '+15122879402', shipping_name = 'billy Cosgrove', shipping_address1 = '6300 Rothway Street', shipping_address2 = 'suite 100A', shipping_company = 'choice botanicals', shipping_city = 'Houston', shipping_state = 'TX', shipping_zip = '77040', shipping_country = 'US', order_from = 'Shopify', marketplace = '', business_verification_required = None, finance_verification_required = None, cs_review_required = None, items = [RawOrderItem(product_code = '55S1BB', quantity = 1), RawOrderItem(product_code = 'CA02A', quantity = 1), RawOrderItem(product_code = 'TA01A', quantity = 1)], attachment = None)],
        'products': [ProductItemInEmail(code = 'CA02A2', name = 'Vibe Smart Camera', quantity = 1), ProductItemInEmail(code = '55S1BB', name = 'Vibe Board S1 55"', quantity = 1)],
        'task': WarehouseTask(id = 365, task_type = 'fulfillment' , order_id = 256, source_id = 1, target_id = 18, new_address = None, note = None, products = [WarehouseTaskProduct(id = 552, product_code = 'CA02A', sku = 'CA02A', quantity = 1, serial_note = [], condition =  'good' ), WarehouseTaskProduct(id = 551, product_code = '55S1BB', sku = 'S55T02AUS', quantity = 1, serial_note = [], condition =  'good' )], created_at = datetime.datetime(2023, 10, 18, 2, 7, 31, 709501), carrier = 'RRTS', transport_mode = 'TRUCK', delivery_cost = None, liftgate_cost = None, limited_cost = None, residential_cost = None, inside_cost = None, insure_cost = None, return_reason = None, return_details = None, on_hold = False, tracking_number_note = None, ref_task_id = None, fulfilled_at = datetime.datetime(2023, 10, 18, 2, 25, 12, 284000), onhold_modified_at = None, email_sended = True, scheduled_date = datetime.datetime(2023, 10, 18, 2, 7, 31, 709501), packages = [Package(id = 373, task_id = 365, unit_system = 'BS' , weight = None, length = None, width = None, height = None, sizes = None, tracking_number = 'dafdsafdfdasfdsa', created_at = datetime.datetime(2023, 10, 18, 2, 8, 39, 643161), delivered_at = None, scanned_serials = None, units = [PackageUnit(id = 378, package_id = 373, serial = 'V55B9090360010', product_code = None, status = 'Delivering'  , shipment_damage = None, shipment_damage_note = None, package_box_condition = None, insurance_cost = None, checked = False, restocked = False, if_stylus = None, if_powercord = None, accessories = [], item = Item(sku = 'S55T02AUS', serial = 'V55B9090360010', condition =  'good'  )), PackageUnit(id = 380, package_id = 373, serial = 'VC1B6155390209', product_code = None, status ='Delivering' , shipment_damage = None, shipment_damage_note = None, package_box_condition = None, insurance_cost = None, checked = False, restocked = False, if_stylus = None, if_powercord = None, accessories = [], item = Item(sku = 'CA02A', serial = 'VC1B6155390209', condition =  'good' ))], accessories = [], pkg_fulfilled_at = datetime.datetime(2023, 10, 18, 2, 8, 39, 643161))], lightning_order = None, files = []),
        'tracking_items': [TrackingItem(number = 'dafdsafdfdasfdsa', url = 'https://tools.rrts.com/LTLTrack/?searchValues=dafdsafdfdasfdsa')],
        'has_75_board': False,
        'has_s1_and_camera': False,
        'shipping_name': 'billy Cosgrove',
        'email': 'rik@vibe.us',
        'created_at': datetime.datetime(2023, 10, 17, 21, 4, 39, tzinfo = datetime.timezone.utc),
        'shipping_company': 'choice botanicals',
        'shipping_address1': '6300 Rothway Street',
        'shipping_address2': 'suite 100A',
        'shipping_city': 'Houston',
        'shipping_state': 'TX',
        'shipping_zip': '08234',
        'shipping_country': 'US'
    }
    print(context)
    
    return render_template("tracking_email.html", **context)

