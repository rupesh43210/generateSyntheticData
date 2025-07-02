"""
Advanced error handling and recovery mechanisms for PII generation
"""

import logging
import traceback
import time
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum
import json

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    VALIDATION = "validation"
    GENERATION = "generation"
    SERIALIZATION = "serialization"
    PERFORMANCE = "performance"
    SYSTEM = "system"

@dataclass
class ErrorContext:
    """Context information for errors"""
    error_id: str
    timestamp: float
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    traceback: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    retry_count: int = 0

class RecoveryStrategy:
    """Base class for error recovery strategies"""
    
    def can_recover(self, error_context: ErrorContext) -> bool:
        """Check if this strategy can handle the error"""
        raise NotImplementedError
    
    def recover(self, error_context: ErrorContext, *args, **kwargs) -> bool:
        """Attempt to recover from the error"""
        raise NotImplementedError

class RetryStrategy(RecoveryStrategy):
    """Retry strategy for transient errors"""
    
    def __init__(self, max_retries: int = 3, backoff_multiplier: float = 1.5):
        self.max_retries = max_retries
        self.backoff_multiplier = backoff_multiplier
    
    def can_recover(self, error_context: ErrorContext) -> bool:
        return (error_context.retry_count < self.max_retries and 
                error_context.category in [ErrorCategory.GENERATION, ErrorCategory.SYSTEM])
    
    def recover(self, error_context: ErrorContext, func: Callable, *args, **kwargs) -> bool:
        """Retry the failed operation with exponential backoff"""
        if not self.can_recover(error_context):
            return False
        
        wait_time = (self.backoff_multiplier ** error_context.retry_count)
        time.sleep(wait_time)
        
        try:
            result = func(*args, **kwargs)
            error_context.recovery_successful = True
            return True
        except Exception as e:
            error_context.retry_count += 1
            error_context.message = f"Retry {error_context.retry_count} failed: {str(e)}"
            return False

class ValidationRecoveryStrategy(RecoveryStrategy):
    """Recovery strategy for validation errors"""
    
    def can_recover(self, error_context: ErrorContext) -> bool:
        return error_context.category == ErrorCategory.VALIDATION
    
    def recover(self, error_context: ErrorContext, fallback_data: Dict[str, Any]) -> bool:
        """Use fallback data for validation errors"""
        try:
            # Apply default values for missing or invalid fields
            if error_context.context_data:
                error_context.context_data.update(fallback_data)
            error_context.recovery_successful = True
            return True
        except Exception:
            return False

class PerformanceRecoveryStrategy(RecoveryStrategy):
    """Recovery strategy for performance issues"""
    
    def can_recover(self, error_context: ErrorContext) -> bool:
        return error_context.category == ErrorCategory.PERFORMANCE
    
    def recover(self, error_context: ErrorContext, reduce_batch_size: bool = True) -> bool:
        """Reduce workload to address performance issues"""
        try:
            if reduce_batch_size and error_context.context_data:
                current_batch_size = error_context.context_data.get('batch_size', 1000)
                new_batch_size = max(10, current_batch_size // 2)
                error_context.context_data['batch_size'] = new_batch_size
                
                current_threads = error_context.context_data.get('num_threads', 4)
                new_threads = max(1, current_threads - 1)
                error_context.context_data['num_threads'] = new_threads
            
            error_context.recovery_successful = True
            return True
        except Exception:
            return False

class RobustErrorHandler:
    """Advanced error handling system with recovery mechanisms"""
    
    def __init__(self):
        self.error_log: List[ErrorContext] = []
        self.recovery_strategies: List[RecoveryStrategy] = [
            RetryStrategy(),
            ValidationRecoveryStrategy(),
            PerformanceRecoveryStrategy()
        ]
        self.logger = logging.getLogger(__name__)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def handle_error(self, 
                    exception: Exception,
                    category: ErrorCategory,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    context_data: Optional[Dict[str, Any]] = None,
                    recovery_func: Optional[Callable] = None,
                    recovery_args: tuple = (),
                    recovery_kwargs: dict = None) -> ErrorContext:
        """Handle an error with automatic recovery attempts"""
        
        if recovery_kwargs is None:
            recovery_kwargs = {}
        
        error_context = ErrorContext(
            error_id=f"err_{int(time.time() * 1000)}_{len(self.error_log)}",
            timestamp=time.time(),
            severity=severity,
            category=category,
            message=str(exception),
            traceback=traceback.format_exc(),
            context_data=context_data or {}
        )
        
        self.error_log.append(error_context)
        
        # Log the error
        self.logger.error(f"Error {error_context.error_id}: {error_context.message}")
        
        # Attempt recovery
        if recovery_func:
            self._attempt_recovery(error_context, recovery_func, recovery_args, recovery_kwargs)
        
        return error_context
    
    def _attempt_recovery(self, 
                         error_context: ErrorContext,
                         recovery_func: Callable,
                         recovery_args: tuple,
                         recovery_kwargs: dict) -> bool:
        """Attempt recovery using available strategies"""
        
        for strategy in self.recovery_strategies:
            if strategy.can_recover(error_context):
                error_context.recovery_attempted = True
                
                try:
                    if isinstance(strategy, RetryStrategy):
                        success = strategy.recover(error_context, recovery_func, *recovery_args, **recovery_kwargs)
                    else:
                        success = strategy.recover(error_context, **recovery_kwargs)
                    
                    if success:
                        self.logger.info(f"Recovery successful for error {error_context.error_id} using {strategy.__class__.__name__}")
                        return True
                        
                except Exception as recovery_error:
                    self.logger.warning(f"Recovery attempt failed for error {error_context.error_id}: {recovery_error}")
        
        self.logger.error(f"All recovery attempts failed for error {error_context.error_id}")
        return False
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors encountered"""
        if not self.error_log:
            return {"total_errors": 0, "summary": "No errors recorded"}
        
        summary = {
            "total_errors": len(self.error_log),
            "by_severity": {},
            "by_category": {},
            "recovery_rate": 0,
            "recent_errors": []
        }
        
        recovered_count = 0
        for error in self.error_log:
            # Count by severity
            severity_key = error.severity.value
            summary["by_severity"][severity_key] = summary["by_severity"].get(severity_key, 0) + 1
            
            # Count by category
            category_key = error.category.value
            summary["by_category"][category_key] = summary["by_category"].get(category_key, 0) + 1
            
            # Count recoveries
            if error.recovery_successful:
                recovered_count += 1
        
        summary["recovery_rate"] = recovered_count / len(self.error_log) * 100
        
        # Recent errors (last 10)
        recent_errors = self.error_log[-10:] if len(self.error_log) > 10 else self.error_log
        summary["recent_errors"] = [
            {
                "error_id": error.error_id,
                "timestamp": error.timestamp,
                "severity": error.severity.value,
                "category": error.category.value,
                "message": error.message[:100] + "..." if len(error.message) > 100 else error.message,
                "recovered": error.recovery_successful
            }
            for error in recent_errors
        ]
        
        return summary
    
    def clear_error_log(self):
        """Clear the error log"""
        self.error_log.clear()
        self.logger.info("Error log cleared")
    
    def export_error_log(self, filename: str):
        """Export error log to JSON file"""
        try:
            error_data = []
            for error in self.error_log:
                error_dict = {
                    "error_id": error.error_id,
                    "timestamp": error.timestamp,
                    "severity": error.severity.value,
                    "category": error.category.value,
                    "message": error.message,
                    "traceback": error.traceback,
                    "context_data": error.context_data,
                    "recovery_attempted": error.recovery_attempted,
                    "recovery_successful": error.recovery_successful,
                    "retry_count": error.retry_count
                }
                error_data.append(error_dict)
            
            with open(filename, 'w') as f:
                json.dump(error_data, f, indent=2)
            
            self.logger.info(f"Error log exported to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to export error log: {e}")

# Global error handler instance
error_handler = RobustErrorHandler()