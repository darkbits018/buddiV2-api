# Farm Management System API Documentation

## Overview
This API provides endpoints for managing a farm-based sales and appointment system, including features for managing farmers, items, sales, appointments, and generating various reports.

## Table of Contents
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Farmers](#farmers)
  - [Items](#items)
  - [Sales](#sales)
  - [Appointments](#appointments)
  - [Buyers](#buyers)
  - [Invoices](#invoices)
  - [Reports](#reports)
  - [Sales Trends](#sales-trends)

## Authentication
Authentication details should be added here 

## Endpoints

### Farmers
#### Create Farmer
```http
POST /farmers
```
**Request Body:**
```json
{
    "name": "string",
    "phone_number": "string",
    "email": "string",
    "address": "string"
}
```
**Response:** Returns farmer_id and success message

### Items
#### Add Item
```http
POST /items
```
**Request Body:**
```json
{
    "farmer_id": "integer",
    "item_name": "string",
    "description": "string",
    "quantity": "integer",
    "price": "float"
}
```

#### Get Item
```http
GET /items/<item_id>
```
Returns specific item details

#### Get Items by Farmer
```http
GET /items/farmer/<farmer_id>
```
Returns all items for a specific farmer

### Sales
#### Record Sale
```http
POST /sales
```
**Request Body:**
```json
{
    "item_id": "integer",
    "buyer_id": "integer",
    "quantity_sold": "integer",
    "sale_price": "float"
}
```

#### Get Sale
```http
GET /sales/<sale_id>
```
Returns specific sale details

#### Get Sales by Farmer
```http
GET /sales/farmer/<farmer_id>
```
Returns all sales for a specific farmer

### Appointments
#### Create Appointment
```http
POST /appointments
```
**Request Body:**
```json
{
    "farmer_id": "integer",
    "buyer_id": "integer",
    "appointment_date": "datetime"
}
```

#### Update Appointment
```http
PUT /appointments/<id>
```
**Request Body:**
```json
{
    "status": "string"
}
```

### Buyers
#### Create Buyer
```http
POST /buyers
```
**Request Body:**
```json
{
    "name": "string",
    "phone_number": "string",
    "email": "string",
    "address": "string"
}
```

### Invoices
#### Download Invoice
```http
GET /invoices/<sale_id>
```
Returns PDF invoice for the specified sale

### Reports

#### Monthly Sales Report
```http
GET /api/sales/report/monthly
```
Returns PNG image of monthly sales chart for current year

#### Yearly Sales Report
```http
GET /api/sales/report/yearly
```
Returns PNG image of yearly sales chart

#### Quarterly Sales Report
```http
GET /api/sales/report/quarterly
```
Returns PNG image of quarterly sales chart

#### Specific Month/Year Report
```http
GET /api/sales/report/specific-month-png?year=<year>&month=<month>
```
Returns PNG image of sales report for specific month and year

#### Specific Year Report
```http
GET /api/sales/report/year/<year>
```
Returns PNG image of sales report for specific year

### Item-Specific Reports

#### Monthly Item Sales Report
```http
GET /api/sales/item-report/monthly
```
Returns PNG image of monthly sales chart by item

#### Yearly Item Sales Report
```http
GET /api/sales/item-report/yearly
```
Returns PNG image of yearly sales chart by item

#### Quarterly Item Sales Report
```http
GET /api/sales/item-report/quarterly
```
Returns PNG image of quarterly sales chart by item

#### Specific Year Item Report
```http
GET /api/sales/item-report/year/<year>
```
Returns PNG image of sales report by item for specific year

#### Specific Month Item Report
```http
GET /api/sales/item-report/month/<year>/<month>
```
Returns PNG image of sales report by item for specific month and year

### Sales Trends

#### Individual Item Sales Trend
```http
GET /sales_trends/<item_id>
```
Returns PNG image of sales trend chart for specific item

#### All Items Sales Trends
```http
GET /sales-trends-all
```
Returns PNG image of sales trends chart for all items

## Response Formats
- JSON responses for data operations
- PNG images for reports and charts
- PDF for invoices

## Error Handling
The API returns appropriate HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 404: Not Found
- 500: Server Error

## Dependencies
- Flask
- SQLAlchemy
- Matplotlib
- ReportLab
- Pandas

## Notes
- All report endpoints generate visualizations using Matplotlib
- Charts are returned as PNG images
- Invoices are generated as PDF documents
- Database operations use SQLAlchemy ORM
