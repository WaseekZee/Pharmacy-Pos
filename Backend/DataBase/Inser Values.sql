-- Customer
INSERT INTO Customer (CustomerID, Name, Phone) VALUES
(1, 'Ayesha Perera', '0771234567'),
(2, 'Nimal Silva', '0779876543'),
(3, 'Kamal Fernando', '0712345678'),
(4, 'Rashmi Gunasekara', '0755554321'),
(5, 'Suresh Jayasuriya', '0788881234');

-- Employee
INSERT INTO Employee (EmployeeID, Name, Type, Password) VALUES
(1, 'Dilshan Kumara', 'Cashier', 'pass123'),
(2, 'Amali Herath', 'Manager', 'admin321'),
(3, 'Sunil Senanayake', 'StockKeeper', 'stock111'),
(4, 'Ishara Wijesinghe', 'Delivery', 'deliverme'),
(5, 'Thilini Rathnayake', 'Cashier', 'cash@2025');

-- Brand
INSERT INTO Brand (BrandID, Name, Description) VALUES
(1, 'Panadol', 'Pain reliever'),
(2, 'Vicks', 'Cold relief'),
(3, 'Hemas', 'Personal care products'),
(4, 'Dettol', 'Antiseptic range'),
(5, 'Anchor', 'Milk powder');

-- Product
INSERT INTO Product (ProductID, ProductName, Description, BrandID) VALUES
(1, 'Panadol Extra', '500mg tablets', 1),
(2, 'Vicks Balm', 'Relieves cold symptoms', 2),
(3, 'Baby Shampoo', 'Mild shampoo', 3),
(4, 'Dettol Liquid', 'Antiseptic liquid', 4),
(5, 'Anchor Milk', 'Full cream milk powder', 5);

-- Supplier
INSERT INTO Supplier (SupplierID, Name, Telephone, BankAccount) VALUES
(1, 'Health Distributors', '0112345678', 'ACC123456'),
(2, 'Medical Supplies Pvt', '0118765432', 'ACC654321'),
(3, 'Global Pharma', '0111112222', 'ACC987654'),
(4, 'ABC Traders', '0113334444', 'ACC223344'),
(5, 'Wellness Partners', '0115556666', 'ACC112233');

-- Stock
INSERT INTO Stock (StockID, ProductID, ExpDate, MfgDate, PurchasePrice, SellingPrice, Quantity, SupplierID) VALUES
(1, 1, '2025-12-31', '2024-12-01', 10.00, 15.00, 100, 1),
(2, 2, '2026-01-15', '2025-01-10', 5.50, 9.00, 150, 2),
(3, 3, '2025-11-30', '2024-11-01', 12.00, 18.00, 80, 3),
(4, 4, '2025-10-31', '2024-10-05', 8.00, 12.00, 90, 4),
(5, 5, '2026-03-01', '2025-03-01', 15.00, 22.00, 200, 5);

-- Order
INSERT INTO [Order] (OrderID, Date, Quantity, TotalAmount, PaymentType, CustomerID, EmployeeID) VALUES
(1, '2025-06-01', 5, 75.00, 'Cash', 1, 1),
(2, '2025-06-02', 3, 45.00, 'Card', 2, 2),
(3, '2025-06-03', 4, 60.00, 'Online', 3, 3),
(4, '2025-06-04', 2, 30.00, 'Cash', 4, 4),
(5, '2025-06-05', 6, 90.00, 'Card', 5, 5);

-- Pack
INSERT INTO Pack (PackID, Quantity, Date, ProductID, OrderID, StockID) VALUES
(1, 2, '2025-06-01', 1, 1, 1),
(2, 1, '2025-06-02', 2, 2, 2),
(3, 3, '2025-06-03', 3, 3, 3),
(4, 1, '2025-06-04', 4, 4, 4),
(5, 4, '2025-06-05', 5, 5, 5);

-- ReturnedStock
INSERT INTO ReturnedStock (RStockID, ReturnedDate, Reason, Quantity, StockID, ProductID) VALUES
(1, '2025-06-06', 'Damaged packaging', 5, 1, 1),
(2, '2025-06-07', 'Expired', 3, 2, 2),
(3, '2025-06-08', 'Wrong item', 2, 3, 3),
(4, '2025-06-09', 'Overstock', 6, 4, 4),
(5, '2025-06-10', 'Customer return', 4, 5, 5);

-- ReturnProduct
INSERT INTO ReturnProduct (CRID, Date, Quantity, Reason, CustomerID, ProductID) VALUES
(1, '2025-06-06', 1, 'Defective item', 1, 1),
(2, '2025-06-07', 2, 'Changed mind', 2, 2),
(3, '2025-06-08', 1, 'Expired', 3, 3),
(4, '2025-06-09', 1, 'Damaged', 4, 4),
(5, '2025-06-10', 3, 'Wrong product', 5, 5);

-- OrderProduct
INSERT INTO OrderProduct (OrderID, ProductID) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5);
