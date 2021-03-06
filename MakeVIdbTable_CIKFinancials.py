#!/usr/bin/env python
#
# Create the database tables needed for the VI web site.
#
import psycopg2

conn = psycopg2.connect(database="stocks_us", user="postgres", password="v3gBdD#VI")
cur = conn.cursor()

cur.execute("SET statement_timeout = 0;")
# cur.execute("SET lock_timeout = 0;")
cur.execute("SET client_encoding = 'UTF8';")
cur.execute("SET standard_conforming_strings = off;")
cur.execute("SET check_function_bodies = false;")
cur.execute("SET client_min_messages = warning;")
cur.execute("SET escape_string_warning = off;")

#
# Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: -; Owner: postgres
#
cur.execute("CREATE OR REPLACE PROCEDURAL LANGUAGE plpgsql;")


cur.execute("ALTER PROCEDURAL LANGUAGE plpgsql OWNER TO postgres;")

cur.execute("SET search_path = public, pg_catalog;")

cur.execute("SET default_tablespace = '';")

cur.execute("SET default_with_oids = false;")

cur.execute('DROP TABLE cik_financials')

#
# Name: cik_financials; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
#
cur.execute('CREATE TABLE cik_financials (cik integer NOT NULL, \
    "SalesRevenueNet" integer, \
    "CostOfGoodsAndServicesSold" integer, \
    "GrossProfit" integer, \
    "ResearchAndDevelopmentExpense" integer, \
    "SellingGeneralAndAdministrativeExpense" integer, \
    "OperatingExpenses" integer, \
    "OperatingIncomeLoss" integer, \
    "NonoperatingIncomeExpense" integer, \
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest" integer, \
    "IncomeTaxExpenseBenefit" integer, \
    "NetIncomeLoss" integer, \
    "EarningsPerShareBasic" money, \
    "EarningsPerShareDiluted" money, \
    "WeightedAverageNumberOfSharesOutstandingBasic" integer, \
    "WeightedAverageNumberOfDilutedSharesOutstanding" integer, \
    "CommonStockDividendsPerShareDeclared" money, \
    "OtherComprehensiveIncomeLossNetOfTax" integer, \
    "ComprehensiveIncomeNetOfTax" integer, \
    "CashAndCashEquivalentsAtCarryingValue" integer, \
    "AvailableForSaleSecuritiesCurrent" integer, \
    "AccountsReceivableNetCurrent" integer, \
    "InventoryNet" integer, \
    "DeferredTaxAssetsLiabilitiesNetCurrent" integer, \
    "NontradeReceivablesCurrent" integer, \
    "AssetsCurrent" integer, \
    "AvailableForSaleSecuritiesNoncurrent" integer, \
    "PropertyPlantAndEquipmentNet" integer, \
    "Goodwill" integer, \
    "IntangibleAssetsNetExcludingGoodwill" integer, \
    "OtherAssetsNoncurrent" integer, \
    "Assets" integer, \
    "AccountsPayableCurrent" integer, \
    "AccruedLiabilitiesCurrent" integer, \
    "DeferredRevenueCurrent" integer, \
    "CommercialPaper" integer, \
    "LongTermDebtCurrent" integer, \
    "LiabilitiesCurrent" integer, \
    "DeferredRevenueNoncurrent" integer, \
    "LongTermDebtNoncurrent" integer, \
    "OtherLiabilitiesNoncurrent" integer, \
    "Liabilities" integer, \
    "CommonStocksIncludingAdditionalPaidInCapital" integer, \
    "RetainedEarningsAccumulatedDeficit" integer, \
    "AccumulatedOtherComprehensiveIncomeLossNetOfTax" integer, \
    "StockholdersEquity" integer, \
    "LiabilitiesAndStockholdersEquity" integer, \
    "DepreciationAmortizationAndAccretionNet" integer, \
    "ShareBasedCompensation" integer, \
    "DeferredIncomeTaxExpenseBenefit" integer, \
    "IncreaseDecreaseInAccountsReceivable" integer, \
    "IncreaseDecreaseInInventories" integer, \
    "IncreaseDecreaseInOtherOperatingAssets" integer, \
    "IncreaseDecreaseInAccountsPayable" integer, \
    "IncreaseDecreaseInDeferredRevenue" integer, \
    "IncreaseDecreaseInOtherOperatingLiabilities" integer, \
    "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations" integer, \
    "PaymentsToAcquireAvailableForSaleSecurities" integer, \
    "ProceedsFromMaturitiesPrepaymentsAndCallsOfAvailableForSaleSecurities" integer, \
    "ProceedsFromSaleOfAvailableForSaleSecurities" integer, \
    "PaymentsToAcquireBusinessesNetOfCashAcquired" integer, \
    "PaymentsToAcquirePropertyPlantAndEquipment" integer, \
    "PaymentsToAcquireIntangibleAssets" integer, \
    "PaymentsForProceedsFromOtherInvestingActivities" integer, \
    "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations" integer, \
    "ProceedsFromIssuanceOfCommonStock" integer, \
    "ExcessTaxBenefitFromShareBasedCompensationFinancingActivities" integer, \
    "PaymentsRelatedToTaxWithholdingForShareBasedCompensation" integer, \
    "PaymentsForRepurchaseOfCommonStock" integer, \
    "ProceedsFromIssuanceOfLongTermDebt" integer, \
    "ProceedsFromRepaymentsOfCommercialPaper" integer, \
    "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations" integer, \
    "CashAndCashEquivalentsPeriodIncreaseDecrease" integer \
    )');


# Shown in AAPL statement, but not GAAP:
#   <aapl:IncreaseDecreaseInNonTradeReceivables contextRef="eol_PE2035----1510-K0012_STD_364_20150926_0" unitRef="iso4217_USD" decimals="-6" id="id_5290686_88BDB078-95B3-493E-8A8D-33F52EB05AD7_1_10">3735000000</aapl:IncreaseDecreaseInNonTradeReceivables>
#   <aapl:PaymentsOfDividendsAndDividendEquivalentsOnCommonStockAndRestrictedStockUnits contextRef="eol_PE2035----1510-K0012_STD_364_20150926_0" unitRef="iso4217_USD" decimals="-6" id="id_5290686_88BDB078-95B3-493E-8A8D-33F52EB05AD7_1_29">11561000000</aapl:PaymentsOfDividendsAndDividendEquivalentsOnCommonStockAndRestrictedStockUnits>

cur.execute('ALTER TABLE public.cik_financials OWNER TO postgres;')

cur.execute("COMMENT ON COLUMN cik_financials.\"CommonStockDividendsPerShareDeclared\" IS 'last column of income statement';")
cur.execute("COMMENT ON COLUMN cik_financials.\"OtherComprehensiveIncomeLossNetOfTax\" IS 'first column of balance sheet';")
cur.execute("COMMENT ON COLUMN cik_financials.\"AvailableForSaleSecuritiesCurrent\" IS 'Short-term marketable securities';")
cur.execute("COMMENT ON COLUMN cik_financials.\"AccountsReceivableNetCurrent\" IS 'Accounts receivable';")
cur.execute("COMMENT ON COLUMN cik_financials.\"InventoryNet\" IS 'Inventory';")
cur.execute("COMMENT ON COLUMN cik_financials.\"AssetsCurrent\" IS 'Total current assets';")
cur.execute("COMMENT ON COLUMN cik_financials.\"AvailableForSaleSecuritiesNoncurrent\" IS 'Long-term marketable securities';")
cur.execute("COMMENT ON COLUMN cik_financials.\"PropertyPlantAndEquipmentNet\" IS 'Property, plant and equipment, net';")
cur.execute("COMMENT ON COLUMN cik_financials.\"OtherAssetsNoncurrent\" IS 'Other Assets';")
cur.execute("COMMENT ON COLUMN cik_financials.\"Assets\" IS 'Total assets';")
cur.execute("COMMENT ON COLUMN cik_financials.\"LongTermDebtCurrent\" IS 'Current portion of long-term debt';")
cur.execute("COMMENT ON COLUMN cik_financials.\"Liabilities\" IS 'Total liabilities';")
cur.execute("COMMENT ON COLUMN cik_financials.\"LiabilitiesAndStockholdersEquity\" IS 'Total liabilities and shareholders’ equity--last entry in balance sheet';")
cur.execute("COMMENT ON COLUMN cik_financials.\"DepreciationAmortizationAndAccretionNet\" IS 'first column of cash flow statement';")
cur.execute("COMMENT ON COLUMN cik_financials.\"IncreaseDecreaseInAccountsReceivable\" IS 'Accounts receivable, net';")
cur.execute("COMMENT ON COLUMN cik_financials.\"IncreaseDecreaseInOtherOperatingAssets\" IS 'Other current and non-current assets';")
cur.execute("COMMENT ON COLUMN cik_financials.\"NetCashProvidedByUsedInOperatingActivitiesContinuingOperations\" IS 'Last entry for operating activities';")
cur.execute("COMMENT ON COLUMN cik_financials.\"PaymentsToAcquireAvailableForSaleSecurities\" IS 'First entry for investing activities';")
cur.execute("COMMENT ON COLUMN cik_financials.\"NetCashProvidedByUsedInInvestingActivitiesContinuingOperations\" IS 'Last entry for investing activities';")
cur.execute("COMMENT ON COLUMN cik_financials.\"ProceedsFromIssuanceOfCommonStock\" IS 'First entry for financing activities';")


# TODO: what good is this? Why does pgdump emit it?
cur.execute("CREATE SEQUENCE cik_financials_cik_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;")
cur.execute("ALTER TABLE public.cik_financials_cik_seq OWNER TO postgres;")
cur.execute("ALTER SEQUENCE cik_financials_cik_seq OWNED BY cik_financials.cik;")

# cur.execute("CREATE TABLE ticker_cik ( ticker character varying(8) NOT NULL, cik integer);")
# cur.execute("ALTER TABLE public.ticker_cik OWNER TO postgres;")

cur.execute("ALTER TABLE ONLY cik_financials ADD CONSTRAINT cik_financials_pkey PRIMARY KEY (cik);")
# cur.execute("ALTER TABLE ONLY cik_form10xml ADD CONSTRAINT cik_form10xml_pkey PRIMARY KEY (accession);")
# cur.execute("ALTER TABLE ONLY ticker_cik ADD CONSTRAINT ticker_cik_pkey PRIMARY KEY (ticker);")
# cur.execute("ALTER TABLE ONLY ticker_cik ADD CONSTRAINT unique_cik UNIQUE (cik);")

# Commit all these commands
#
conn.commit()

# Close up shop
#
cur.close()
conn.close()

