#!/usr/bin/env python3
"""Test script for the new generators"""

# Test just the new generators individually
from src.generators.travel_generator import TravelGenerator
from src.generators.financial_transactions_generator import FinancialTransactionsGenerator
from src.generators.communication_generator import CommunicationGenerator

print('Testing new generators individually...')

# Test travel generator
travel_gen = TravelGenerator()
travel_profile = travel_gen.generate_travel_profile(30, 50000, 'average')
print(f'✅ Travel generator: {travel_profile.total_trips} trips, {len(travel_profile.recent_travels)} recent')

# Test financial generator
financial_gen = FinancialTransactionsGenerator()
financial_profile = financial_gen.generate_financial_profile(30, 50000, 700, 'average')
print(f'✅ Financial generator: {len(financial_profile.bank_accounts)} accounts, net worth: ${financial_profile.net_worth:,.2f}')

# Test communication generator
comm_gen = CommunicationGenerator()
comm_profile = comm_gen.generate_communication_profile(30, 'Software Engineer', 'average', 'San Francisco, CA')
print(f'✅ Communication generator: {comm_profile.total_contacts} contacts, {len(comm_profile.communication_records)} records')

print('✅ All new generators working individually!')