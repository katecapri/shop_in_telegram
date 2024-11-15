from openpyxl import load_workbook
import datetime

def add_order_in_orders_table(user, address, total_sum, user_order):
    wb = load_workbook("/application/src/media/orders.xlsx")
    ws = wb.active
    ws.append([datetime.datetime.now(), user.name, user.phone, address, user_order, total_sum])
    wb.save("/application/src/media/orders.xlsx")
    wb.close()