"""Data Validator Agent for quality assessment and validation."""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from weather_stock_dashboard.agents.base_agent import BaseWeatherStockAgent, BaseTool
from weather_stock_dashboard.models import WeatherData, StockData

logger = logging.getLogger(__name__)


class DataValidationTool(BaseTool):
    """Tool for data validation operations."""
    
    name: str = "data_validation"
    description: str = "Validate weather and stock data for quality and consistency"
    
    def _run(self, data_type: str, data: List[Dict[str, Any]]) -> str:
        """Run data validation."""
        try:
            validator = DataValidatorAgent("temp", "temp", "temp", "temp")
            if data_type == "weather":
                result = validator._validate_weather_data(data)
            elif data_type == "stock":
                result = validator._validate_stock_data(data)
            else:
                return f"Unknown data type: {data_type}"
            
            return f"Validation completed: {result['summary']}"
        except Exception as e:
            return f"Validation failed: {str(e)}"


class OutlierDetectionTool(BaseTool):
    """Tool for outlier detection."""
    
    name: str = "outlier_detection"
    description: str = "Detect outliers in time series data"
    
    def _run(self, data: List[float], method: str = "iqr") -> str:
        """Run outlier detection."""
        try:
            validator = DataValidatorAgent("temp", "temp", "temp", "temp")
            outliers = validator._detect_outliers(data, method)
            return f"Found {len(outliers)} outliers using {method} method"
        except Exception as e:
            return f"Outlier detection failed: {str(e)}"


class DataValidatorAgent(BaseWeatherStockAgent):
    """Agent for data quality assessment and validation."""
    
    def __init__(self):
        """Initialize Data Validator Agent."""
        super().__init__(
            name="data_validator",
            role="Data Quality Analyst",
            goal="Ensure data integrity and quality for weather and stock data",
            backstory="""You are an expert data quality analyst with extensive experience 
            in financial and meteorological data validation. You have a keen eye for 
            detecting anomalies, inconsistencies, and data quality issues that could 
            impact analysis results."""
        )
        self.validation_thresholds = {
            "weather": {
                "temperature": {"min": -100, "max": 60},
                "humidity": {"min": 0, "max": 100},
                "pressure": {"min": 800, "max": 1200},
                "precipitation": {"min": 0, "max": 1000},
                "wind_speed": {"min": 0, "max": 200}
            },
            "stock": {
                "price": {"min": 0.01, "max": 100000},
                "volume": {"min": 0, "max": 1e12},
                "change_percent": {"min": -100, "max": 1000}
            }
        }
    
    def get_tools(self) -> List[BaseTool]:
        """Get tools for data validation."""
        return [
            DataValidationTool(),
            OutlierDetectionTool()
        ]
    
    async def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data validation task."""
        try:
            task_type = context.get("task_type", "validate")
            data_type = context.get("data_type", "weather")
            data = context.get("data", [])
            
            if task_type == "validate":
                if data_type == "weather":
                    result = self._validate_weather_data(data)
                elif data_type == "stock":
                    result = self._validate_stock_data(data)
                else:
                    raise ValueError(f"Unknown data type: {data_type}")
            
            elif task_type == "outlier_detection":
                values = context.get("values", [])
                method = context.get("method", "iqr")
                outliers = self._detect_outliers(values, method)
                result = {
                    "outliers": outliers,
                    "outlier_count": len(outliers),
                    "method": method,
                    "summary": f"Detected {len(outliers)} outliers using {method} method"
                }
            
            elif task_type == "completeness_check":
                result = self._check_data_completeness(data, data_type)
            
            elif task_type == "consistency_check":
                result = self._check_data_consistency(data, data_type)
            
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # Update agent memory
            self.update_memory(f"last_{task_type}_result", result)
            
            return {
                "agent": self.name,
                "task": task_description,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": result.get("summary", "Task completed successfully")
            }
            
        except Exception as e:
            logger.error(f"Data validation task failed: {e}")
            return {
                "agent": self.name,
                "task": task_description,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "summary": f"Task failed: {str(e)}"
            }
    
    def _validate_weather_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate weather data quality."""
        if not data:
            return {"valid": False, "summary": "No data provided", "issues": ["Empty dataset"]}
        
        issues = []
        valid_count = 0
        total_count = len(data)
        
        for i, item in enumerate(data):
            item_issues = []
            
            try:
                # Try to create WeatherData model to validate
                weather_data = WeatherData(**item)
                valid_count += 1
            except Exception as e:
                item_issues.append(f"Model validation failed: {str(e)}")
            
            # Additional custom validations
            if "timestamp" in item:
                try:
                    timestamp = pd.to_datetime(item["timestamp"])
                    # Check if timestamp is reasonable (not too far in future/past)
                    now = datetime.utcnow()
                    if timestamp > now + timedelta(days=7):
                        item_issues.append("Timestamp too far in future")
                    elif timestamp < now - timedelta(days=365*10):
                        item_issues.append("Timestamp too far in past")
                except Exception:
                    item_issues.append("Invalid timestamp format")
            
            # Check for missing required fields
            required_fields = ["temperature", "humidity", "pressure", "location"]
            for field in required_fields:
                if field not in item or item[field] is None:
                    item_issues.append(f"Missing required field: {field}")
            
            if item_issues:
                issues.append(f"Item {i}: {'; '.join(item_issues)}")
        
        # Check for duplicates
        if len(data) > 1:
            df = pd.DataFrame(data)
            if "timestamp" in df.columns and "location" in df.columns:
                duplicates = df.duplicated(subset=["timestamp", "location"]).sum()
                if duplicates > 0:
                    issues.append(f"Found {duplicates} duplicate records")
        
        validity_rate = valid_count / total_count if total_count > 0 else 0
        
        return {
            "valid": len(issues) == 0,
            "total_records": total_count,
            "valid_records": valid_count,
            "validity_rate": validity_rate,
            "issues": issues,
            "summary": f"Validated {total_count} weather records: {valid_count} valid ({validity_rate:.1%}), {len(issues)} issues found"
        }
    
    def _validate_stock_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate stock data quality."""
        if not data:
            return {"valid": False, "summary": "No data provided", "issues": ["Empty dataset"]}
        
        issues = []
        valid_count = 0
        total_count = len(data)
        
        for i, item in enumerate(data):
            item_issues = []
            
            try:
                # Try to create StockData model to validate
                stock_data = StockData(**item)
                valid_count += 1
            except Exception as e:
                item_issues.append(f"Model validation failed: {str(e)}")
            
            # Additional custom validations
            if "timestamp" in item:
                try:
                    timestamp = pd.to_datetime(item["timestamp"])
                    # Check if timestamp is reasonable
                    now = datetime.utcnow()
                    if timestamp > now + timedelta(days=1):
                        item_issues.append("Timestamp in future")
                    elif timestamp < now - timedelta(days=365*20):
                        item_issues.append("Timestamp too old")
                except Exception:
                    item_issues.append("Invalid timestamp format")
            
            # Check for missing required fields
            required_fields = ["symbol", "price", "volume"]
            for field in required_fields:
                if field not in item or item[field] is None:
                    item_issues.append(f"Missing required field: {field}")
            
            # Check for suspicious values
            if "price" in item and item["price"] is not None:
                if item["price"] <= 0:
                    item_issues.append("Non-positive price")
                elif item["price"] > 50000:  # Suspicious high price
                    item_issues.append("Suspiciously high price")
            
            if "volume" in item and item["volume"] is not None:
                if item["volume"] < 0:
                    item_issues.append("Negative volume")
            
            if item_issues:
                issues.append(f"Item {i}: {'; '.join(item_issues)}")
        
        # Check for duplicates
        if len(data) > 1:
            df = pd.DataFrame(data)
            if "timestamp" in df.columns and "symbol" in df.columns:
                duplicates = df.duplicated(subset=["timestamp", "symbol"]).sum()
                if duplicates > 0:
                    issues.append(f"Found {duplicates} duplicate records")
        
        validity_rate = valid_count / total_count if total_count > 0 else 0
        
        return {
            "valid": len(issues) == 0,
            "total_records": total_count,
            "valid_records": valid_count,
            "validity_rate": validity_rate,
            "issues": issues,
            "summary": f"Validated {total_count} stock records: {valid_count} valid ({validity_rate:.1%}), {len(issues)} issues found"
        }
    
    def _detect_outliers(self, values: List[float], method: str = "iqr") -> List[int]:
        """Detect outliers in numerical data."""
        if not values or len(values) < 4:
            return []
        
        values_array = np.array(values)
        outlier_indices = []
        
        if method == "iqr":
            Q1 = np.percentile(values_array, 25)
            Q3 = np.percentile(values_array, 75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_indices = np.where(
                (values_array < lower_bound) | (values_array > upper_bound)
            )[0].tolist()
        
        elif method == "zscore":
            mean = np.mean(values_array)
            std = np.std(values_array)
            if std > 0:
                z_scores = np.abs((values_array - mean) / std)
                outlier_indices = np.where(z_scores > 3)[0].tolist()
        
        elif method == "modified_zscore":
            median = np.median(values_array)
            mad = np.median(np.abs(values_array - median))
            if mad > 0:
                modified_z_scores = 0.6745 * (values_array - median) / mad
                outlier_indices = np.where(np.abs(modified_z_scores) > 3.5)[0].tolist()
        
        return outlier_indices
    
    def _check_data_completeness(self, data: List[Dict[str, Any]], data_type: str) -> Dict[str, Any]:
        """Check data completeness."""
        if not data:
            return {"complete": False, "summary": "No data provided"}
        
        df = pd.DataFrame(data)
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        completeness_rate = (total_cells - missing_cells) / total_cells if total_cells > 0 else 0
        
        # Check for missing values by column
        missing_by_column = df.isnull().sum().to_dict()
        missing_columns = {col: count for col, count in missing_by_column.items() if count > 0}
        
        return {
            "complete": missing_cells == 0,
            "total_cells": total_cells,
            "missing_cells": missing_cells,
            "completeness_rate": completeness_rate,
            "missing_by_column": missing_columns,
            "summary": f"Data completeness: {completeness_rate:.1%} ({missing_cells} missing out of {total_cells} cells)"
        }
    
    def _check_data_consistency(self, data: List[Dict[str, Any]], data_type: str) -> Dict[str, Any]:
        """Check data consistency."""
        if not data:
            return {"consistent": False, "summary": "No data provided"}
        
        issues = []
        df = pd.DataFrame(data)
        
        # Check timestamp consistency
        if "timestamp" in df.columns:
            try:
                timestamps = pd.to_datetime(df["timestamp"])
                
                # Check for chronological order
                if not timestamps.is_monotonic_increasing:
                    issues.append("Timestamps not in chronological order")
                
                # Check for reasonable time gaps
                if len(timestamps) > 1:
                    time_diffs = timestamps.diff().dropna()
                    if data_type == "stock":
                        # Stock data should have reasonable intervals
                        max_gap = pd.Timedelta(days=7)  # Max 1 week gap
                        large_gaps = (time_diffs > max_gap).sum()
                        if large_gaps > 0:
                            issues.append(f"Found {large_gaps} large time gaps (>1 week)")
                    
            except Exception as e:
                issues.append(f"Timestamp consistency check failed: {str(e)}")
        
        # Check value consistency
        if data_type == "weather" and "temperature" in df.columns:
            temp_changes = df["temperature"].diff().abs()
            extreme_changes = (temp_changes > 20).sum()  # >20°C change
            if extreme_changes > 0:
                issues.append(f"Found {extreme_changes} extreme temperature changes")
        
        elif data_type == "stock" and "price" in df.columns:
            price_changes = df["price"].pct_change().abs()
            extreme_changes = (price_changes > 0.5).sum()  # >50% change
            if extreme_changes > 0:
                issues.append(f"Found {extreme_changes} extreme price changes")
        
        return {
            "consistent": len(issues) == 0,
            "issues": issues,
            "summary": f"Data consistency check: {'Passed' if len(issues) == 0 else f'{len(issues)} issues found'}"
        }