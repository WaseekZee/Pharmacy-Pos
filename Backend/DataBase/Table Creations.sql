CREATE TABLE Customer (
    CustomerID INT PRIMARY KEY,
    Name VARCHAR(100),
    Phone VARCHAR(20)
);

CREATE TABLE Employee (
    EmployeeID INT PRIMARY KEY,
    Name VARCHAR(100),
    Type VARCHAR(50),
    Password VARCHAR(100)
);

CREATE TABLE Brand (
    BrandID INT PRIMARY KEY,
    Name VARCHAR(100),
    Description TEXT
);

CREATE TABLE Product (
    ProductID INT PRIMARY KEY,
    ProductName VARCHAR(100),
    Description TEXT,
    BrandID INT,
    FOREIGN KEY (BrandID) REFERENCES Brand(BrandID)
);

CREATE TABLE Supplier (
    SupplierID INT PRIMARY KEY,
    Name VARCHAR(100),
    Telephone VARCHAR(20),
    BankAccount VARCHAR(50)
);

CREATE TABLE Stock (
    StockID INT,
    ProductID INT,
    ExpDate DATE,
    MfgDate DATE,
    PurchasePrice DECIMAL(10, 2),
    SellingPrice DECIMAL(10, 2),
    Quantity INT,
    SupplierID INT,
    PRIMARY KEY (StockID, ProductID),
    FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
);

CREATE TABLE [Order] (
    OrderID INT PRIMARY KEY,
    Date DATE,
    Quantity INT,
    TotalAmount DECIMAL(10, 2),
    PaymentType VARCHAR(50),
    CustomerID INT,
    EmployeeID INT,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID)
);

CREATE TABLE Pack (
    PackID INT PRIMARY KEY,
    Quantity INT,
    Date DATE,
    ProductID INT,
    OrderID INT,
    StockID INT,
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    FOREIGN KEY (OrderID) REFERENCES [Order](OrderID),
    FOREIGN KEY (StockID, ProductID) REFERENCES Stock(StockID, ProductID)
);

CREATE TABLE ReturnedStock (
    RStockID INT PRIMARY KEY,
    ReturnedDate DATE,
    Reason TEXT,
    Quantity INT,
    StockID INT,
    ProductID INT,
    FOREIGN KEY (StockID, ProductID) REFERENCES Stock(StockID, ProductID)
);

CREATE TABLE ReturnProduct (
    CRID INT PRIMARY KEY,
    Date DATE,
    Quantity INT,
    Reason TEXT,
    CustomerID INT,
    ProductID INT,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
);

CREATE TABLE OrderProduct (
    OrderID INT,
    ProductID INT,
    PRIMARY KEY (OrderID, ProductID),
    FOREIGN KEY (OrderID) REFERENCES [Order](OrderID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
);
