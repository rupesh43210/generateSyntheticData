# PII Generator Web Interface

A modern, responsive web interface for the PII Generator that provides an intuitive way to generate synthetic personal data with various quality profiles.

## Features

### 🎨 Modern UI/UX
- Clean, professional design with gradient accents
- Responsive layout that works on desktop and mobile
- Real-time progress tracking during generation
- Interactive data preview with sortable tables

### 🔧 Generation Options
- **Data Quality Profiles**:
  - **Minimal**: Clean data with minimal errors (1% missing data, 0.5% typos)
  - **Realistic**: Production-like data (5% missing data, 2% typos)
  - **Messy**: Stress testing data (15% missing data, 5% typos)
  - **Extreme**: Chaos testing data (25% missing data, 10% typos)
- Configurable number of records (1 - 1,000,000)
- Multi-threading support (1-16 threads)
- Batch size configuration
- Family cluster generation option

### 📊 Real-time Statistics
- Total records generated
- Generation time and speed (records/second)
- Unique addresses and employers count
- Interactive statistics dashboard
- Data quality metrics

### 💾 Export Options
- **CSV Export**: Flattened format for easy analysis
- **JSON Export**: Full hierarchical data structure
- Download directly from browser

### 📈 Analytics Dashboard
- Gender distribution charts
- Age demographics
- Geographic distribution by state
- Employment statistics
- Financial metrics (credit scores, income)
- Data quality validation

## Quick Start

### Installation

1. Make sure you have the PII Generator installed:
```bash
pip install -r requirements.txt
```

2. Run the web application:
```bash
python web_app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

### Using the Interface

1. **Select Data Quality Profile**: Choose from the four pre-configured profiles based on your testing needs

2. **Configure Generation Settings**:
   - Number of records to generate
   - Number of threads (higher = faster generation)
   - Batch size for processing
   - Enable family clusters if needed

3. **Generate Data**: Click the "Generate Data" button and watch the real-time progress

4. **View Results**:
   - Preview the first 100 records in the data table
   - Check generation statistics
   - Switch to the Statistics tab for detailed analytics

5. **Export Data**:
   - Click "Export CSV" for a flattened format
   - Click "Export JSON" for the complete data structure

## Architecture

### Frontend
- Pure HTML/CSS/JavaScript (no framework dependencies)
- Responsive design using CSS Grid and Flexbox
- Font Awesome icons for better UX
- Inter font for modern typography

### Backend
- Flask web framework
- RESTful API endpoints
- Asynchronous task handling
- In-memory data storage for exports

### API Endpoints

- `GET /` - Main web interface
- `POST /api/generate` - Generate synthetic data
- `GET /api/export/<task_id>/<format>` - Export data (CSV/JSON)
- `GET /api/statistics/<task_id>` - Get detailed statistics
- `DELETE /api/cleanup/<task_id>` - Clean up stored data

## Performance

The web interface maintains the same high-performance characteristics as the CLI:

- 1M records in < 5 minutes
- Real-time progress tracking
- Memory-efficient streaming for large datasets
- Multi-threaded generation

## Customization

### Styling
Edit the embedded CSS in `templates/index.html` to customize:
- Color scheme (currently using purple gradients)
- Layout and spacing
- Font choices
- Animation effects

### Generation Profiles
Modify the profiles in `web_app.py` to adjust:
- Missing data rates
- Typo frequencies
- Duplicate rates
- Outlier percentages

### Data Fields
The interface currently shows key fields in the preview. To add more fields:
1. Update the table headers in `index.html`
2. Modify the data mapping in `web_app.py`
3. Add corresponding cells in the JavaScript

## Security Considerations

- The web app runs locally by default
- No authentication is implemented (add if deploying publicly)
- Generated data is stored temporarily in memory
- Data is automatically cleaned up after export

## Troubleshooting

### Port Already in Use
If port 5000 is occupied:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change port
```

### Memory Issues with Large Datasets
- Reduce batch size
- Generate data in smaller chunks
- Use the CLI for datasets > 10M records

### Browser Compatibility
The interface works best in modern browsers:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Future Enhancements

- [ ] Real-time streaming generation
- [ ] Database connection configuration UI
- [ ] Advanced filtering and search
- [ ] Data visualization with Chart.js
- [ ] Export to multiple database formats
- [ ] Save/load generation configurations
- [ ] Batch job scheduling
- [ ] API key authentication

## Screenshots

The interface features:
1. **Control Panel** - Easy configuration of all generation parameters
2. **Results Dashboard** - Real-time statistics and progress tracking
3. **Data Preview** - Instant preview of generated records
4. **Export Options** - One-click export to CSV or JSON

---

Built with ❤️ for data professionals who need a user-friendly interface for synthetic data generation.