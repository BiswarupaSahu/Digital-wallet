import requests
from config import Config

class CurrencyService:
    def __init__(self):
        self.api_key = Config.CURRENCY_API_KEY
        self.base_url = Config.CURRENCY_API_URL
    
    def convert_currency(self, amount: float, from_currency: str = 'INR', to_currency: str = 'USD') -> float:
        """Convert amount from one currency to another"""
        if from_currency == to_currency:
            return amount
        
        if not self.api_key:
            # Fallback rates if no API key is provided
            fallback_rates = {
                'USD': 0.012,  # 1 INR = 0.012 USD (approximate)
                'EUR': 0.011,  # 1 INR = 0.011 EUR (approximate)
                'GBP': 0.0095, # 1 INR = 0.0095 GBP (approximate)
            }
            
            if to_currency in fallback_rates:
                return round(amount * fallback_rates[to_currency], 2)
            else:
                raise ValueError(f"Currency {to_currency} not supported")
        
        try:
            # Make API request to get exchange rates
            params = {
                'apikey': self.api_key,
                'base_currency': from_currency,
                'currencies': to_currency
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data and to_currency in data['data']:
                exchange_rate = data['data'][to_currency]['value']
                converted_amount = amount * exchange_rate
                return round(converted_amount, 2)
            else:
                raise ValueError(f"Unable to get exchange rate for {to_currency}")
                
        except requests.RequestException as e:
            # Fallback to default rates if API fails
            fallback_rates = {
                'USD': 0.012,
                'EUR': 0.011,
                'GBP': 0.0095,
            }
            
            if to_currency in fallback_rates:
                return round(amount * fallback_rates[to_currency], 2)
            else:
                raise ValueError(f"Currency conversion failed: {str(e)}")

# Global instance
currency_service = CurrencyService()