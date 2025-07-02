import multiprocessing as mp
from multiprocessing import Pool, Queue, Process
import threading
from typing import Iterator, List, Callable, Any, Optional, Tuple
import time
import psutil
import queue
from datetime import datetime
import logging
from tqdm import tqdm
import pandas as pd
from contextlib import contextmanager

from .models import Person, GenerationConfig


class PerformanceOptimizer:
    """High-performance data generation with multiprocessing and streaming"""
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Performance metrics
        self.start_time = None
        self.records_generated = 0
        self.bytes_generated = 0
        
        # System resources
        self.cpu_count = mp.cpu_count()
        self.memory_limit = psutil.virtual_memory().total * 0.8  # Use max 80% of RAM
        
    def generate_parallel(self, generator_func: Callable, 
                         total_records: int,
                         batch_size: Optional[int] = None,
                         num_processes: Optional[int] = None) -> Iterator[List[Person]]:
        """Generate records in parallel using multiprocessing"""
        if batch_size is None:
            batch_size = self.config.batch_size
        if num_processes is None:
            num_processes = min(self.config.num_threads, self.cpu_count)
        
        self.start_time = time.time()
        
        # Calculate batches per process
        records_per_process = total_records // num_processes
        remainder = total_records % num_processes
        
        # Create work items
        work_items = []
        start_idx = 0
        for i in range(num_processes):
            count = records_per_process + (1 if i < remainder else 0)
            if count > 0:
                work_items.append((start_idx, count, batch_size, i))
                start_idx += count
        
        # Progress tracking
        with tqdm(total=total_records, desc="Generating records") as pbar:
            with Pool(processes=num_processes) as pool:
                # Use imap_unordered for better performance
                results = pool.imap_unordered(
                    self._generate_batch_wrapper,
                    work_items,
                    chunksize=1
                )
                
                for batch in results:
                    self.records_generated += len(batch)
                    pbar.update(len(batch))
                    yield batch
        
        self._log_performance_stats()
    
    def stream_generate(self, generator_func: Callable,
                       rate_per_second: int,
                       duration_seconds: Optional[int] = None) -> Iterator[Person]:
        """Stream generation at specified rate"""
        interval = 1.0 / rate_per_second
        start_time = time.time()
        
        while True:
            if duration_seconds and (time.time() - start_time) > duration_seconds:
                break
            
            batch_start = time.time()
            
            # Generate one record
            record = generator_func()
            self.records_generated += 1
            yield record
            
            # Rate limiting
            elapsed = time.time() - batch_start
            if elapsed < interval:
                time.sleep(interval - elapsed)
    
    def generate_chunked(self, generator_func: Callable,
                        total_records: int,
                        chunk_size: int = 10000) -> Iterator[pd.DataFrame]:
        """Generate records in memory-efficient chunks as DataFrames"""
        remaining = total_records
        
        with tqdm(total=total_records, desc="Generating chunks") as pbar:
            while remaining > 0:
                current_chunk_size = min(chunk_size, remaining)
                chunk_data = []
                
                for _ in range(current_chunk_size):
                    record = generator_func()
                    # Convert to dict for DataFrame
                    chunk_data.append(self._person_to_dict(record))
                
                # Create DataFrame
                df = pd.DataFrame(chunk_data)
                
                remaining -= current_chunk_size
                self.records_generated += current_chunk_size
                pbar.update(current_chunk_size)
                
                yield df
    
    @contextmanager
    def memory_monitor(self, threshold_mb: int = 2000):
        """Monitor memory usage and yield control if threshold exceeded"""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        def check_memory():
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            used_memory = current_memory - initial_memory
            
            if used_memory > threshold_mb:
                self.logger.warning(f"Memory usage exceeded threshold: {used_memory:.2f} MB")
                return False
            return True
        
        yield check_memory
    
    def _generate_batch_wrapper(self, args: Tuple[int, int, int, int]) -> List[Person]:
        """Wrapper for multiprocessing batch generation"""
        start_idx, count, batch_size, process_id = args
        
        # Re-seed random in each process
        import random
        random.seed(self.config.seed + process_id if self.config.seed else None)
        
        # Import here to avoid pickling issues
        from ..generators.person_generator import PersonGenerator
        
        # Create generator for this process
        generator = PersonGenerator(self.config)
        
        batch = []
        for i in range(count):
            person = generator.generate_person()
            batch.append(person)
            
            # Yield batches to prevent memory buildup
            if len(batch) >= batch_size:
                yield_batch = batch
                batch = []
                return yield_batch
        
        return batch
    
    def _person_to_dict(self, person: Person) -> dict:
        """Convert Person object to flat dictionary for DataFrame"""
        # Base fields
        data = {
            'person_id': person.person_id,
            'ssn': person.ssn,
            'first_name': person.first_name,
            'middle_name': person.middle_name,
            'last_name': person.last_name,
            'suffix': person.suffix,
            'prefix': person.prefix,
            'nickname': person.nickname,
            'maiden_name': person.maiden_name,
            'date_of_birth': person.date_of_birth,
            'gender': person.gender,
            'created_at': person.created_at,
            'updated_at': person.updated_at
        }
        
        # Current address
        current_addr = next((a for a in person.addresses if a.address_type == "current"), None)
        if current_addr:
            data.update({
                'current_street_1': current_addr.street_1,
                'current_street_2': current_addr.street_2,
                'current_city': current_addr.city,
                'current_state': current_addr.state,
                'current_zip': current_addr.zip_code
            })
        
        # Primary phone
        primary_phone = next((p for p in person.phone_numbers if p.is_primary), None)
        if primary_phone:
            data['primary_phone'] = f"{primary_phone.area_code}{primary_phone.number}"
        
        # Primary email
        primary_email = next((e for e in person.email_addresses if e.is_primary), None)
        if primary_email:
            data['primary_email'] = primary_email.email
        
        # Current employment
        current_job = next((e for e in person.employment_history if e.is_current), None)
        if current_job:
            data.update({
                'current_employer': current_job.employer_name,
                'current_job_title': current_job.job_title,
                'current_salary': current_job.salary
            })
        
        # Financial profile
        if person.financial_profile:
            data.update({
                'credit_score': person.financial_profile.credit_score,
                'annual_income': person.financial_profile.annual_income,
                'debt_to_income_ratio': person.financial_profile.debt_to_income_ratio
            })
        
        return data
    
    def _log_performance_stats(self):
        """Log performance statistics"""
        if not self.start_time:
            return
        
        elapsed = time.time() - self.start_time
        rate = self.records_generated / elapsed if elapsed > 0 else 0
        
        self.logger.info(f"Performance Statistics:")
        self.logger.info(f"  Total records: {self.records_generated:,}")
        self.logger.info(f"  Time elapsed: {elapsed:.2f} seconds")
        self.logger.info(f"  Rate: {rate:.2f} records/second")
        self.logger.info(f"  Memory used: {psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB")


class StreamingBuffer:
    """Buffer for streaming data generation with backpressure"""
    
    def __init__(self, max_size: int = 10000):
        self.queue = queue.Queue(maxsize=max_size)
        self.producer_thread = None
        self.stop_event = threading.Event()
        
    def start_producer(self, generator_func: Callable, count: int):
        """Start producer thread"""
        self.producer_thread = threading.Thread(
            target=self._produce,
            args=(generator_func, count)
        )
        self.producer_thread.start()
    
    def _produce(self, generator_func: Callable, count: int):
        """Producer thread function"""
        for i in range(count):
            if self.stop_event.is_set():
                break
            
            record = generator_func()
            self.queue.put(record)
    
    def consume(self, batch_size: int = 1000) -> Iterator[List[Any]]:
        """Consume records in batches"""
        batch = []
        
        while True:
            try:
                # Get with timeout to check stop event
                record = self.queue.get(timeout=1.0)
                batch.append(record)
                
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
                    
            except queue.Empty:
                # Check if producer is done
                if self.producer_thread and not self.producer_thread.is_alive():
                    if batch:
                        yield batch
                    break
    
    def stop(self):
        """Stop producer"""
        self.stop_event.set()
        if self.producer_thread:
            self.producer_thread.join()


def estimate_memory_usage(num_records: int, avg_record_size: int = 2048) -> float:
    """Estimate memory usage for given number of records"""
    # Assume average record size of 2KB
    total_bytes = num_records * avg_record_size
    return total_bytes / 1024 / 1024  # Convert to MB


def optimize_batch_size(total_records: int, available_memory_mb: float,
                       num_processes: int = 4) -> int:
    """Calculate optimal batch size based on available memory"""
    # Reserve memory for each process
    memory_per_process = available_memory_mb / num_processes
    
    # Estimate record size (2KB average)
    avg_record_size_mb = 0.002
    
    # Calculate batch size (with safety margin)
    batch_size = int(memory_per_process * 0.7 / avg_record_size_mb)
    
    # Ensure reasonable bounds
    batch_size = max(100, min(batch_size, 50000))
    
    return batch_size