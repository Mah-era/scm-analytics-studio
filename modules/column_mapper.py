"""Auto and manual column mapping helpers."""
from __future__ import annotations

import re
from typing import Dict, List, Optional

import pandas as pd


EXPECTED_FIELDS = [
    "Date", "Product", "SKU", "Category", "Supplier", "Customer", "Region", "Warehouse",
    "Demand", "Forecast", "Sales", "Revenue", "Cost", "COGS", "Average Inventory",
    "Inventory", "Lead Time", "Order Date", "Delivery Date", "Promised Delivery Date",
    "Received Date", "Defective Units", "Total Units", "Shipment Cost", "Carrier", "Route",
    "Shipment ID", "Production Quantity", "Planned Production", "Capacity", "Maximum Capacity",
    "Downtime", "Inbound Quantity", "Outbound Quantity", "Space Used", "Space Capacity",
    "Picks", "Accurate Picks", "Stockout Event", "Fulfilled Orders", "Total Orders",
    "Cost Category", "Procurement Cost", "Logistics Cost", "Last Movement Date",
    "Order ID", "PO Number", "SO Number", "Order Quantity", "Shipped Quantity",
    "Open Quantity", "PO Status", "Order Status", "Shipment Status", "Due Date",
    "Standard Price", "Contract Price", "Actual Price", "Unit Price", "Weight",
    "Volume", "Distance", "Origin", "Destination", "Incoterm", "Currency",
    "Plant", "Site", "Lot", "Batch", "Planner", "Buyer", "Customer Segment",
    "UOM", "Receipt Date", "Issue Date", "Lot Quantity", "Standard Cost",
    "Scrap Quantity", "Good Quantity", "Planned Time", "Run Time", "Schedule Quantity",
    "Actual Start Date", "Actual End Date", "Worker", "Team", "Activity",
    "Start Time", "End Time", "Dock Time", "Putaway Time", "Cycle Count Quantity",
    "System Quantity", "Service Level", "Holding Cost Rate", "Order Cost",
    "Open PO Quantity", "Open Supply", "Backorder Quantity", "Payment Date",
    "Invoice Date", "Collection Date",
]

KEYWORDS = {
    "Date": ["date", "transaction_date", "period"],
    "Product": ["product", "product_name", "item", "item_description", "material"],
    "SKU": ["sku", "stock_keeping", "item_code", "material_code"],
    "Category": ["category", "segment"],
    "Supplier": ["supplier", "supplier_name", "vendor", "vendor_name"],
    "Customer": ["customer", "client"],
    "Region": ["region", "area", "zone", "location"],
    "Warehouse": ["warehouse", "warehouse_location", "warehouse_id", "wh", "depot", "storage"],
    "Demand": ["demand", "demand_qty", "order_qty", "qty_ordered", "ordered_quantity"],
    "Forecast": ["forecast", "forecasted"],
    "Sales": ["sales", "sold", "sales_qty"],
    "Revenue": ["revenue", "income", "sales_value"],
    "Cost": ["cost", "total_cost", "unit_cost", "holding_cost"],
    "COGS": ["cogs", "cost_of_goods"],
    "Average Inventory": ["average_inventory", "avg_inventory"],
    "Inventory": ["inventory", "inventory_on_hand", "stock", "stock_level", "on_hand"],
    "Lead Time": ["lead_time", "lead_time_days", "leadtime"],
    "Order Date": ["order_date", "order_dt", "ordered_date"],
    "Delivery Date": ["delivery_date", "actual_delivery_date", "delivered_date", "actual_delivery", "actual_arrival", "ship_date"],
    "Promised Delivery Date": ["promised_delivery", "promised_date", "eta", "due_date", "target_delivery"],
    "Received Date": ["received_date", "receipt_date"],
    "Defective Units": ["defective", "defects", "defective_units", "defect_units", "defect_qty"],
    "Total Units": ["total_units", "units_supplied", "quantity_supplied", "received_qty"],
    "Shipment Cost": ["shipment_cost", "freight", "freight_cost", "freight_bdt", "transport_cost"],
    "Carrier": ["carrier", "transporter"],
    "Route": ["route", "lane"],
    "Shipment ID": ["shipment_id", "shipment"],
    "Production Quantity": ["production_quantity", "production_qty", "actual_units", "actual_output", "output"],
    "Planned Production": ["planned_production", "planned_production_qty", "planned_units", "planned_output"],
    "Capacity": ["capacity", "capacity_hours", "available_capacity"],
    "Maximum Capacity": ["maximum_capacity", "max_capacity_hours", "max_capacity"],
    "Downtime": ["downtime", "downtime_hours", "machine_downtime"],
    "Inbound Quantity": ["inbound", "received_qty"],
    "Outbound Quantity": ["outbound", "dispatched_qty"],
    "Space Used": ["space_used", "used_space"],
    "Space Capacity": ["space_capacity", "capacity_space"],
    "Picks": ["picks", "picked_orders"],
    "Accurate Picks": ["accurate_picks", "correct_picks"],
    "Stockout Event": ["stockout", "stockout_flag", "stock_out"],
    "Fulfilled Orders": ["fulfilled_orders", "fulfilled"],
    "Total Orders": ["total_orders", "orders"],
    "Cost Category": ["cost_category", "expense_category"],
    "Procurement Cost": ["procurement_cost", "purchase_cost"],
    "Logistics Cost": ["logistics_cost", "transportation_cost"],
    "Last Movement Date": ["last_movement", "last_sold", "last_issue"],
    "Order ID": ["order_id", "order_number"],
    "PO Number": ["po", "po_id", "purchase_order", "po_number"],
    "SO Number": ["so", "sales_order", "so_number"],
    "Order Quantity": ["order_quantity", "ordered_qty", "order_qty"],
    "Shipped Quantity": ["shipped_quantity", "shipped_qty", "ship_qty"],
    "Open Quantity": ["open_quantity", "open_qty"],
    "PO Status": ["po_status", "purchase_order_status"],
    "Order Status": ["order_status"],
    "Shipment Status": ["shipment_status"],
    "Due Date": ["due_date"],
    "Standard Price": ["standard_price", "std_price"],
    "Contract Price": ["contract_price"],
    "Actual Price": ["actual_price", "po_price", "unit_price_bdt"],
    "Unit Price": ["unit_price", "unit_price_bdt", "price"],
    "Weight": ["weight", "kg"],
    "Volume": ["volume", "cube", "cbm"],
    "Distance": ["distance", "miles", "km"],
    "Origin": ["origin", "ship_from"],
    "Destination": ["destination", "ship_to"],
    "Incoterm": ["incoterm"],
    "Currency": ["currency"],
    "Plant": ["plant"],
    "Site": ["site"],
    "Lot": ["lot"],
    "Batch": ["batch"],
    "Planner": ["planner"],
    "Buyer": ["buyer"],
    "Customer Segment": ["customer_segment", "segment"],
    "UOM": ["uom", "unit_of_measure"],
    "Receipt Date": ["receipt_date"],
    "Issue Date": ["issue_date"],
    "Lot Quantity": ["lot_quantity", "lot_qty"],
    "Standard Cost": ["standard_cost", "std_cost"],
    "Scrap Quantity": ["scrap", "scrap_quantity", "scrap_qty"],
    "Good Quantity": ["good_quantity", "good_qty"],
    "Planned Time": ["planned_time", "planned_hours"],
    "Run Time": ["run_time", "runtime"],
    "Schedule Quantity": ["schedule_quantity", "scheduled_qty"],
    "Actual Start Date": ["actual_start"],
    "Actual End Date": ["actual_end"],
    "Worker": ["worker", "operator"],
    "Team": ["team", "crew"],
    "Activity": ["activity", "process"],
    "Start Time": ["start_time", "pick_start"],
    "End Time": ["end_time", "pick_end"],
    "Dock Time": ["dock_time", "dock_start"],
    "Putaway Time": ["putaway_time", "dock_end", "putaway_end"],
    "Cycle Count Quantity": ["cycle_count_quantity", "counted_qty"],
    "System Quantity": ["system_quantity", "system_qty"],
    "Service Level": ["service_level"],
    "Holding Cost Rate": ["holding_cost_rate"],
    "Order Cost": ["order_cost"],
    "Open PO Quantity": ["open_po_quantity", "open_po_qty"],
    "Open Supply": ["open_supply"],
    "Backorder Quantity": ["backorder_quantity", "backorder_qty"],
    "Payment Date": ["payment_date"],
    "Invoice Date": ["invoice_date"],
    "Collection Date": ["collection_date"],
    "Received Date": ["received_date", "receipt_date", "dock_time"],
    "Lot Quantity": ["lot_quantity", "lot_qty", "qty", "quantity"],
    "Open Supply": ["open_supply", "open_po_qty", "open_po_quantity", "inbound_qty"],
    "Backorder Quantity": ["backorder_quantity", "backorder_qty", "backordered_qty"],
    "Start Time": ["start_time", "pick_start", "pick_start_time"],
    "End Time": ["end_time", "pick_end", "pick_end_time"],
    "Dock Time": ["dock_time", "dock_start", "dock_arrival", "receiving_start"],
    "Putaway Time": ["putaway_time", "dock_end", "putaway_end"],
    "SKU": ["sku", "component_sku", "stock_keeping", "item_code", "material_code"],
    "Product": ["product", "parent_sku", "product_name", "item", "item_description", "material"],
    "Order Quantity": ["order_quantity", "gross_requirement", "qty_ordered", "ordered_qty", "order_qty"],
    "Inventory": ["inventory", "inventory_qty", "inventory_on_hand", "component_on_hand", "stock", "stock_level", "on_hand"],
    "Open Supply": ["open_supply", "open_po_qty", "open_po_quantity", "inbound_qty"],
}


def _clean(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")


def auto_map_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """Map expected SCM fields to dataframe columns using keyword matching."""
    clean_cols = {_clean(c): c for c in df.columns}
    mapping: Dict[str, Optional[str]] = {field: None for field in EXPECTED_FIELDS}

    for field in EXPECTED_FIELDS:
        candidates = [_clean(field)] + [_clean(k) for k in KEYWORDS.get(field, [])]
        # Exact match first
        for cand in candidates:
            if cand in clean_cols:
                mapping[field] = clean_cols[cand]
                break
        if mapping[field]:
            continue
        # Partial match
        for clean_col, original in clean_cols.items():
            if any(cand and cand in clean_col for cand in candidates):
                mapping[field] = original
                break

    return mapping


def mapped_col(mapping: Dict[str, Optional[str]], field: str) -> Optional[str]:
    col = mapping.get(field)
    return col if col else None


def available_fields(mapping: Dict[str, Optional[str]]) -> Dict[str, str]:
    return {field: col for field, col in mapping.items() if col}


def required_missing(mapping: Dict[str, Optional[str]], required_fields: List[str]) -> List[str]:
    return [f for f in required_fields if not mapped_col(mapping, f)]
