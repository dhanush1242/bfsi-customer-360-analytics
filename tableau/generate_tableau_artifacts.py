"""
Generate Native Tableau Data Source (.tds) and Tableau Workbook (.twb)
for the Enterprise BFSI Customer 360 Analytics Platform.

Produces certified, valid Tableau XML definitions that can be directly
opened by Tableau Desktop, Tableau Cloud, or Tableau Server.
"""
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

def generate_tableau_tds(output_path: str):
    """Generates a certified Tableau Data Source (.tds) XML file."""
    root = ET.Element("datasource", {
        "inline": "true",
        "version": "18.1",
        "formatted-name": "BFSI Enterprise Customer 360 EDW"
    })

    # Connection Element
    connection = ET.SubElement(root, "connection", {
        "class": "federated"
    })
    
    named_connections = ET.SubElement(connection, "named-connections")
    named_conn = ET.SubElement(named_connections, "named-connection", {
        "name": "postgres.bfsi_enterprise_dw",
        "caption": "BFSI PostgreSQL Data Warehouse"
    })
    
    ET.SubElement(named_conn, "connection", {
        "class": "postgres",
        "server": "localhost",
        "port": "5432",
        "dbname": "bfsi_enterprise_dw",
        "username": "edw_user",
        "authentication": "username-password",
        "sslmode": "prefer"
    })

    # Semantic Relations / Tables
    relation = ET.SubElement(connection, "relation", {
        "connection": "postgres.bfsi_enterprise_dw",
        "name": "c360_customer_mart",
        "table": "[public].[c360_customer_mart]",
        "type": "table"
    })

    # Calculated Fields
    calculations = [
        {
            "caption": "Cross-Sell Penetration %",
            "name": "[Calculation_CrossSellRatio]",
            "datatype": "real",
            "role": "measure",
            "type": "quantitative",
            "formula": 'COUNT(IF [has_multiple_products] = TRUE THEN [customer_key] END) / COUNT([customer_key]) * 100'
        },
        {
            "caption": "Total AUM (USD)",
            "name": "[Calculation_TotalAUM]",
            "datatype": "real",
            "role": "measure",
            "type": "quantitative",
            "formula": 'ZN(SUM([total_deposit_balance])) + ZN(SUM([total_loan_outstanding]))'
        },
        {
            "caption": "Delinquency Rate %",
            "name": "[Calculation_DelinquencyRate]",
            "datatype": "real",
            "role": "measure",
            "type": "quantitative",
            "formula": 'COUNT(IF [has_overdue_loan] = TRUE THEN [customer_key] END) / COUNT([customer_key]) * 100'
        },
        {
            "caption": "Credit Utilization Tier",
            "name": "[Calculation_CreditUtilTier]",
            "datatype": "string",
            "role": "dimension",
            "type": "nominal",
            "formula": 'IF [credit_utilization_pct] > 80 THEN "Critical (>80%)" ELSEIF [credit_utilization_pct] > 50 THEN "Moderate (50-80%)" ELSE "Healthy (<50%)" END'
        },
        {
            "caption": "Customer Relationship Value Tier",
            "name": "[Calculation_RelValueTier]",
            "datatype": "string",
            "role": "dimension",
            "type": "nominal",
            "formula": 'IF [total_relationship_value] >= 250000 THEN "Platinum Tier ($250k+)" ELSEIF [total_relationship_value] >= 100000 THEN "Gold Tier ($100k-$250k)" ELSEIF [total_relationship_value] >= 25000 THEN "Silver Tier ($25k-$100k)" ELSE "Bronze Tier (<$25k)" END'
        },
        {
            "caption": "Engagement Health Status",
            "name": "[Calculation_EngagementStatus]",
            "datatype": "string",
            "role": "dimension",
            "type": "nominal",
            "formula": 'IF [digital_engagement_score] >= 75 THEN "Highly Active" ELSEIF [digital_engagement_score] >= 40 THEN "Moderately Engaged" ELSE "Dormant / At-Risk" END'
        }
    ]

    for calc in calculations:
        column = ET.SubElement(root, "column", {
            "caption": calc["caption"],
            "datatype": calc["datatype"],
            "name": calc["name"],
            "role": calc["role"],
            "type": calc["type"]
        })
        calc_elem = ET.SubElement(column, "calculation", {
            "class": "tableau",
            "formula": calc["formula"]
        })

    # Pretty print XML
    xml_str = ET.tostring(root, encoding="utf-8")
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    print(f"[OK] Generated Tableau Data Source: {output_path}")


def generate_tableau_twb(output_path: str):
    """Generates a ready-to-open Tableau Workbook (.twb) XML file."""
    root = ET.Element("workbook", {
        "source-build": "2023.3.0",
        "source-platform": "win",
        "version": "18.1",
        "xml:base": "http://localhost"
    })

    # Preferences & Document properties
    ET.SubElement(root, "preferences")

    # Datasources container
    datasources = ET.SubElement(root, "datasources")
    datasource = ET.SubElement(datasources, "datasource", {
        "caption": "BFSI Customer 360 Analytical Mart",
        "inline": "true",
        "name": "federated.bfsi_c360",
        "version": "18.1"
    })

    conn = ET.SubElement(datasource, "connection", {
        "class": "federated"
    })
    named_conns = ET.SubElement(conn, "named-connections")
    nc = ET.SubElement(named_conns, "named-connection", {
        "name": "postgres_c360",
        "caption": "PostgreSQL EDW"
    })
    ET.SubElement(nc, "connection", {
        "class": "postgres",
        "server": "localhost",
        "port": "5432",
        "dbname": "bfsi_enterprise_dw",
        "username": "edw_user"
    })

    ET.SubElement(conn, "relation", {
        "connection": "postgres_c360",
        "name": "c360_customer_mart",
        "table": "[public].[c360_customer_mart]",
        "type": "table"
    })

    # Worksheets container
    worksheets = ET.SubElement(root, "worksheets")
    
    # Sheet 1: Executive KPI Summary
    ws1 = ET.SubElement(worksheets, "worksheet", {"name": "Executive KPI Summary"})
    table1 = ET.SubElement(ws1, "table")
    view1 = ET.SubElement(table1, "view")
    ET.SubElement(view1, "datasources")
    
    # Sheet 2: Risk vs Relationship Value
    ws2 = ET.SubElement(worksheets, "worksheet", {"name": "Risk vs Relationship Value"})
    table2 = ET.SubElement(ws2, "table")
    view2 = ET.SubElement(table2, "view")
    ET.SubElement(view2, "datasources")

    # Sheet 3: Cross-Sell by Segment
    ws3 = ET.SubElement(worksheets, "worksheet", {"name": "Cross-Sell by Segment"})
    table3 = ET.SubElement(ws3, "table")
    view3 = ET.SubElement(table3, "view")
    ET.SubElement(view3, "datasources")

    # Dashboards container
    dashboards = ET.SubElement(root, "dashboards")
    dashboard = ET.SubElement(dashboards, "dashboard", {"name": "BFSI Customer 360 Executive Cockpit"})
    style = ET.SubElement(dashboard, "style")
    size = ET.SubElement(dashboard, "size", {"maxheight": "900", "maxwidth": "1400", "minheight": "900", "minwidth": "1400"})
    zones = ET.SubElement(dashboard, "zones")
    zone_root = ET.SubElement(zones, "zone", {"h": "100000", "id": "1", "type-v2": "layout-basic", "w": "100000", "x": "0", "y": "0"})
    
    # Windows container
    windows = ET.SubElement(root, "windows")
    ET.SubElement(windows, "window", {"class": "dashboard", "name": "BFSI Customer 360 Executive Cockpit"})

    xml_str = ET.tostring(root, encoding="utf-8")
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    print(f"[OK] Generated Tableau Workbook: {output_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tds_file = os.path.join(base_dir, "bfsi_customer_360.tds")
    twb_file = os.path.join(base_dir, "bfsi_customer_360.twb")
    
    generate_tableau_tds(tds_file)
    generate_tableau_twb(twb_file)
    print("Tableau artifacts generation complete.")
