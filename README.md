# NontoxicGoods.com

A searchable, filterable static website for discovering non-toxic products. This site loads product data from a CSV file, allowing for easy updates and maintenance.

## 🌿 About

NontoxicGoods.com is a curated collection of non-toxic products spanning categories like Personal Care, Kitchen, Cleaning, and more.

## ✨ Features

- **Responsive Design** - Mobile-first approach that works on all devices
- **Dark/Light Mode** - Automatic theme detection with manual toggle
- **Search Functionality** - Filter products by keyword across all fields
- **Category & Origin Filters** - Interactive filter chips for product categories and countries
- **Real-time Filtering** - Results update instantly as filters are applied
- **Clean UI** - Soft, calming aesthetic with warm neutrals
- **CSV-Powered** - Easy data updates via a simple CSV file

## 🛠️ Setup & Installation

1. **Clone the repository**
   ```
   git clone https://github.com/ruthmade/nontoxicgoods.com.git
   cd nontoxicgoods.com
   ```

2. **Create your product data**
   - Use the provided `products.csv` template or create your own
   - Follow the CSV format outlined below

3. **Test locally**
   - Open `index.html` in your browser, or
   - Use a local server: `python -m http.server` or `npx serve`

## 📊 CSV Data Format

Create a file named `products.csv` in the root directory with the following columns:

| Column | Description |
|--------|-------------|
| `Title` | Name of the product |
| `Brand` | Brand or manufacturer |
| `Notes` | Short description or notes about the product |
| `Made In` | Country of origin |
| `Category` | Product category (e.g., Personal Care, Kitchen, Cleaning) |
| `Link` | URL to the product |

Example:
```csv
Title,Brand,Notes,Made In,Category,Link
Natural Deodorant,EcoRoot,Aluminum-free with essential oils,USA,Personal Care,https://example.com/product1
Bamboo Cutting Board,GreenKitchen,Sustainable and antimicrobial,Canada,Kitchen,https://example.com/product2
```

## 🚀 Deployment

### GitHub Pages

1. Push your code to GitHub
2. Go to your repository settings
3. Under "GitHub Pages", select your branch (usually `main`)
4. Wait for the deployment to complete

### Other Hosting Options

The site is a static HTML/CSS/JS application and can be hosted on any static site hosting service:

- Netlify
- Vercel
- AWS S3
- Firebase Hosting

## 🎨 Customization

### Styling

The site uses CSS variables for easy customization. The main variables are defined at the top of the CSS section:

```css
:root {
    /* Light Theme (default) */
    --background: #f9f5f1;
    --background-card: #ffffff;
    --text-primary: #3e3a39;
    --text-secondary: #5a5655;
    --accent: #d8b3a5;
    --accent-light: #e8d1c9;
    --border: #e6e0dc;
    --shadow: rgba(0, 0, 0, 0.05);
    
    /* Common variables */
    --border-radius: 8px;
    --container-max-width: 1200px;
    --header-font: 'Playfair Display', serif;
    --body-font: 'Lora', serif;
    --ui-font: 'DM Sans', sans-serif;
    /* ... */
}
```

### Adding Categories

To add new product categories, simply include them in your CSV data. The site will automatically generate filter chips for any new categories.

### Category Colors

Product cards are color-coded by category. To customize or add colors for new categories, modify this section in the CSS:

```css
/* Category colors */
.product-card[data-category="Personal Care"] {
    border-left: 4px solid #e6a4b4;
}

.product-card[data-category="Kitchen"] {
    border-left: 4px solid #b6d7a8;
}

/* Add more categories as needed */
```

## 🧠 How It Works

1. The site loads the CSV data using PapaParse
2. The CSV is converted to JSON for easy processing
3. Filter chips are generated from unique categories and countries
4. The search input and filter chips update the filtering criteria
5. Products are filtered in real-time based on user selections
6. The product grid displays only matching products

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Acknowledgements

- [PapaParse](https://www.papaparse.com/) for CSV parsing
- Google Fonts for [Playfair Display](https://fonts.google.com/specimen/Playfair+Display), [Lora](https://fonts.google.com/specimen/Lora), and [DM Sans](https://fonts.google.com/specimen/DM+Sans)