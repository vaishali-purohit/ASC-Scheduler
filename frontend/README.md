# Frontend Setup Guide

## Prerequisites

- Node.js 16 or higher
- npm or yarn package manager

## Installation Steps

### 1. Install Dependencies

```bash
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

Or use the provided script:

```bash
./start_frontend.sh
```

## Verification

Once the server is running:

- Open the printed URL (usually http://127.0.0.1:5173/) -> should see "ASC Scheduler"
- The page should load without errors

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/     # Reusable UI components
│   │   └── PassScheduleTable.tsx
│   ├── pages/          # Page components
│   │   └── Dashboard.tsx
│   ├── App.tsx         # Main app component
│   └── main.tsx        # Application entry point
├── package.json        # Dependencies and scripts
└── README.md           # This file
```

## Backend Integration

The frontend connects to the backend API running on:

- Development: `http://127.0.0.1:8000`
- Update API base URL in your API service files if needed

## Technologies Used

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client for API calls
- **Lucide React** - Icon library

## Development

### Adding New Components

Create new components in `src/components/` directory.

### API Integration

Create API service files in `src/` directory (or `src/api/` if you create it) to handle backend communication.

Example structure:

```typescript
// src/services/api.ts
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

export const getSatellites = async () => {
  const response = await axios.get(`${API_BASE_URL}/satellites`);
  return response.data;
};
```
