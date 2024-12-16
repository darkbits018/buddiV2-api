[![wakatime](https://wakatime.com/badge/github/darkbits018/buddiV2-api.svg)](https://wakatime.com/badge/github/darkbits018/buddiV2-api)
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

### 1. Monthly Sales Report
- **Endpoint:** `/api/sales/report/monthly`
- **Method:** GET
- **Description:** Generates a monthly sales report for the current year
- **Response:**
  - `image_url`: URL of the generated PNG sales chart
  - **Chart Details:** 
    - X-axis: Months (Jan-Dec)
    - Y-axis: Total Sales
    - Title: Monthly Sales Report (Current Year)

### 2. Yearly Sales Report
- **Endpoint:** `/api/sales/report/yearly`
- **Method:** GET
- **Description:** Generates a line chart of total sales across all years
- **Response:**
  - `report_url`: URL of the generated PNG sales chart
  - `years`: List of years with sales data
  - **Chart Details:**
    - X-axis: Years
    - Y-axis: Total Sales
    - Marker: Circular points
    - Line Style: Solid blue line

### 3. Quarterly Sales Report
- **Endpoint:** `/api/sales/report/quarterly`
- **Method:** GET
- **Description:** Generates a quarterly sales report for the current year
- **Response:**
  - `report_url`: URL of the generated PNG sales chart
  - `year`: Current year of the report
  - **Chart Details:**
    - X-axis: Quarters (Q1-Q4)
    - Y-axis: Total Sales
    - Title: Quarterly Sales Report (Current Year)

### 4. Specific Year Sales Report
- **Endpoint:** `/api/sales/report/year/<int:year>`
- **Method:** GET
- **Description:** Generates a sales report for a specific year
- **Parameters:**
  - `year`: Target year for the report (integer)
- **Response:**
  - `report_url`: URL of the generated PNG sales chart
  - **Chart Details:**
    - X-axis: Year
    - Y-axis: Total Sales
    - Title: Sales Report for [Specified Year]

### 5. Monthly Item Sales Report
- **Endpoint:** `/api/sales/item-report/monthly`
- **Method:** GET
- **Description:** Generates a monthly sales report for all items in the current year
- **Response:**
  - `report_url`: URL of the generated PNG sales chart
  - **Chart Details:**
    - X-axis: Months
    - Y-axis: Total Quantity Sold
    - Multiple lines representing different items
    - Title: Monthly Sales Report for Current Year

### 6. Yearly Item Sales Report
- **Endpoint:** `/api/sales/item-report/yearly`
- **Method:** GET
- **Description:** Generates a yearly sales report comparing items across years
- **Response:**
  - `report_url`: URL of the generated PNG sales chart
  - **Chart Details:**
    - X-axis: Years
    - Y-axis: Total Quantity Sold
    - Grouped bar chart with different items
    - Title: Yearly Sales Report

### 7. Quarterly Item Sales Report
- **Endpoint:** `/api/sales/report/quarterly`
- **Method:** GET
- **Description:** Generates a quarterly sales report comparing items
- **Response:**
  - `report_url`: URL of the generated PNG sales chart
  - **Chart Details:**
    - X-axis: Quarters (Q1-Q4)
    - Y-axis: Total Quantity Sold
    - Grouped bar chart with different items
    - Title: Quarterly Sales Report

### 8. Specific Year Item Sales Report
- **Endpoint:** `/api/sales/item-report/year/<int:year>`
- **Method:** GET
- **Description:** Generates an item sales report for a specific year
- **Parameters:**
  - `year`: Target year for the report (integer)
- **Response:**
  - `report_url`: URL of the generated PNG sales chart
  - **Chart Details:**
    - X-axis: Items
    - Y-axis: Total Quantity Sold
    - Bar chart with quantity labels
    - Title: Sales Report for [Specified Year]

### 9. Specific Month Item Sales Report
- **Endpoint:** `/api/sales/item-report/month/<int:year>/<int:month>`
- **Method:** GET
- **Description:** Generates an item sales report for a specific month and year
- **Parameters:**
  - `year`: Target year (integer)
  - `month`: Target month (integer, 1-12)
- **Response:**
  - `report_url`: URL of the generated PNG sales chart
  - **Chart Details:**
    - X-axis: Items
    - Y-axis: Total Quantity Sold
    - Bar chart with quantity labels
    - Title: Sales Report for [Month]/[Year]

### 10. Single Item Sales Trend
- **Endpoint:** `/sales_trends/<int:item_id>`
- **Method:** GET
- **Description:** Generates a sales trend report for a specific item
- **Parameters:**
  - `item_id`: Unique identifier for the item (integer)
- **Response:**
  - `report_url`: URL of the generated PNG sales trend chart
  - `item_name`: Name of the item
  - `item_id`: ID of the item
  - **Chart Details:**
    - X-axis: Years
    - Y-axis: Quantity Sold
    - Line plot with markers
    - Title: Sales Trend for [Item Name]

### 11. All Items Sales Trends
- **Endpoint:** `/sales-trends-all`
- **Method:** GET
- **Description:** Generates sales trend reports for all items
- **Response:**
  - `report_url`: URL of the generated PNG sales trends chart
  - **Chart Details:**
    - Separate subplot for each item
    - X-axis: Years
    - Y-axis: Total Quantity Sold
    - Bar chart with quantity labels

## Response Formats
- JSON responses for data operations
- All reports are generated as PNG images
- Images are automatically uploaded to S3 and a public URL is returned
- Reports are dynamically generated based on available sales data
- Time-based reports default to the current year when applicable

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
