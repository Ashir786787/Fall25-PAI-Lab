# AI Stock Tracker Project

## Project Overview
This is a web-based Stock Price Tracker application developed for the 4th-semester Programming for AI Lab. The application allows users to search for various stocks, view their real-time market data, visualize price history through interactive charts, and get intelligent insights using AI.

## Key Features
- **Real-time Search**: Get instant details for top stocks like Apple, Google, Microsoft, and more.
- **Data Visualization**: Interactive price charts powered by Chart.js with support for different time periods (1 Month, 1 Year).
- **AI Insights**: Integrated Gemini AI to provide:
  - **Price Predictions**: Analysis of potential future trends.
  - **Market Analysis**: In-depth look at valuation and momentum.
  - **News Summaries**: Quick bullet points on recent developments.
  - **Investment Advice**: Basic guidance on whether to Buy, Hold, or Sell.
- **Favorites System**: Save your most tracked stocks locally in the browser.
- **Student-Friendly Design**: Simple, responsive UI built with Bootstrap for easy navigation.

## Technologies Used
- **Backend**: Python with Flask Framework
- **Frontend**: HTML5, CSS3 (Bootstrap), and JavaScript
- **AI Engine**: Google Gemini API (google-generativeai)
- **Data Plotting**: Chart.js for dynamic line graphs
- **Environment**: python-dotenv for secure API key management

## Project Structure
- `app.py`: Main Flask server handling all API routes and AI logic.
- `templates/index.html`: The frontend user interface.
- `.env`: (Optional) Store your `GEMINI_API_KEY` here for AI features.
- `requirements.txt`: List of Python libraries needed to run the project.

## How to Run the Project

1. **Install Python**: Ensure you have Python 3.10+ installed on your system.
2. **Install Dependencies**: Open your terminal and run:
   ```bash
   pip install -r requirements.txt
   ```
3. **Setup AI (Optional)**: If you want to use the AI features, add your Gemini API key to a `.env` file:
   ```
   GEMINI_API_KEY=your_key_here
   ```
   *If no key is provided, the app will automatically use smart mock responses.*
4. **Start the Server**:
   ```bash
   python app.py
   ```
5. **Access the App**: Open your browser and go to `http://127.0.0.1:5000`.

## Example Stocks to Try
- **AAPL** (Apple)
- **GOOGL** (Alphabet/Google)
- **MSFT** (Microsoft)
- **TSLA** (Tesla)
- **AMZN** (Amazon)

## Submission Details
- **Course**: Programming for AI (Lab)
- **Semester**: 4th Semester
- **Project Topic**: AI-Integrated Stock Market Tracking System