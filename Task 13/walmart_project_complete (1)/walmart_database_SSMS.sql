USE master
GO

IF EXISTS (SELECT name FROM sys.databases WHERE name = 'WalmartSalesForecast')
BEGIN
    ALTER DATABASE WalmartSalesForecast
        SET SINGLE_USER WITH ROLLBACK IMMEDIATE
    DROP DATABASE WalmartSalesForecast
END
GO

CREATE DATABASE WalmartSalesForecast
GO

USE WalmartSalesForecast
GO

CREATE TABLE Stores (
    Store   INT          NOT NULL,
    Type    NVARCHAR(5)  NOT NULL,
    Size    INT          NOT NULL,
    CONSTRAINT PK_Stores PRIMARY KEY (Store)
)
GO

CREATE TABLE Features (
    FeatureID    INT           IDENTITY(1,1) NOT NULL,
    Store        INT           NOT NULL,
    Date         DATE          NOT NULL,
    Temperature  FLOAT         NULL,
    Fuel_Price   DECIMAL(10,4) NULL,
    MarkDown1    DECIMAL(18,2) NULL,
    MarkDown2    DECIMAL(18,2) NULL,
    MarkDown3    DECIMAL(18,2) NULL,
    MarkDown4    DECIMAL(18,2) NULL,
    MarkDown5    DECIMAL(18,2) NULL,
    CPI          FLOAT         NULL,
    Unemployment FLOAT         NULL,
    IsHoliday    BIT           NOT NULL DEFAULT 0,
    CONSTRAINT PK_Features       PRIMARY KEY (FeatureID),
    CONSTRAINT FK_Features_Store  FOREIGN KEY (Store) REFERENCES Stores(Store)
)
GO

CREATE TABLE SalesTraining (
    SaleID       INT           IDENTITY(1,1) NOT NULL,
    Store        INT           NOT NULL,
    Dept         INT           NOT NULL,
    Date         DATE          NOT NULL,
    Weekly_Sales DECIMAL(18,2) NOT NULL,
    IsHoliday    BIT           NOT NULL DEFAULT 0,
    CONSTRAINT PK_SalesTraining  PRIMARY KEY (SaleID),
    CONSTRAINT FK_Sales_Store    FOREIGN KEY (Store) REFERENCES Stores(Store)
)
GO

CREATE TABLE SalesTest (
    TestID    INT  IDENTITY(1,1) NOT NULL,
    Store     INT  NOT NULL,
    Dept      INT  NOT NULL,
    Date      DATE NOT NULL,
    IsHoliday BIT  NOT NULL DEFAULT 0,
    CONSTRAINT PK_SalesTest   PRIMARY KEY (TestID),
    CONSTRAINT FK_Test_Store  FOREIGN KEY (Store) REFERENCES Stores(Store)
)
GO

CREATE TABLE ModelPredictions (
    PredictionID     INT           IDENTITY(1,1) NOT NULL,
    Store            INT           NOT NULL,
    Dept             INT           NOT NULL,
    PredictionDate   DATETIME      NOT NULL DEFAULT GETDATE(),
    Temperature      FLOAT         NULL,
    Fuel_Price       DECIMAL(10,4) NULL,
    CPI              FLOAT         NULL,
    IsHoliday        BIT           NOT NULL DEFAULT 0,
    Predicted_Sales  DECIMAL(18,2) NOT NULL,
    Historical_Avg   DECIMAL(18,2) NULL,
    Confidence_Score FLOAT         NULL,
    Model_Used       NVARCHAR(100) NULL,
    CONSTRAINT PK_ModelPredictions PRIMARY KEY (PredictionID)
)
GO

CREATE TABLE AuditLog (
    AuditID    INT           IDENTITY(1,1) NOT NULL,
    ActionType NVARCHAR(10)  NOT NULL,
    TableName  NVARCHAR(100) NOT NULL,
    RecordID   INT           NULL,
    OldValue   NVARCHAR(MAX) NULL,
    NewValue   NVARCHAR(MAX) NULL,
    ActionTime DATETIME      NOT NULL DEFAULT GETDATE(),
    ActionBy   NVARCHAR(100) NOT NULL DEFAULT SYSTEM_USER,
    CONSTRAINT PK_AuditLog PRIMARY KEY (AuditID)
)
GO

CREATE TABLE PipelineLog (
    LogID        INT           IDENTITY(1,1) NOT NULL,
    TableName    NVARCHAR(100) NOT NULL,
    RowsInserted INT           NOT NULL DEFAULT 0,
    RowsFailed   INT           NOT NULL DEFAULT 0,
    StartTime    DATETIME      NULL,
    EndTime      DATETIME      NULL,
    Status       NVARCHAR(20)  NOT NULL DEFAULT 'PENDING',
    ErrorMessage NVARCHAR(MAX) NULL,
    CONSTRAINT PK_PipelineLog PRIMARY KEY (LogID)
)
GO

CREATE INDEX IX_Sales_Store_Dept ON SalesTraining(Store, Dept)
CREATE INDEX IX_Sales_Date       ON SalesTraining(Date)
CREATE INDEX IX_Features_Store   ON Features(Store, Date)
GO

INSERT INTO Stores (Store, Type, Size) VALUES
(1,  'A', 151315), (2,  'A', 202307), (3,  'B', 37392),
(4,  'A', 205863), (5,  'B', 34875),  (6,  'A', 202505),
(7,  'B', 70713),  (8,  'A', 155078), (9,  'B', 125833),
(10, 'B', 126512), (11, 'A', 207499), (12, 'B', 112238),
(13, 'A', 219622), (14, 'A', 200898), (15, 'B', 123737),
(16, 'B', 57197),  (17, 'B', 93188),  (18, 'B', 120653),
(19, 'A', 203819), (20, 'A', 203742), (21, 'B', 140167),
(22, 'B', 119557), (23, 'B', 114533), (24, 'A', 203819),
(25, 'B', 128107), (26, 'A', 152513), (27, 'A', 204184),
(28, 'A', 206302), (29, 'B', 93638),  (30, 'C', 42988),
(31, 'A', 203750), (32, 'A', 203007), (33, 'A', 39690),
(34, 'A', 158114), (35, 'B', 103681), (36, 'A', 39910),
(37, 'C', 39910),  (38, 'C', 39690),  (39, 'A', 184109),
(40, 'A', 155083), (41, 'A', 196321), (42, 'C', 39690),
(43, 'C', 41062),  (44, 'C', 39910),  (45, 'B', 118221)
GO

INSERT INTO Features
    (Store, Date, Temperature, Fuel_Price, MarkDown1, CPI, Unemployment, IsHoliday)
VALUES
(1,  '2010-02-05', 42.31, 2.572, NULL,     211.09, 8.106, 0),
(1,  '2010-02-12', 38.51, 2.548, NULL,     211.24, 8.106, 1),
(1,  '2010-02-19', 39.93, 2.514, NULL,     211.29, 8.106, 0),
(1,  '2010-11-26', 55.00, 3.100, 9220.00,  215.00, 7.800, 1),
(1,  '2010-12-31', 35.00, 3.200, 11000.00, 215.50, 7.700, 1)
GO

INSERT INTO SalesTraining (Store, Dept, Date, Weekly_Sales, IsHoliday) VALUES
(1,  1, '2010-02-05', 24924.50, 0),
(1,  1, '2010-02-12', 46039.49, 1),
(1,  1, '2010-02-19', 41595.55, 0),
(1,  1, '2010-02-26', 19403.54, 0)
GO

CREATE VIEW vw_SalesWithStoreInfo AS
SELECT
    s.SaleID,
    s.Store,
    st.Type  AS StoreType,
    st.Size  AS StoreSize,
    s.Dept,
    s.Date,
    s.Weekly_Sales,
    s.IsHoliday,
    CASE st.Type
        WHEN 'A' THEN 'Large Store'
        WHEN 'B' THEN 'Medium Store'
        WHEN 'C' THEN 'Small Store'
    END AS StoreCategory
FROM SalesTraining s
JOIN Stores st ON s.Store = st.Store
GO

CREATE VIEW vw_MonthlySalesTrend AS
SELECT
    s.Store,
    st.Type             AS StoreType,
    YEAR(s.Date)        AS SaleYear,
    MONTH(s.Date)       AS SaleMonth,
    COUNT(*)            AS WeekCount,
    AVG(s.Weekly_Sales) AS Avg_Sales,
    SUM(s.Weekly_Sales) AS Total_Sales
FROM SalesTraining s
JOIN Stores st ON s.Store = st.Store
GROUP BY s.Store, st.Type, YEAR(s.Date), MONTH(s.Date)
GO

CREATE VIEW vw_HolidayImpact AS
SELECT
    IsHoliday,
    AVG(Weekly_Sales) AS Avg_Sales,
    MAX(Weekly_Sales) AS Max_Sales,
    MIN(Weekly_Sales) AS Min_Sales,
    SUM(Weekly_Sales) AS Total_Sales
FROM SalesTraining
GROUP BY IsHoliday
GO

CREATE VIEW vw_TopStores AS
SELECT
    s.Store,
    st.Type,
    st.Size,
    AVG(s.Weekly_Sales)    AS Avg_Weekly_Sales,
    SUM(s.Weekly_Sales)    AS Total_Sales
FROM SalesTraining s
JOIN Stores st ON s.Store = st.Store
GROUP BY s.Store, st.Type, st.Size
GO

CREATE VIEW vw_SalesWithEconomicFactors AS
SELECT
    s.Store,
    s.Dept,
    s.Date,
    s.Weekly_Sales,
    s.IsHoliday,
    st.Type  AS StoreType,
    st.Size  AS StoreSize,
    f.Temperature,
    f.Fuel_Price,
    f.CPI,
    f.Unemployment
FROM SalesTraining s
JOIN Stores   st ON s.Store = st.Store
JOIN Features f  ON s.Store = f.Store AND s.Date = f.Date
GO

CREATE FUNCTION fn_GetStoreAvgSales (@StoreID INT)
RETURNS DECIMAL(18,2)
AS
BEGIN
    DECLARE @Avg DECIMAL(18,2)
    SELECT @Avg = AVG(Weekly_Sales)
    FROM SalesTraining
    WHERE Store = @StoreID
    RETURN ISNULL(@Avg, 0)
END
GO

CREATE FUNCTION fn_GetHolidayLiftPercent (@StoreID INT)
RETURNS FLOAT
AS
BEGIN
    DECLARE @Reg  FLOAT
    DECLARE @Hol  FLOAT
    DECLARE @Lift FLOAT

    SELECT @Reg = AVG(CAST(Weekly_Sales AS FLOAT))
    FROM SalesTraining
    WHERE Store = @StoreID AND IsHoliday = 0

    SELECT @Hol = AVG(CAST(Weekly_Sales AS FLOAT))
    FROM SalesTraining
    WHERE Store = @StoreID AND IsHoliday = 1

    IF @Reg IS NULL OR @Reg = 0
        RETURN 0

    SET @Lift = ((@Hol - @Reg) / @Reg) * 100
    RETURN ISNULL(@Lift, 0)
END
GO

CREATE PROCEDURE sp_GetStoreSales
    @StoreID INT,
    @Weeks   INT = 12
AS
BEGIN
    SET NOCOUNT ON
    SELECT TOP (@Weeks)
        s.Store,
        st.Type   AS StoreType,
        s.Dept,
        s.Date,
        s.Weekly_Sales,
        s.IsHoliday
    FROM SalesTraining s
    JOIN Stores st ON s.Store = st.Store
    WHERE s.Store = @StoreID
    ORDER BY s.Date DESC
END
GO

CREATE PROCEDURE sp_SavePrediction
    @Store          INT,
    @Dept           INT,
    @Temperature    FLOAT,
    @FuelPrice      DECIMAL(10,4),
    @CPI            FLOAT,
    @IsHoliday      BIT,
    @PredictedSales DECIMAL(18,2),
    @HistAvg        DECIMAL(18,2),
    @Confidence     FLOAT,
    @ModelUsed      NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON
    INSERT INTO ModelPredictions
        (Store, Dept, Temperature, Fuel_Price, CPI, IsHoliday,
         Predicted_Sales, Historical_Avg, Confidence_Score, Model_Used)
    VALUES
        (@Store, @Dept, @Temperature, @FuelPrice, @CPI, @IsHoliday,
         @PredictedSales, @HistAvg, @Confidence, @ModelUsed)
END
GO

CREATE TRIGGER trg_Sales_PreventNegative
ON SalesTraining
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON
    IF EXISTS (SELECT 1 FROM inserted WHERE Weekly_Sales < 0)
    BEGIN
        RAISERROR('Negative Weekly_Sales not allowed.', 16, 1)
        RETURN
    END
    INSERT INTO SalesTraining (Store, Dept, Date, Weekly_Sales, IsHoliday)
    SELECT Store, Dept, Date, Weekly_Sales, IsHoliday
    FROM inserted
END
GO

CREATE TRIGGER trg_Sales_AfterUpdate
ON SalesTraining
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON
    INSERT INTO AuditLog (ActionType, TableName, RecordID, OldValue, NewValue)
    SELECT
        'UPDATE',
        'SalesTraining',
        i.SaleID,
        CAST(d.Weekly_Sales AS VARCHAR),
        CAST(i.Weekly_Sales AS VARCHAR)
    FROM inserted i
    JOIN deleted d ON i.SaleID = d.SaleID
END
GO