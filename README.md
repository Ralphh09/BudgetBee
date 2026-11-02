# BudgetBee

BudgetBee is a personal finance tracker built with Python and Streamlit. It helps you keep track of your money in any currency of your choosing and see where it goes each month.

## Features
- Track earnings, savings, and expenses
- Set monthly spending limits by category
- Monitor savings goals
- View charts and monthly breakdowns
- Convert currencies using the ExchangeRate API

## Requirements
- Python 3.10+
- A free ExchangeRate API key

## Install locally

```bash
git clone https://github.com/Ralphh09/BudgetBee.git
cd BudgetBee
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Add your API key
Create a file named `.streamlit/secrets.toml` with the following:

```toml
EXCHANGE_API_KEY = "your_exchange_rate_api_key_here"
```

You can also set the same value as an environment variable:

```bash
export EXCHANGE_API_KEY="your_exchange_rate_api_key_here"
```

## Run the app

```bash
streamlit run budgetbee.py
```

The app will open in your browser.

## Deploy to Streamlit Cloud
1. Push this repo to GitHub
2. Go to https://share.streamlit.io
3. Connect your GitHub account
4. Select this repository
5. Set the app file to `budgetbee.py`
6. Add the secret value for `EXCHANGE_API_KEY` in Streamlit Cloud Secrets

## Notes
- The app stores user data locally in JSON files under a `data/<username>/` folder.
- Do not commit your real `.streamlit/secrets.toml` file to GitHub. Use `.streamlit/secrets.toml.example` as a template.
