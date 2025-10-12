# Mintly Frontend - React Application

Modern React frontend for the Mintly Personal Budgeting App.

## Tech Stack

- **React 18** - UI library
- **React Router** - Navigation
- **Axios** - HTTP client  
- **Recharts** - Chart visualizations
- **Vite** - Build tool
- **date-fns** - Date utilities

## Features

- 📤 **Upload Page** - Drag-and-drop CSV file upload
- 📊 **Transactions** - View, edit, split, and delete transactions
- 📈 **Reports** - Interactive charts and spending summaries
- 🎨 **Modern UI** - Clean, responsive design
- ⚡ **Fast** - Built with Vite for instant HMR

## Development

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Opens at http://localhost:3000

The development server proxies API requests to the Python backend at http://localhost:8000

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Upload.jsx          # CSV upload page
│   │   ├── Transactions.jsx    # Transaction management
│   │   ├── Reports.jsx         # Charts and reports
│   │   └── SplitModal.jsx      # Transaction split modal
│   ├── services/
│   │   └── api.js              # API client
│   ├── App.jsx                 # Main app component
│   ├── App.css                 # App styles
│   ├── main.jsx                # Entry point
│   └── index.css               # Global styles
├── public/                     # Static assets
├── index.html                  # HTML template
├── vite.config.js              # Vite configuration
├── package.json                # Dependencies
├── Dockerfile                  # Docker image
└── README.md                   # This file
```

## API Integration

The frontend communicates with the Python FastAPI backend through RESTful APIs:

### Endpoints Used

- `POST /api/transactions/upload` - Upload CSV
- `GET /api/transactions/list` - List transactions
- `PUT /api/transactions/{id}/category` - Update category
- `POST /api/transactions/{id}/split` - Split transaction
- `DELETE /api/transactions/{id}` - Delete transaction
- `GET /api/transactions/categories` - Get categories
- `GET /api/reports/summary` - Get spending summary
- `GET /api/reports/chart/*` - Get chart data

## Environment Variables

Create a `.env` file for local development:

```
VITE_API_URL=http://localhost:8000/api
```

In Docker, the API URL is set to `http://backend:8000/api`

## Docker

### Build Image

```bash
docker build -t mintly-frontend .
```

### Run Container

```bash
docker run -p 3000:3000 mintly-frontend
```

### With Docker Compose

```bash
cd ..
docker-compose up
```

## Components

### Upload
- File input with validation
- Progress indicator
- Bank format guide
- Auto-redirect after success

### Transactions
- Table view of all transactions
- Inline category editing
- Split transaction modal
- Delete confirmation
- Real-time updates

### Reports
- Date range picker
- Summary cards (income, expenses, balance)
- Pie chart - spending by category
- Bar chart - category breakdown
- Responsive charts with Recharts

### SplitModal
- Add/remove split entries
- Amount validation
- Category selection
- Notes field

## Styling

Custom CSS with CSS variables for theming:

- Primary color: `#4ECDC4`
- Secondary color: `#FF6B6B`
- Dark color: `#2C3E50`
- Responsive grid layouts
- Mobile-friendly design

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

When adding new features:

1. Create component in `src/components/`
2. Add API calls to `src/services/api.js`
3. Update routing in `App.jsx`
4. Add styles to component or `App.css`

## License

MIT

