CREATE INDEX idx_dimdate_full_date ON edw.DimDate (FullDate);
CREATE INDEX idx_dimdate_fiscal_year ON edw.DimDate (FiscalYear);

CREATE INDEX idx_factpayroll_employee ON edw.FactPayroll (EmployeeID);
CREATE INDEX idx_factpayroll_agency ON edw.FactPayroll (AgencyID);
CREATE INDEX idx_factpayroll_title ON edw.FactPayroll (TitleCode);
CREATE INDEX idx_factpayroll_fiscal_year ON edw.FactPayroll (FiscalYear);
